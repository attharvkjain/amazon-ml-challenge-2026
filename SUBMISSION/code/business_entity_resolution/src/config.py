import os
from pathlib import Path

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "Data" / "6ab10eb3b23ba_student_resource" / "student_resource" / "dataset"
TRAIN_DIR = DATA_DIR / "train"
TEST_DIR = DATA_DIR / "test"
OUTPUT_DIR = PROJECT_ROOT / "SUBMISSION" / "output"

# Ensure output dir exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Hyperparameters
RANDOM_STATE = 42
SAMPLE_FRAC = 1.0  # Set to 0.1 for local rapid development

# Blocking configs
BLOCKING_TOP_K = 30
TFIDF_NGRAM_RANGE = (3, 3)

# Model configs
LGBM_PARAMS = {
    'objective': 'binary',
    'metric': 'custom',
    'boosting_type': 'gbdt',
    'learning_rate': 0.05,
    'num_leaves': 31,
    'max_depth': -1,
    'n_estimators': 300,
    'random_state': RANDOM_STATE,
    'n_jobs': -1
}
