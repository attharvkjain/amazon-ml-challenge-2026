"""
Data ingestion — load TSVs and create train/val split.

Split strategy:
  - 80/20 stratified split on S1 entities by country
  - Matched S2/S3 follow their S1 into train or val
  - Unmatched S2/S3 (distractors) are split proportionally
  - SAMPLE_FRAC < 1.0 samples S1 first, then carries matched S2/S3
"""
from __future__ import annotations

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from tqdm import tqdm

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    TRAIN_DIR, TEST_DIR, RANDOM_STATE, SAMPLE_FRAC, VAL_FRAC,
)


def _read_tsv(path: str | os.PathLike) -> pd.DataFrame:
    """Read a tab-separated file."""
    df = pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)
    return df


def _parse_ground_truth(gt_df: pd.DataFrame) -> dict[str, set[str]]:
    """Parse ground truth TSV → {s1_id: set of matched s2/s3 ids}."""
    gt = {}
    # Optimized: zip is 1000x faster than iterrows
    for s1_id, matched in zip(gt_df["source1_entity_id"], gt_df["matched_entity_ids"]):
        if pd.notna(matched) and str(matched).strip():
            gt[str(s1_id)] = set(str(matched).split(","))
        else:
            gt[str(s1_id)] = set()
    return gt


def _build_reverse_map(gt: dict[str, set[str]]) -> dict[str, str]:
    """Build reverse map: {s2s3_id → s1_id} for all matched records."""
    rev = {}
    for s1_id, matched_ids in gt.items():
        for mid in matched_ids:
            rev[mid] = s1_id
    return rev


