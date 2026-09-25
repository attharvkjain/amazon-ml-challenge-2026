"""
Blocking — Country-first hard partition + TF-IDF character n-gram candidate generation.
(Multithreading optimized)
"""
from __future__ import annotations

import gc
import numpy as np
import pandas as pd
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer
import multiprocessing
from joblib import Parallel, delayed

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BLOCKING_TOP_K, TFIDF_NGRAM_RANGE, TFIDF_MAX_FEATURES, OUTPUT_DIR


def _process_batch(start: int, end: int, query_matrix: sparse.csr_matrix, index_matrix: sparse.csr_matrix, top_k: int) -> list[list[tuple[int, float]]]:
    """Process a single batch of queries for top-K extraction."""
    batch = query_matrix[start:end]
    # Sparse dot product releases GIL
    sim_matrix = batch.dot(index_matrix.T)

    batch_results = []
    for i in range(sim_matrix.shape[0]):
        row_start = sim_matrix.indptr[i]
        row_end = sim_matrix.indptr[i+1]
        
        indices = sim_matrix.indices[row_start:row_end]
        data = sim_matrix.data[row_start:row_end]
        
        if len(data) == 0:
            batch_results.append([])
            continue
            
        if len(data) <= top_k:
            sorted_idx = np.argsort(-data)
            top_indices = indices[sorted_idx]
            top_data = data[sorted_idx]
        else:
            part_idx = np.argpartition(-data, top_k)[:top_k]
            sorted_subset_idx = np.argsort(-data[part_idx])
            sorted_idx = part_idx[sorted_subset_idx]
            top_indices = indices[sorted_idx]
            top_data = data[sorted_idx]
            
        pairs = [(int(idx), float(val)) for idx, val in zip(top_indices, top_data)]
        batch_results.append(pairs)
        
    return batch_results


