> **Version:** v1.0 | **Last updated:** 2026-09-26 02:07 IST | **By:** Codex

# Business Entity Resolution — Reproduction Guide

> This README ships inside the final submission zip. It tells reviewers how to reproduce our results end-to-end.

---

## Quick Start

```bash
# 1. Set up environment (from repo root)
python -m venv .venv

# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Linux/macOS:
# source .venv/bin/activate

pip install -r SUBMISSION/code/business_entity_resolution/requirements.txt

# 2. Ensure dataset is at the expected path:
#    data/6ab10eb3b23ba_student_resource/student_resource/dataset/
#      ├── train/  (train_source1.tsv, train_source2.tsv, train_source3.tsv, train_ground_truth.tsv)
#      └── test/   (test_source1.tsv, test_source2.tsv, test_source3.tsv)

# 3. Run the full pipeline
python SUBMISSION/code/business_entity_resolution/src/main.py --mode train

# 4. Outputs will be written to:
#    SUBMISSION/output/matching_results.tsv   (scored on leaderboard)
#    SUBMISSION/output/candidate_pairs.tsv    (local blocking audit)
```

---

## Pipeline Overview

The pipeline reads TSV records, cleans and transliterates text, generates country-partitioned word-unigram TF-IDF candidates, extracts pairwise string features, trains a LightGBM matcher, tunes the threshold on validation data, and writes the leaderboard and audit outputs.

Training uses the full training set by default. Set `SAMPLE_FRAC` in `src/config.py` below `1.0` for a sampled development run.

---

## Source Code Structure

```
code/business_entity_resolution/
├── src/
│   ├── main.py              (train, predict, and CV entry point)
│   ├── config.py            (paths and run settings)
│   └── ...                  (preprocessing, blocking, features, model, evaluation)
├── README.md                (this file)
└── requirements.txt         (dependency list)
```

---

## Important Notes

- All data files are **tab-separated** (`.tsv`) — always use `sep='\t'`
- Model must be ≤ **8 billion parameters**
- Only **MIT or Apache 2.0 licensed** models/libraries
- **No external data** or APIs allowed (geocoding, business registries, etc.)
- `output/matching_results.tsv` must have one row per S1 test entity.
- Predict mode uses the tuned threshold saved by train mode in `output/model_threshold.txt`.

---

## Validation

Before submitting, always validate:

```bash
python data/6ab10eb3b23ba_student_resource/student_resource/utils/validate_submission.py \
    --matching SUBMISSION/output/matching_results.tsv \
    --candidate SUBMISSION/output/candidate_pairs.tsv \
    --test-dir data/6ab10eb3b23ba_student_resource/student_resource/dataset/test
```

Must print `PASS` (exit 0).

## Changelog

| Version | Date | By | Summary |
|---------|------|----|---------|
| v1.0 | 2026-09-26 | Codex | Replaced scaffold placeholders with implemented pipeline guidance and corrected repository-root paths and output-count reference. |
