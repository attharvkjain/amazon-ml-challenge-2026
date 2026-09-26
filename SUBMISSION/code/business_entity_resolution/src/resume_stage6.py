import os
import json
import joblib
import time
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import SAMPLE_FRAC, THRESHOLD_PATH
from postprocessing.threshold import sweep_threshold

def resume():
    CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cache')
    sample_key = f"{SAMPLE_FRAC:g}"
    
    print("\n[resume] Loading val_pairs...")
    val_pairs_path = os.path.join(CACHE_DIR, f'val_pairs_{sample_key}.pkl')
    val_pairs, _ = joblib.load(val_pairs_path)
    
    print("[resume] Loading val_probs_reranked...")
    reranked_probs_path = os.path.join(CACHE_DIR, f'val_probs_reranked_{sample_key}.pkl')
    val_probs = joblib.load(reranked_probs_path)
    
    print("[resume] Loading train_data (for ground truth)...")
    train_data_path = os.path.join(CACHE_DIR, f'train_data_{sample_key}.pkl')
    data = joblib.load(train_data_path)
    val_gt = data['val_gt']
    val_s1_ids = set(data['val_s1']['entity_id'])
    
    # We also need matcher for model_cache
    print("[resume] Instantiating dummy matcher (already cached inside it)...")
    from models.matcher import EntityMatcher
    matcher = EntityMatcher()
    lgb_cache_path = os.path.join(CACHE_DIR, 'lgb_model.pkl')
    xgb_cache_path = os.path.join(CACHE_DIR, 'xgb_model.pkl')
    matcher.lgb_model = joblib.load(lgb_cache_path)
    matcher.xgb_model = joblib.load(xgb_cache_path)
    
    import gc
    gc.collect()
    
    print("\n" + "="*60)
    print("STAGE 6: Threshold tuning")
    print("="*60)
    
    print("\n[postprocessing] Applying business logic penalties...")
    from postprocessing.penalty import apply_number_penalty
    val_probs = apply_number_penalty(val_pairs, val_probs, data['val_s1'], data['val_s2'], data['val_s3'])
    
    t0 = time.time()
    best_threshold, best_f05 = sweep_threshold(
        val_pairs, val_probs, val_gt, all_s1_ids=val_s1_ids
    )
    print(f"\nThreshold tuning took {time.time() - t0:.1f} seconds")
    
    print("\n[cache] Saving model_cache...")
    model_cache_path = os.path.join(CACHE_DIR, f'model_cache_{sample_key}.pkl')
    joblib.dump({
        'matcher': matcher,
        'best_threshold': best_threshold,
        'best_f05': best_f05,
        'val_probs': val_probs,
        'val_s1_ids': val_s1_ids
    }, model_cache_path)
    
    with open(THRESHOLD_PATH, 'w', encoding='utf-8') as f:
        if isinstance(best_threshold, dict):
            json.dump(best_threshold, f)
        else:
            f.write(f"{best_threshold:.8f}\n")
            
    print("\n[resume] Successfully completed Stage 6!")

if __name__ == '__main__':
    resume()