def load_train_data(
    sample_frac: float | None = None,
    val_frac: float | None = None,
    loco_country: str | None = None,
) -> dict:
    """
    Load training data and create train/val split.

    Returns dict with keys:
        train_s1, train_s2, train_s3, train_gt (dict),
        val_s1, val_s2, val_s3, val_gt (dict),
        full_gt (dict — all ground truth before split)
    """
    if sample_frac is None:
        sample_frac = SAMPLE_FRAC
    if val_frac is None:
        val_frac = VAL_FRAC

    print(f"[load] Reading training TSVs from {TRAIN_DIR} ...")
    s1 = _read_tsv(TRAIN_DIR / "train_source1.tsv")
    s2 = _read_tsv(TRAIN_DIR / "train_source2.tsv")
    s3 = _read_tsv(TRAIN_DIR / "train_source3.tsv")
    gt_raw = _read_tsv(TRAIN_DIR / "train_ground_truth.tsv")
    print(f"[load] S1={len(s1):,}, S2={len(s2):,}, S3={len(s3):,}, GT={len(gt_raw):,}")

    # Parse ground truth
    gt = _parse_ground_truth(gt_raw)

    # ── Sampling (for fast dev) ────────────────────────────────────────────
    if sample_frac < 1.0:
        print(f"[load] Sampling {sample_frac*100:.0f}% of S1 entities ...")
        s1_sampled = s1.sample(frac=sample_frac, random_state=RANDOM_STATE)
        s1_ids_sampled = set(s1_sampled["entity_id"])

        # Keep only GT entries for sampled S1
        gt = {k: v for k, v in gt.items() if k in s1_ids_sampled}

        # Build reverse map for sampled GT
        rev = _build_reverse_map(gt)

        # Keep matched S2/S3 + proportional distractors
        matched_s2_ids = {mid for mid in rev if mid.startswith("S2-")}
        matched_s3_ids = {mid for mid in rev if mid.startswith("S3-")}

        s2_matched = s2[s2["entity_id"].isin(matched_s2_ids)]
        s3_matched = s3[s3["entity_id"].isin(matched_s3_ids)]

        # Sample distractors proportionally
        s2_unmatched = s2[~s2["entity_id"].isin(matched_s2_ids)]
        s3_unmatched = s3[~s3["entity_id"].isin(matched_s3_ids)]

        n_s2_dist = int(len(s2_unmatched) * sample_frac)
        n_s3_dist = int(len(s3_unmatched) * sample_frac)

        s2_dist_sample = s2_unmatched.sample(n=min(n_s2_dist, len(s2_unmatched)),
                                              random_state=RANDOM_STATE)
        s3_dist_sample = s3_unmatched.sample(n=min(n_s3_dist, len(s3_unmatched)),
                                              random_state=RANDOM_STATE)

        s1 = s1_sampled
        s2 = pd.concat([s2_matched, s2_dist_sample], ignore_index=True)
        s3 = pd.concat([s3_matched, s3_dist_sample], ignore_index=True)

        print(f"[load] After sampling: S1={len(s1):,}, S2={len(s2):,}, S3={len(s3):,}")

    # ── Train / Val split (stratified by country on S1) ────────────────────
    print(f"[load] Creating {1-val_frac:.0%}/{val_frac:.0%} train/val split ...")

    if val_frac == 0.0:
        print(f"[load] val_frac=0.0, returning all data as training data ...")
        return {
            "train_s1": s1.reset_index(drop=True),
            "train_s2": s2.reset_index(drop=True),
            "train_s3": s3.reset_index(drop=True),
            "train_gt": gt,
            "val_s1": pd.DataFrame(columns=s1.columns),
            "val_s2": pd.DataFrame(columns=s2.columns),
            "val_s3": pd.DataFrame(columns=s3.columns),
            "val_gt": {},
            "full_gt": gt,
        }

    if loco_country:
        print(f"[load] LOCO Mode: Using '{loco_country}' as validation, all other countries as train ...")
        val_s1 = s1[s1['country'] == loco_country]
        train_s1 = s1[s1['country'] != loco_country]
    else:
        # Stratified split on S1 by country
        train_s1, val_s1 = train_test_split(
            s1,
            test_size=val_frac,
            stratify=s1["country"],
            random_state=RANDOM_STATE,
        )
    train_s1_ids = set(train_s1["entity_id"])
    val_s1_ids = set(val_s1["entity_id"])

    # Split ground truth
    train_gt = {k: v for k, v in gt.items() if k in train_s1_ids}
    val_gt = {k: v for k, v in gt.items() if k in val_s1_ids}

    # Build reverse maps
    train_rev = _build_reverse_map(train_gt)
    val_rev = _build_reverse_map(val_gt)

    # Split S2/S3: matched records follow their S1
    train_matched_ids = set(train_rev.keys())
    val_matched_ids = set(val_rev.keys())
    all_matched_ids = train_matched_ids | val_matched_ids

    s2_train_matched = s2[s2["entity_id"].isin(train_matched_ids)]
    s2_val_matched = s2[s2["entity_id"].isin(val_matched_ids)]
    s3_train_matched = s3[s3["entity_id"].isin(train_matched_ids)]
    s3_val_matched = s3[s3["entity_id"].isin(val_matched_ids)]

    # Distractors: split proportionally
    s2_distractors = s2[~s2["entity_id"].isin(all_matched_ids)]
    s3_distractors = s3[~s3["entity_id"].isin(all_matched_ids)]

    if loco_country:
        s2_dist_val = s2_distractors[s2_distractors['country'] == loco_country]
        s2_dist_train = s2_distractors[s2_distractors['country'] != loco_country]
        s3_dist_val = s3_distractors[s3_distractors['country'] == loco_country]
        s3_dist_train = s3_distractors[s3_distractors['country'] != loco_country]
    else:
        s2_dist_train, s2_dist_val = train_test_split(
            s2_distractors,
            test_size=val_frac,
            random_state=RANDOM_STATE,
        )
        s3_dist_train, s3_dist_val = train_test_split(
            s3_distractors,
            test_size=val_frac,
            random_state=RANDOM_STATE,
        )

    train_s2 = pd.concat([s2_train_matched, s2_dist_train], ignore_index=True)
    val_s2 = pd.concat([s2_val_matched, s2_dist_val], ignore_index=True)
    train_s3 = pd.concat([s3_train_matched, s3_dist_train], ignore_index=True)
    val_s3 = pd.concat([s3_val_matched, s3_dist_val], ignore_index=True)

    print(f"[load] Train: S1={len(train_s1):,}, S2={len(train_s2):,}, S3={len(train_s3):,}")
    print(f"[load] Val:   S1={len(val_s1):,}, S2={len(val_s2):,}, S3={len(val_s3):,}")
    print(f"[load] Train GT entries: {len(train_gt):,}, Val GT entries: {len(val_gt):,}")

    return {
        "train_s1": train_s1.reset_index(drop=True),
        "train_s2": train_s2.reset_index(drop=True),
        "train_s3": train_s3.reset_index(drop=True),
        "train_gt": train_gt,
        "val_s1": val_s1.reset_index(drop=True),
        "val_s2": val_s2.reset_index(drop=True),
        "val_s3": val_s3.reset_index(drop=True),
        "val_gt": val_gt,
        "full_gt": gt,
    }


def load_test_data() -> dict:
    """
    Load test data (no ground truth).

    Returns dict with keys: test_s1, test_s2, test_s3
    """
    print(f"[load] Reading test TSVs from {TEST_DIR} ...")
    s1 = _read_tsv(TEST_DIR / "test_source1.tsv")
    s2 = _read_tsv(TEST_DIR / "test_source2.tsv")
    s3 = _read_tsv(TEST_DIR / "test_source3.tsv")
    print(f"[load] Test: S1={len(s1):,}, S2={len(s2):,}, S3={len(s3):,}")
    return {"test_s1": s1, "test_s2": s2, "test_s3": s3}
