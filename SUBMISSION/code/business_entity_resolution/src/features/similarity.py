"""
Pairwise feature extraction for candidate pairs.
(Multithreading optimized)
"""
from __future__ import annotations

import re
import numpy as np
import pandas as pd
from rapidfuzz import fuzz
from rapidfuzz.distance import JaroWinkler
import multiprocessing
from joblib import Parallel, delayed

FEATURE_NAMES = [
    "jaro_winkler_name", "levenshtein_ratio_name",
    "token_sort_ratio_name", "token_set_ratio_name",
    "jaro_winkler_address", "levenshtein_ratio_address",
    "token_sort_ratio_address", "token_set_ratio_address",
    "token_overlap_name", "token_overlap_address",
    "name_length_ratio", "address_length_ratio",
    "shared_numeric_tokens", "source_indicator",
]

_NUM_RE = re.compile(r'\d+')


def _token_overlap_jaccard(s1: str, s2: str) -> float:
    tokens1 = set(s1.split()) if s1 else set()
    tokens2 = set(s2.split()) if s2 else set()
    if not tokens1 and not tokens2:
        return 1.0
    if not tokens1 or not tokens2:
        return 0.0
    return len(tokens1 & tokens2) / len(tokens1 | tokens2)

def _length_ratio(s1: str, s2: str) -> float:
    l1, l2 = len(s1), len(s2)
    if l1 == 0 and l2 == 0:
        return 1.0
    if l1 == 0 or l2 == 0:
        return 0.0
    return min(l1, l2) / max(l1, l2)

def _shared_numeric_tokens(s1: str, s2: str) -> int:
    nums1 = set(_NUM_RE.findall(s1)) if s1 else set()
    nums2 = set(_NUM_RE.findall(s2)) if s2 else set()
    return len(nums1 & nums2)


def compute_pair_features(name1: str, name2: str, addr1: str, addr2: str, source: str) -> list[float]:
    name1 = name1 or ""
    name2 = name2 or ""
    addr1 = addr1 or ""
    addr2 = addr2 or ""
    return [
        JaroWinkler.normalized_similarity(name1, name2),
        fuzz.ratio(name1, name2) / 100.0,
        fuzz.token_sort_ratio(name1, name2) / 100.0,
        fuzz.token_set_ratio(name1, name2) / 100.0,
        JaroWinkler.normalized_similarity(addr1, addr2),
        fuzz.ratio(addr1, addr2) / 100.0,
        fuzz.token_sort_ratio(addr1, addr2) / 100.0,
        fuzz.token_set_ratio(addr1, addr2) / 100.0,
        _token_overlap_jaccard(name1, name2),
        _token_overlap_jaccard(addr1, addr2),
        _length_ratio(name1, name2),
        _length_ratio(addr1, addr2),
        _shared_numeric_tokens(addr1, addr2),
        1.0 if source == "S3" else 0.0,
    ]


def _extract_chunk(chunk_df: pd.DataFrame, s1_lookup: dict, s2s3_lookup: dict) -> np.ndarray:
    """Process a chunk of pairs to extract features. Returns float32 numpy array for fast IPC."""
    features = []
    for row in chunk_df.itertuples(index=False):
        s1_data = s1_lookup.get(row.s1_id, ('', ''))
        s2s3_data = s2s3_lookup.get(row.s2s3_id, ('', ''))

        feat = compute_pair_features(
            s1_data[0], s2s3_data[0],
            s1_data[1], s2s3_data[1],
            row.source,
        )
        features.append(feat)
    return np.array(features, dtype=np.float32)


def extract_features(
    pairs_df: pd.DataFrame,
    s1_df: pd.DataFrame,
    s2_df: pd.DataFrame,
    s3_df: pd.DataFrame,
) -> np.ndarray:
    """Extract pairwise features for all candidate pairs using multithreading."""
    n_jobs = max(1, multiprocessing.cpu_count() - 2)
    print(f"[features] Extracting features for {len(pairs_df):,} pairs on {n_jobs} threads ...")

    s1_lookup = {}
    for row in s1_df.itertuples(index=False):
        s1_lookup[row.entity_id] = (getattr(row, 'clean_name', ''), getattr(row, 'clean_address', ''))

    s2s3_lookup = {}
    for row in s2_df.itertuples(index=False):
        s2s3_lookup[row.entity_id] = (getattr(row, 'clean_name', ''), getattr(row, 'clean_address', ''))
    for row in s3_df.itertuples(index=False):
        s2s3_lookup[row.entity_id] = (getattr(row, 'clean_name', ''), getattr(row, 'clean_address', ''))

    if len(pairs_df) == 0:
        return np.array([], dtype=np.float32)

    chunks = np.array_split(pairs_df, max(1, n_jobs * 4))
    
    # Using 'loky' backend for true multiprocessing. Pickling overhead is small
    # compared to the massive speedup of avoiding GIL and iterrows overhead.
    results_list = Parallel(n_jobs=n_jobs, backend='threading')(
        delayed(_extract_chunk)(chunk, s1_lookup, s2s3_lookup) for chunk in chunks
    )

    return np.vstack(results_list)


def generate_labels(pairs_df: pd.DataFrame, ground_truth: dict[str, set[str]]) -> np.ndarray:
    labels = []
    for row in pairs_df.itertuples(index=False):
        gt_set = ground_truth.get(row.s1_id, set())
        labels.append(1 if row.s2s3_id in gt_set else 0)

    labels = np.array(labels, dtype=np.int32)
    pos = labels.sum()
    neg = len(labels) - pos
    if pos > 0:
        print(f"[features] Labels: {pos:,} pos, {neg:,} neg (ratio 1:{neg/pos:.1f})")
    return labels
