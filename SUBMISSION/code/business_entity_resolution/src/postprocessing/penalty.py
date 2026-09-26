import re
import pandas as pd
import numpy as np
from tqdm import tqdm

def apply_number_penalty(pairs_df: pd.DataFrame, probs: np.ndarray, s1_df: pd.DataFrame, s2_df: pd.DataFrame, s3_df: pd.DataFrame) -> np.ndarray:
    """
    Applies a mathematical 0.1x penalty to probabilities where the building/house
    number fundamentally conflicts between the two addresses.
    """
    print(f"\n[penalty] Applying first-number post-processing penalty to {len(pairs_df):,} pairs...")
    
    # 1. Build fast address lookups
    s1_lookup = s1_df.set_index('entity_id')['clean_address'].to_dict()
    
    s2s3_df = pd.concat([s2_df[['entity_id', 'clean_address']], s3_df[['entity_id', 'clean_address']]])
    s2s3_lookup = s2s3_df.set_index('entity_id')['clean_address'].to_dict()
    
    penalized_probs = probs.copy()
    num_re = re.compile(r'\b\d+\b')
    
    # 2. Iterate raw arrays for maximum speed
    s1_ids = pairs_df['s1_id'].values
    s2s3_ids = pairs_df['s2s3_id'].values
    
    penalized_count = 0
    
    for i in tqdm(range(len(s1_ids)), desc="Applying Penalty", leave=False):
        a1 = s1_lookup.get(s1_ids[i], "")
        a2 = s2s3_lookup.get(s2s3_ids[i], "")
        
        m1 = num_re.search(a1)
        m2 = num_re.search(a2)
        
        if m1 and m2:
            f1 = m1.group(0)
            f2 = m2.group(0)
            
            n1 = set(num_re.findall(a1))
            n2 = set(num_re.findall(a2))
            
            # If the first number of A1 is nowhere in A2, and vice versa = CONFLICT
            if f1 not in n2 and f2 not in n1:
                penalized_probs[i] *= 0.1
                penalized_count += 1
                
    print(f"[penalty] Penalized {penalized_count:,} structurally conflicting pairs.")
    return penalized_probs
