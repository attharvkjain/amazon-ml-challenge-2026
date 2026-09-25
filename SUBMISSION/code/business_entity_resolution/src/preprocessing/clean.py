"""
Text cleaning — Unicode-safe punctuation stripping + legal suffix normalization.
(Multiprocessing optimized)
"""
from __future__ import annotations

import re
import numpy as np
import pandas as pd
import multiprocessing
from joblib import Parallel, delayed


_SUFFIX_RULES = [
    (re.compile(r'\b(?:pvt|pvt\.)\b', re.IGNORECASE | re.UNICODE), 'private'),
    (re.compile(r'\b(?:ltd|ltd\.)\b', re.IGNORECASE | re.UNICODE), 'limited'),
    (re.compile(r'\b(?:inc\.)\b', re.IGNORECASE | re.UNICODE), 'inc'),
    (re.compile(r'\b(?:co\.)\b', re.IGNORECASE | re.UNICODE), 'company'),
    (re.compile(r'\b(?:corp\.)\b', re.IGNORECASE | re.UNICODE), 'corp'),
    (re.compile(r'\b(?:assoc\.)\b', re.IGNORECASE | re.UNICODE), 'associates'),
    (re.compile(r'\b(?:intl\.)\b', re.IGNORECASE | re.UNICODE), 'international'),
]

_PUNCT_RE = re.compile(r'[^\w\s]', re.UNICODE)
_MULTI_SPACE_RE = re.compile(r'\s+')


def clean_text(text: str | float | None) -> str:
    if pd.isna(text) or text is None:
        return ""
    text = str(text).lower()

    for pattern, replacement in _SUFFIX_RULES:
        text = pattern.sub(replacement, text)

    text = _PUNCT_RE.sub(' ', text)
    text = _MULTI_SPACE_RE.sub(' ', text).strip()
    return text


def _apply_clean(chunk: pd.Series) -> pd.Series:
    return chunk.apply(clean_text)


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply text cleaning to business_name and business_address columns.
    Uses multiprocessing to saturate CPU.
    """
    df = df.copy()
    n_jobs = max(1, multiprocessing.cpu_count() - 2)

    if len(df) == 0:
        df['clean_name'] = ""
        df['clean_address'] = ""
        df['name_address'] = ""
        return df

    # Use 'loky' backend for CPU bound string manipulation
    chunks_name = np.array_split(df['business_name'], max(1, n_jobs * 4))
    print(f"[clean] Cleaning names with {n_jobs} cores ...")
    res_name = Parallel(n_jobs=n_jobs, backend='loky')(delayed(_apply_clean)(c) for c in chunks_name)
    df['clean_name'] = pd.concat(res_name)

    chunks_addr = np.array_split(df['business_address'], max(1, n_jobs * 4))
    print(f"[clean] Cleaning addresses with {n_jobs} cores ...")
    res_addr = Parallel(n_jobs=n_jobs, backend='loky')(delayed(_apply_clean)(c) for c in chunks_addr)
    df['clean_address'] = pd.concat(res_addr)

    df['name_address'] = df['clean_name'] + " " + df['clean_address']
    return df