def _sparse_top_k(query_matrix: sparse.csr_matrix,
                   index_matrix: sparse.csr_matrix,
                   top_k: int) -> list[list[tuple[int, float]]]:
    """
    Multithreaded batched sparse matrix top-K search.
    Uses 'threading' backend because scipy/numpy operations release the GIL.
    Dynamically computes batch_size to strictly limit memory allocation.
    """
    n_queries = query_matrix.shape[0]
    n_index = index_matrix.shape[0]
    
    # We want max possible non-zeros per batch to be ~50,000,000 (which takes ~200MB).
    # This prevents OOM on large countries like the US (3.1M index items)
    batch_size = max(1, 50_000_000 // n_index)
    
    n_jobs = max(1, multiprocessing.cpu_count() - 2)
    
    tasks = [(start, min(start + batch_size, n_queries)) for start in range(0, n_queries, batch_size)]
    
    print(f"  TF-IDF search on {n_jobs} threads ({len(tasks)} batches of size {batch_size}) ...")
    
    # Threading backend is safe and zero-copy since scipy sparse matrices are passed by reference
    results_list = Parallel(n_jobs=n_jobs, backend='threading')(
        delayed(_process_batch)(s, e, query_matrix, index_matrix, top_k) for s, e in tasks
    )

    # Flatten results
    results = []
    for r in results_list:
        results.extend(r)
    return results


def generate_candidates(
    s1: pd.DataFrame,
    s2: pd.DataFrame,
    s3: pd.DataFrame,
    top_k: int | None = None,
    save_path: str | os.PathLike | None = None,
) -> pd.DataFrame:
    """Generate candidate pairs using country-first partitioning + TF-IDF blocking."""
    if top_k is None:
        top_k = BLOCKING_TOP_K

    countries = sorted(s1['country'].unique())
    print(f"[blocker] Countries: {countries}")
    all_pairs = []

    for country in countries:
        print(f"\n[blocker] Processing country: {country}")
        s1_c = s1[s1['country'] == country].reset_index(drop=True)
        s2_c = s2[s2['country'] == country].reset_index(drop=True)
        s3_c = s3[s3['country'] == country].reset_index(drop=True)

        print(f"  S1: {len(s1_c):,}, S2: {len(s2_c):,}, S3: {len(s3_c):,}")

        if len(s1_c) == 0:
            continue

        print(f"  Fitting TF-IDF vectorizer ...")
        vectorizer = TfidfVectorizer(
            analyzer='char_wb',
            ngram_range=TFIDF_NGRAM_RANGE,
            max_features=TFIDF_MAX_FEATURES,
            max_df=0.25,
            sublinear_tf=True,
            dtype=np.float32,
        )

        s1_texts = s1_c['name_address'].fillna('').tolist()
        s1_tfidf = vectorizer.fit_transform(s1_texts)
        s1_ids = s1_c['entity_id'].tolist()

        if len(s2_c) > 0:
            print(f"  Blocking S2 ({len(s2_c):,} records) ...")
            s2_texts = s2_c['name_address'].fillna('').tolist()
            s2_tfidf = vectorizer.transform(s2_texts)
            s2_results = _sparse_top_k(s2_tfidf, s1_tfidf, top_k)
            s2_ids = s2_c['entity_id'].tolist()

            for q_idx, matches in enumerate(s2_results):
                for s1_idx, score in matches:
                    all_pairs.append({
                        's1_id': s1_ids[s1_idx],
                        's2s3_id': s2_ids[q_idx],
                        'source': 'S2',
                        'country': country,
                        'tfidf_score': score,
                    })
            del s2_tfidf, s2_results
            gc.collect()

        if len(s3_c) > 0:
            print(f"  Blocking S3 ({len(s3_c):,} records) ...")
            s3_texts = s3_c['name_address'].fillna('').tolist()
            s3_tfidf = vectorizer.transform(s3_texts)
            s3_results = _sparse_top_k(s3_tfidf, s1_tfidf, top_k)
            s3_ids = s3_c['entity_id'].tolist()

            for q_idx, matches in enumerate(s3_results):
                for s1_idx, score in matches:
                    all_pairs.append({
                        's1_id': s1_ids[s1_idx],
                        's2s3_id': s3_ids[q_idx],
                        'source': 'S3',
                        'country': country,
                        'tfidf_score': score,
                    })
            del s3_tfidf, s3_results
            gc.collect()

        del s1_tfidf, vectorizer
        gc.collect()

    pairs_df = pd.DataFrame(all_pairs)
    print(f"\n[blocker] Total candidate pairs: {len(pairs_df):,}")

    if save_path is not None:
        _save_candidate_pairs(pairs_df, s1, save_path)

    return pairs_df


def _save_candidate_pairs(pairs_df: pd.DataFrame, s1: pd.DataFrame, save_path: str | os.PathLike) -> None:
    grouped = pairs_df.groupby('s1_id')['s2s3_id'].apply(lambda x: ','.join(sorted(set(x)))).reset_index()
    grouped.columns = ['source1_entity_id', 'candidate_entity_ids']
    all_s1 = pd.DataFrame({'source1_entity_id': s1['entity_id'].unique()})
    result = all_s1.merge(grouped, on='source1_entity_id', how='left')
    result['candidate_entity_ids'] = result['candidate_entity_ids'].fillna('')
    result.to_csv(save_path, sep='\t', index=False)
    print(f"[blocker] Saved candidate_pairs.tsv: {len(result):,} rows → {save_path}")


def compute_blocking_recall(pairs_df: pd.DataFrame, ground_truth: dict[str, set[str]]) -> float:
    candidate_set = set(zip(pairs_df['s1_id'], pairs_df['s2s3_id']))
    total_true = 0
    found = 0
    for s1_id, matched_ids in ground_truth.items():
        for mid in matched_ids:
            total_true += 1
            if (s1_id, mid) in candidate_set:
                found += 1
    recall = found / total_true if total_true > 0 else 0.0
    print(f"[blocker] Blocking recall: {found:,}/{total_true:,} = {recall:.4f}")
    return recall
