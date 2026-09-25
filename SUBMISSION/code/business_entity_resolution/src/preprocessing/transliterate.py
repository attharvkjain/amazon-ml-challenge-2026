"""
Multi-script transliteration — convert non-Latin S2/S3 text to Latin.
(Multiprocessing optimized)
"""
from __future__ import annotations

import unicodedata
import numpy as np
import pandas as pd
import multiprocessing
from joblib import Parallel, delayed

try:
    from indic_transliteration import sanscript
    from indic_transliteration.sanscript import transliterate as indic_translit
    _HAS_INDIC = True
except ImportError:
    _HAS_INDIC = False
    print("[transliterate] WARNING: indic-transliteration not installed.")


_SCRIPT_RANGES = [
    (0x0900, 0x097F, 'DEVANAGARI'),
    (0x0980, 0x09FF, 'BENGALI'),
    (0x0A00, 0x0A7F, 'GURMUKHI'),
    (0x0A80, 0x0AFF, 'GUJARATI'),
    (0x0B00, 0x0B7F, 'ORIYA'),
    (0x0B80, 0x0BFF, 'TAMIL'),
    (0x0C00, 0x0C7F, 'TELUGU'),
    (0x0C80, 0x0CFF, 'KANNADA'),
    (0x0D00, 0x0D7F, 'MALAYALAM'),
]

_SCHEME_MAP = {}
if _HAS_INDIC:
    _SCHEME_MAP = {
        'DEVANAGARI': sanscript.DEVANAGARI,
        'BENGALI': sanscript.BENGALI,
        'GURMUKHI': sanscript.GURMUKHI,
        'GUJARATI': sanscript.GUJARATI,
        'ORIYA': sanscript.ORIYA,
        'TAMIL': sanscript.TAMIL,
        'TELUGU': sanscript.TELUGU,
        'KANNADA': sanscript.KANNADA,
        'MALAYALAM': sanscript.MALAYALAM,
    }


def _detect_script(char: str) -> str | None:
    cp = ord(char)
    for start, end, name in _SCRIPT_RANGES:
        if start <= cp <= end:
            return name
    return None

def _normalize_french_accents(text: str) -> str:
    nfd = unicodedata.normalize('NFD', text)
    return ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')

def transliterate_text(text: str) -> str:
    if pd.isna(text) or not text:
        return text if pd.isna(text) else ""
    text = str(text)

    has_non_latin = any(ord(c) >= 0x0300 for c in text)
    if not has_non_latin:
        return text

    text = _normalize_french_accents(text)

    if not _HAS_INDIC:
        return text

    has_indic = any(_detect_script(c) is not None for c in text)
    if not has_indic:
        return text

    segments = []
    current_script = None
    current_chars = []

    for char in text:
        script = _detect_script(char)
        if script != current_script:
            if current_chars:
                segments.append((current_script, ''.join(current_chars)))
            current_script = script
            current_chars = [char]
        else:
            current_chars.append(char)
    if current_chars:
        segments.append((current_script, ''.join(current_chars)))

    result_parts = []
    for script, segment in segments:
        if script is not None and script in _SCHEME_MAP:
            try:
                transliterated = indic_translit(
                    segment, _SCHEME_MAP[script], sanscript.ITRANS,
                )
                result_parts.append(transliterated)
            except Exception:
                result_parts.append(segment)
        else:
            result_parts.append(segment)

    return ''.join(result_parts)


def _apply_translit(chunk: pd.Series) -> pd.Series:
    return chunk.apply(transliterate_text)


def apply_transliteration(df: pd.DataFrame, is_s1: bool = False) -> pd.DataFrame:
    """
    Apply transliteration to a dataframe using multiprocessing.
    """
    if is_s1:
        return df

    df = df.copy()
    n_jobs = max(1, multiprocessing.cpu_count() - 2)

    if len(df) == 0:
        return df

    chunks_name = np.array_split(df['clean_name'], max(1, n_jobs * 4))
    print(f"[transliterate] Transliterating names with {n_jobs} cores ...")
    res_name = Parallel(n_jobs=n_jobs, backend='loky')(delayed(_apply_translit)(c) for c in chunks_name)
    df['clean_name'] = pd.concat(res_name)

    chunks_addr = np.array_split(df['clean_address'], max(1, n_jobs * 4))
    print(f"[transliterate] Transliterating addresses with {n_jobs} cores ...")
    res_addr = Parallel(n_jobs=n_jobs, backend='loky')(delayed(_apply_translit)(c) for c in chunks_addr)
    df['clean_address'] = pd.concat(res_addr)

    df['name_address'] = df['clean_name'] + " " + df['clean_address']
    return df
