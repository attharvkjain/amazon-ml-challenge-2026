"""
Blocking - country-first hard partition plus GPU Semantic Blocking candidate generation.
(PyTorch Chunked Optimized)
"""
from __future__ import annotations

import gc
import numpy as np
import pandas as pd
import multiprocessing

import torch
import joblib
from sentence_transformers import SentenceTransformer

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BLOCKING_TOP_K, OUTPUT_DIR


def _dense_top_k(query_embeddings: torch.Tensor, index_embeddings: torch.Tensor, top_k: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Batched dense matrix top-K search on GPU.
    Uses chunked exact cosine similarity (dot product of normalized vectors).
    Returns fully vectorized arrays: (q_idx, s1_idx, scores)
    """
    chunk_size = 256  # Small chunk size for 8GB VRAM with 700k records
    n_queries = query_embeddings.shape[0]
    
    q_idx_list, s1_idx_list, scores_list = [], [], []
    
    # Process queries in chunks
    for start in range(0, n_queries, chunk_size):
        end = min(start + chunk_size, n_queries)
        chunk = query_embeddings[start:end].to(index_embeddings.device)
        
        # Exact cosine similarity (assuming normalized vectors)
        sim_matrix = torch.matmul(chunk, index_embeddings.T)
        
        # Get Top-K
        k = min(top_k, sim_matrix.shape[1])
        top_scores, top_indices = torch.topk(sim_matrix, k, dim=1)
        
        # Move to CPU to free VRAM for next operations
        top_scores = top_scores.cpu().numpy()
        top_indices = top_indices.cpu().numpy()
        
        # Vectorized array construction
        q_idxs = np.arange(start, end).reshape(-1, 1).repeat(k, axis=1)
        
        q_idx_list.append(q_idxs.flatten())
        s1_idx_list.append(top_indices.flatten())
        scores_list.append(top_scores.flatten())
            
    return np.concatenate(q_idx_list), np.concatenate(s1_idx_list), np.concatenate(scores_list)


def generate_candidates(
    s1: pd.DataFrame,
    s2: pd.DataFrame,
    s3: pd.DataFrame,
    top_k: int | None = None,
    save_path: str | os.PathLike | None = None,
    target_country: str | None = None,
    cache_prefix: str = 'train',
) -> pd.DataFrame:
    """Generate candidate pairs using country-first partitioning + Semantic GPU blocking."""
    if top_k is None:
        top_k = BLOCKING_TOP_K

    if target_country:
        countries = [target_country]
    else:
        countries = sorted(s1['country'].unique())
        
    print(f"[blocker] Countries: {countries}")
    all_pairs_dfs = []
    
    # ── Inter-stage Caching ──
    blocker_cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'cache')
    os.makedirs(blocker_cache_dir, exist_ok=True)

    print("  Loading MiniLM-L12-v2 to GPU ...")
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2', device=device)

    for country in countries:
        print(f"\n[blocker] Processing country: {country}")
        country_cache_path = os.path.join(blocker_cache_dir, f'blocker_cache_{cache_prefix}_{country}.pkl')
        if os.path.exists(country_cache_path):
            print(f"  [cache] Loading {country} candidates from cache...")
            cached_dfs = joblib.load(country_cache_path)
            all_pairs_dfs.extend(cached_dfs)
            continue
            
        s1_c = s1[s1['country'] == country].reset_index(drop=True)
        s2_c = s2[s2['country'] == country].reset_index(drop=True)
        s3_c = s3[s3['country'] == country].reset_index(drop=True)

        print(f"  S1: {len(s1_c):,}, S2: {len(s2_c):,}, S3: {len(s3_c):,}")

        if len(s1_c) == 0:
            continue
        
        country_dfs = []

        print(f"  Encoding S1 ...")
        s1_texts = s1_c['name_address'].fillna('').tolist()
        s1_embeddings = model.encode(s1_texts, batch_size=1024, convert_to_tensor=True, normalize_embeddings=True, device=device, show_progress_bar=True)
        s1_ids = s1_c['entity_id'].values

        if len(s2_c) > 0:
            print(f"  Encoding and Blocking S2 ({len(s2_c):,} records) ...")
            s2_texts = s2_c['name_address'].fillna('').tolist()
            s2_embeddings = model.encode(s2_texts, batch_size=1024, convert_to_tensor=True, normalize_embeddings=True, device=device, show_progress_bar=True)
            # Move massive S2 embeddings to CPU to prevent VRAM paging (2.5GB)
            s2_embeddings = s2_embeddings.cpu()
            if device == 'cuda': torch.cuda.empty_cache()
            
            s2_results = _dense_top_k(s2_embeddings, s1_embeddings, top_k)
            s2_ids = s2_c['entity_id'].values

            q_idx_arr, s1_idx_arr, scores_arr = s2_results
            
            del s2_embeddings, s2_results
            if device == 'cuda': torch.cuda.empty_cache()
            
            s2_df = pd.DataFrame()
            s2_df['s1_id'] = s1_ids[s1_idx_arr]
            s2_df['s2s3_id'] = s2_ids[q_idx_arr]
            s2_df['source'] = pd.Categorical(['S2'] * len(s1_idx_arr))
            s2_df['country'] = pd.Categorical([country] * len(s1_idx_arr))
            s2_df['semantic_score'] = scores_arr
            del q_idx_arr, s1_idx_arr, scores_arr
            
            # Prune candidates to dramatically reduce candidate set size for final ranking
            s2_df = s2_df[s2_df['semantic_score'] >= 0.55].reset_index(drop=True)
            country_dfs.append(s2_df)
            gc.collect()

        if len(s3_c) > 0:
            print(f"  Encoding and Blocking S3 ({len(s3_c):,} records) ...")
            s3_texts = s3_c['name_address'].fillna('').tolist()
            s3_embeddings = model.encode(s3_texts, batch_size=1024, convert_to_tensor=True, normalize_embeddings=True, device=device, show_progress_bar=True)
            # Move massive S3 embeddings to CPU to prevent VRAM paging
            s3_embeddings = s3_embeddings.cpu()
            if device == 'cuda': torch.cuda.empty_cache()
            
            s3_results = _dense_top_k(s3_embeddings, s1_embeddings, top_k)
            s3_ids = s3_c['entity_id'].values

            q_idx_arr, s1_idx_arr, scores_arr = s3_results
            
            del s3_embeddings, s3_results
            if device == 'cuda': torch.cuda.empty_cache()
            
            s3_df = pd.DataFrame()
            s3_df['s1_id'] = s1_ids[s1_idx_arr]
            s3_df['s2s3_id'] = s3_ids[q_idx_arr]
            s3_df['source'] = pd.Categorical(['S3'] * len(s1_idx_arr))
            s3_df['country'] = pd.Categorical([country] * len(s1_idx_arr))
            s3_df['semantic_score'] = scores_arr
            del q_idx_arr, s1_idx_arr, scores_arr
            
            # Prune candidates to dramatically reduce candidate set size for final ranking
            s3_df = s3_df[s3_df['semantic_score'] >= 0.55].reset_index(drop=True)
            country_dfs.append(s3_df)
            gc.collect()

        del s1_embeddings
        if device == 'cuda': torch.cuda.empty_cache()
        gc.collect()

        print(f"  [cache] Saving {country} candidates to cache...")
        joblib.dump(country_dfs, country_cache_path)
        all_pairs_dfs.extend(country_dfs)

    pairs_df = pd.concat(all_pairs_dfs, ignore_index=True) if all_pairs_dfs else pd.DataFrame()
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
    # 1. Flatten ground truth into a DataFrame (extremely fast for ~3M pairs)
    gt_records = []
    for s1_id, matched_ids in ground_truth.items():
        for mid in matched_ids:
            gt_records.append((s1_id, mid))
    
    total_true = len(gt_records)
    if total_true == 0:
        return 0.0
        
    gt_df = pd.DataFrame(gt_records, columns=['s1_id', 's2s3_id'])
    
    # 2. Chunked vectorized merge (strictly bounds memory overhead to prevent Int64Vector OOM)
    chunk_size = 5_000_000
    found = 0
    pairs_subset = pairs_df[['s1_id', 's2s3_id']]
    
    for i in range(0, len(pairs_subset), chunk_size):
        chunk = pairs_subset.iloc[i:i+chunk_size]
        merged = chunk.merge(gt_df, on=['s1_id', 's2s3_id'], how='inner')
        found += len(merged)
    
    recall = found / total_true
    print(f"[blocker] Blocking recall: {found:,}/{total_true:,} = {recall:.4f}")
    return recall
