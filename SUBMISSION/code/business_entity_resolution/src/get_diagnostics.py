import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
import os
import joblib
import pandas as pd
import numpy as np

CACHE_DIR = r"F:\PROJECTS\AmazonMLChallenge_2026\SUBMISSION\code\business_entity_resolution\cache"
model_cache_path = os.path.join(CACHE_DIR, 'model_cache_1.pkl')
val_pairs_path = os.path.join(CACHE_DIR, 'val_pairs_1.pkl')
train_data_path = os.path.join(CACHE_DIR, 'train_data_1.pkl')

print("Loading data...")
model_data = joblib.load(model_cache_path)
best_threshold = model_data['best_threshold']
val_probs = model_data['val_probs']

val_pairs, _ = joblib.load(val_pairs_path)
data = joblib.load(train_data_path)
val_gt = data['val_gt']
val_s1_ids = set(data['val_s1']['entity_id'])

s1_lookup = data['val_s1'].set_index('entity_id')
s2_lookup = data['val_s2'].set_index('entity_id')
s3_lookup = data['val_s3'].set_index('entity_id')

print("Applying threshold...")
from collections import defaultdict
predictions = defaultdict(set)
t = best_threshold if not isinstance(best_threshold, dict) else best_threshold.get('US', 0.5)

sorted_df = val_pairs.copy()
sorted_df['prob'] = val_probs
sorted_df = sorted_df.sort_values('prob', ascending=False)
deduped_df = sorted_df.drop_duplicates(subset='s2s3_id', keep='first')

for country in ['US', 'India']:
    c_pairs = deduped_df[deduped_df['country'] == country]
    t = best_threshold.get(country, 0.5) if isinstance(best_threshold, dict) else best_threshold
    
    s1_ids = c_pairs['s1_id'].values
    s2s3_ids = c_pairs['s2s3_id'].values
    probs = c_pairs['prob'].values
    
    idx = np.searchsorted(-probs, -t, side='right')
    for i in range(idx):
        predictions[s1_ids[i]].add(s2s3_ids[i])

print("Finding False Positives & False Negatives...")
fp_records = []
fn_records = []

for s1 in val_s1_ids:
    p = predictions.get(s1, set())
    t = val_gt.get(s1, set())
    
    for fp in (p - t):
        fp_records.append({'s1_id': s1, 's2s3_id': fp})
        
    for fn in (t - p):
        fn_records.append({'s1_id': s1, 's2s3_id': fn})

print(f"Total False Positives: {len(fp_records)}")
print(f"Total False Negatives: {len(fn_records)}")

def get_row_str(row):
    return f"{row.get('business_name', 'N/A')} | {row.get('business_address', 'N/A')}"

print("\n--- TOP 10 FALSE POSITIVES ---")
# False Positives: we predicted a match, but it shouldn't be matched
for i, rec in enumerate(fp_records[:10]):
    s1 = rec['s1_id']
    s2s3 = rec['s2s3_id']
    s1_row = s1_lookup.loc[s1]
    s2s3_row = s2_lookup.loc[s2s3] if s2s3 in s2_lookup.index else s3_lookup.loc[s2s3]
    
    # Let's find the predicted probability
    mask = (val_pairs['s1_id'] == s1) & (val_pairs['s2s3_id'] == s2s3)
    if mask.any():
        prob = val_probs[mask.argmax()]
    else:
        prob = -1.0
        
    print(f"\nFP {i+1} (Prob: {prob:.3f}):")
    print(f"  S1 [{s1}]: {get_row_str(s1_row)}")
    print(f"  S2/S3 [{s2s3}]: {get_row_str(s2s3_row)}")

print("\n--- TOP 10 FALSE NEGATIVES ---")
# False Negatives: we missed a true match
for i, rec in enumerate(fn_records[:10]):
    s1 = rec['s1_id']
    s2s3 = rec['s2s3_id']
    s1_row = s1_lookup.loc[s1]
    if s2s3 in s2_lookup.index: s2s3_row = s2_lookup.loc[s2s3]
    elif s2s3 in s3_lookup.index: s2s3_row = s3_lookup.loc[s2s3]
    else: continue
    
    mask = (val_pairs['s1_id'] == s1) & (val_pairs['s2s3_id'] == s2s3)
    if mask.any():
        prob = val_probs[mask.argmax()]
    else:
        prob = -1.0 # Means blocking missed it entirely!
        
    print(f"\nFN {i+1} (Prob: {prob:.3f}):")
    print(f"  S1 [{s1}]: {get_row_str(s1_row)}")
    print(f"  S2/S3 [{s2s3}]: {get_row_str(s2s3_row)}")
