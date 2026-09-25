"""
Configuration — all paths, hyperparameters, and thresholds for the pipeline.
"""
import os
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
DATA_DIR = PROJECT_ROOT / "Data" / "6ab10eb3b23ba_student_resource" / "student_resource" / "dataset"
TRAIN_DIR = DATA_DIR / "train"
TEST_DIR = DATA_DIR / "test"
OUTPUT_DIR = PROJECT_ROOT / "SUBMISSION" / "output"
DIAGNOSTICS_DIR = PROJECT_ROOT / "notebooks" / "diagnostics"
VALIDATE_SCRIPT = (
    PROJECT_ROOT / "Data" / "6ab10eb3b23ba_student_resource"
    / "student_resource" / "utils" / "validate_submission.py"
)

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(DIAGNOSTICS_DIR, exist_ok=True)

# ── Development ────────────────────────────────────────────────────────────────
RANDOM_STATE = 42
SAMPLE_FRAC = 0.1          # Set to 1.0 for full run
VAL_FRAC = 0.2             # 80/20 train/val split on S1 entities

# ── Blocking ───────────────────────────────────────────────────────────────────
BLOCKING_TOP_K = 20
TFIDF_NGRAM_RANGE = (3, 3)
TFIDF_MAX_FEATURES = 100_000

# ── Model (LightGBM) ──────────────────────────────────────────────────────────
LGBM_PARAMS = {
    "objective": "binary",
    "metric": "binary_logloss",
    "boosting_type": "gbdt",
    "learning_rate": 0.05,
    "num_leaves": 63,
    "max_depth": -1,
    "n_estimators": 500,
    "scale_pos_weight": 1.0,   # Auto-set during training
    "random_state": RANDOM_STATE,
    "n_jobs": -1,
    "verbose": -1,
}

# ── Threshold ──────────────────────────────────────────────────────────────────
THRESHOLD_MIN = 0.3
THRESHOLD_MAX = 0.95
THRESHOLD_STEP = 0.01

# ── Validation ─────────────────────────────────────────────────────────────────
CV_FOLDS = 5
TEST_S1_COUNT = 1_732_544
