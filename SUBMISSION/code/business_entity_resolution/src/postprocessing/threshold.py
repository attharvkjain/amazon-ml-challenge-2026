"""
Post-processing — threshold tuning, one-to-one constraint, output formatting.

Operations (from architecture.md §Stage 7):
  1. Threshold sweep on validation set to maximize F₀.₅
  2. One-to-one constraint: each S2/S3 → at most 1 S1
  3. Format output: matching_results.tsv (1,732,544 rows) + candidate_pairs.tsv
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from tqdm import tqdm

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    THRESHOLD_MIN, THRESHOLD_MAX, THRESHOLD_STEP, OUTPUT_DIR, TEST_S1_COUNT,
)


def sweep_threshold(
    pairs_df: pd.DataFrame,
    probabilities: np.ndarray,
    ground_truth: dict[str, set[str]],
    all_s1_ids: set[str] | None = None,
    threshold_range: tuple[float, float, float] | None = None,
) -> tuple[float, float]:
    """
    Sweep probability threshold to maximize F₀.₅ on validation set.

    Args:
        pairs_df: Candidate pairs DataFrame
        probabilities: Match probabilities from model
        ground_truth: {s1_id: set of true match ids}
        all_s1_ids: Set of all S1 entity IDs (for singleton handling)
        threshold_range: (min, max, step) for sweep

    Returns:
        (best_threshold, best_f05)
    """
    if threshold_range is None:
        threshold_range = (THRESHOLD_MIN, THRESHOLD_MAX, THRESHOLD_STEP)

    tmin, tmax, tstep = threshold_range
    thresholds = np.arange(tmin, tmax + tstep, tstep)

    if all_s1_ids is None:
        all_s1_ids = set(ground_truth.keys())

    best_threshold = 0.5
    best_f05 = 0.0

    print(f"[threshold] Sweeping {len(thresholds)} thresholds [{tmin:.2f}, {tmax:.2f}] ...")

    for t in thresholds:
        predictions = _apply_threshold_and_constraint(pairs_df, probabilities, t)
        f05 = _compute_f05_macro(predictions, ground_truth, all_s1_ids)
        if f05 > best_f05:
            best_f05 = f05
            best_threshold = t

    print(f"[threshold] Best threshold: {best_threshold:.3f} -> F0.5 = {best_f05:.4f}")
    return best_threshold, best_f05


def _apply_threshold_and_constraint(
    pairs_df: pd.DataFrame,
    probabilities: np.ndarray,
    threshold: float,
) -> dict[str, set[str]]:
    """
    Apply threshold + one-to-one constraint (each S2/S3 → at most 1 S1).

    Returns: {s1_id: set of matched s2s3 ids}
    """
    # Filter by threshold
    mask = probabilities >= threshold
    accepted = pairs_df[mask].copy()
    accepted['prob'] = probabilities[mask]

    if len(accepted) == 0:
        return {}

    # One-to-one constraint: each S2/S3 maps to at most 1 S1 (keep highest prob)
    accepted = accepted.sort_values('prob', ascending=False)
    accepted = accepted.drop_duplicates(subset='s2s3_id', keep='first')

    # Group by S1 using fast pandas groupby instead of iterrows
    if len(accepted) == 0:
        return {}
    
    # This is 100x faster than iterrows
    predictions = accepted.groupby('s1_id')['s2s3_id'].apply(set).to_dict()

    return predictions

def _compute_f05_macro(
    predictions: dict[str, set[str]],
    ground_truth: dict[str, set[str]],
    all_s1_ids: set[str],
) -> float:
    """Macro-averaged F₀.₅ across all S1 entities."""
    scores = []
    for s1_id in all_s1_ids:
        pred = predictions.get(s1_id, set())
        true = ground_truth.get(s1_id, set())
        scores.append(_f05_single(pred, true))
    return np.mean(scores) if scores else 0.0


def _f05_single(predicted: set, true: set) -> float:
    """F₀.₅ for a single S1 entity."""
    # Singleton: empty truth + empty prediction → 1.0
    if not true and not predicted:
        return 1.0
    # Singleton: empty truth + non-empty prediction → 0.0
    if not true and predicted:
        return 0.0
    # Non-singleton: empty prediction → 0.0
    if true and not predicted:
        return 0.0

    tp = len(predicted & true)
    fp = len(predicted - true)
    fn = len(true - predicted)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0

    if precision + recall == 0:
        return 0.0

    beta = 0.5
    f_beta = (1 + beta**2) * (precision * recall) / (beta**2 * precision + recall)
    return f_beta


def format_and_save_output(
    pairs_df: pd.DataFrame,
    probabilities: np.ndarray,
    threshold: float,
    all_s1_ids: list[str] | set[str] | pd.Series,
    output_dir: str | os.PathLike | None = None,
    append_mode: bool = False,
) -> pd.DataFrame:
    """
    Format and save final output files.

    Creates:
      - matching_results.tsv: Final matches (scored on leaderboard)
      - candidate_pairs.tsv: All candidates before threshold (audit)

    Returns:
        matching_results DataFrame
    """
    if output_dir is None:
        output_dir = OUTPUT_DIR

    # Apply threshold + constraint
    predictions = _apply_threshold_and_constraint(pairs_df, probabilities, threshold)

    # Build matching_results
    if isinstance(all_s1_ids, pd.Series):
        all_s1_list = all_s1_ids.tolist()
    elif isinstance(all_s1_ids, set):
        all_s1_list = sorted(all_s1_ids)
    else:
        all_s1_list = list(all_s1_ids)

    rows = []
    for s1_id in all_s1_list:
        matched = predictions.get(s1_id, set())
        matched_str = ','.join(sorted(matched)) if matched else ''
        rows.append({'source1_entity_id': s1_id, 'matched_entity_ids': matched_str})

    matching_df = pd.DataFrame(rows)

    # Save matching_results.tsv
    matching_path = os.path.join(output_dir, 'matching_results.tsv')
    write_mode = 'a' if append_mode else 'w'
    write_header = not append_mode
    matching_df.to_csv(matching_path, sep='\t', index=False, mode=write_mode, header=write_header)

    n_matched = sum(1 for _, r in matching_df.iterrows() if r['matched_entity_ids'])
    n_singleton = len(matching_df) - n_matched
    print(f"[output] matching_results.tsv: {len(matching_df):,} rows "
          f"({n_matched:,} matched, {n_singleton:,} singletons) -> {matching_path}")

    # Build and save candidate_pairs.tsv
    if len(pairs_df) > 0:
        cand_grouped = pairs_df.groupby('s1_id')['s2s3_id'].apply(
            lambda x: ','.join(sorted(set(x)))
        ).reset_index()
        cand_grouped.columns = ['source1_entity_id', 'candidate_entity_ids']

        all_s1_frame = pd.DataFrame({'source1_entity_id': all_s1_list})
        cand_result = all_s1_frame.merge(cand_grouped, on='source1_entity_id', how='left')
        cand_result['candidate_entity_ids'] = cand_result['candidate_entity_ids'].fillna('')
    else:
        # If no pairs at all, just output empty candidates
        cand_result = pd.DataFrame({'source1_entity_id': all_s1_list, 'candidate_entity_ids': ''})

    cand_path = os.path.join(output_dir, 'candidate_pairs.tsv')
    cand_result.to_csv(cand_path, sep='\t', index=False, mode=write_mode, header=write_header)
    print(f"[output] candidate_pairs.tsv: {len(cand_result):,} rows -> {cand_path}")

    return matching_df
