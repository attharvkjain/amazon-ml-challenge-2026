import os
import sys
import time
import pandas as pd
import numpy as np
import joblib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import SAMPLE_FRAC
from postprocessing.threshold import sweep_threshold

def evaluate_stage1():
    CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cache')
    sample_key = f"{SAMPLE_FRAC:g}"
    
    print("\n[eval] Loading models...")
    from models.matcher import EntityMatcher
    matcher = EntityMatcher()
    matcher.lgb_model = joblib.load(os.path.join(CACHE_DIR, 'lgb_model.pkl'))
    matcher.xgb_model = joblib.load(os.path.join(CACHE_DIR, 'xgb_model.pkl'))
    
    print("[eval] Loading val_feat (mmap)...")
    val_feat_path = os.path.join(CACHE_DIR, f'val_feat_{sample_key}.pkl')
    X_val, y_val = joblib.load(val_feat_path)
    
    print("[eval] Loading val_pairs...")
    val_pairs_path = os.path.join(CACHE_DIR, f'val_pairs_{sample_key}.pkl')
    val_pairs, _ = joblib.load(val_pairs_path)
    
    print("[eval] Generating Stage 1 Probabilities...")
    t0 = time.time()
    val_probs = matcher.predict_proba(X_val)
    print(f"  Took {time.time() - t0:.1f}s")
    
    # Free memory
    del X_val
    import gc
    gc.collect()
    
    print("[eval] Loading train_data (for ground truth)...")
    train_data_path = os.path.join(CACHE_DIR, f'train_data_{sample_key}.pkl')
    data = joblib.load(train_data_path)
    val_gt = data['val_gt']
    val_s1_ids = set(data['val_s1']['entity_id'])
    del data
    gc.collect()
    
    print("\n" + "="*60)
    print("STAGE 6: Threshold tuning (Stage 1 Ensemble ONLY)")
    print("="*60)
    
    t0 = time.time()
    best_threshold, best_f05 = sweep_threshold(
        val_pairs, val_probs, val_gt, all_s1_ids=val_s1_ids
    )
    print(f"\nThreshold tuning took {time.time() - t0:.1f} seconds")
    
    print(f"\n[eval] Final Stage 1 ONLY Validation F0.5: {best_f05:.4f}")

if __name__ == "__main__":
    evaluate_stage1()
