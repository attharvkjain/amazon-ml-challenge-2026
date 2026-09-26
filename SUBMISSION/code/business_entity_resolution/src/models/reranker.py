from __future__ import annotations
import numpy as np
import pandas as pd
import torch
from sentence_transformers import CrossEncoder

class TwoStageReranker:
    def __init__(self, model_name: str = 'cross-encoder/ms-marco-MiniLM-L-6-v2', 
                 lower_bound: float = 0.05, 
                 upper_bound: float = 0.95):
        """
        Stage 2 Reranker using a Cross-Encoder.
        Only re-evaluates pairs where the ML model probability is between [lower_bound, upper_bound].
        """
        self.model_name = model_name
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.model = None

    def _load_model(self):
        if self.model is None:
            print(f"[reranker] Loading CrossEncoder: {self.model_name}...")
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            self.model = CrossEncoder(self.model_name, device=device)

    def rerank(self, pairs_df: pd.DataFrame, 
               ml_probs: np.ndarray, 
               s1_df: pd.DataFrame, 
               s2_df: pd.DataFrame, 
               s3_df: pd.DataFrame,
               training_countries: list[str] | None = None) -> np.ndarray:
        """
        Takes the base ML probabilities and overrides them with the Cross-Encoder score
        ONLY for candidates that fall within the uncertainty bounds.
        Forces 100% reranking for any zero-shot country not in the training set.
        """
        if training_countries is None:
            training_countries = ['US', 'India']
            
        mask = (ml_probs >= self.lower_bound) & (ml_probs <= self.upper_bound)
        
        # NEW: Force 100% reranking for any zero-shot country not in the training set
        if 'country' in pairs_df.columns:
            zero_shot_mask = ~pairs_df['country'].isin(training_countries)
            if zero_shot_mask.any():
                zs_count = zero_shot_mask.sum()
                print(f"[reranker] 🚨 FORCING Transformer evaluation for {zs_count:,} ZERO-SHOT pairs.")
                mask = mask | zero_shot_mask
        
        num_to_rerank = mask.sum()
        print(f"\n[reranker] {num_to_rerank:,} / {len(ml_probs):,} pairs selected for Transformer Reranking.")
        
        if num_to_rerank == 0:
            return ml_probs.copy()
            
        self._load_model()
        
        # Build mapping dictionaries for fast O(1) text lookup
        print(f"[reranker] Building text lookup maps...")
        s1_map = {row.entity_id: str(row.clean_name) + " " + str(row.clean_address) for row in s1_df.itertuples()}
        s2_map = {row.entity_id: str(row.clean_name) + " " + str(row.clean_address) for row in s2_df.itertuples()}
        s3_map = {row.entity_id: str(row.clean_name) + " " + str(row.clean_address) for row in s3_df.itertuples()}
        s2s3_map = {**s2_map, **s3_map}
        
        # Extract pairs to rerank
        subset_df = pairs_df[mask]
        
        print(f"[reranker] Preparing {num_to_rerank:,} pairs for Cross-Encoder...")
        text_pairs = []
        for s1_id, s2s3_id in zip(subset_df['s1_id'], subset_df['s2s3_id']):
            text1 = s1_map.get(s1_id, "")
            text2 = s2s3_map.get(s2s3_id, "")
            text_pairs.append((text1, text2))
            
        print(f"[reranker] Running Cross-Encoder inference...")
        # CrossEncoder returns logits by default, we apply sigmoid to get [0, 1] probabilities
        scores = self.model.predict(text_pairs, batch_size=256, show_progress_bar=True)
        # Assuming ms-marco returns logits, we convert to probabilities
        probs = 1 / (1 + np.exp(-scores))
        
        # Update the probabilities
        new_probs = ml_probs.copy()
        new_probs[mask] = probs
        
        print(f"[reranker] Inference complete. ML probabilities updated.")
        return new_probs
