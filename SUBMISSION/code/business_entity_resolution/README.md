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

pip install -r code/business_entity_resolution/requirements.txt

# 2. Ensure dataset is at the expected path:
#    ../Data/6ab10eb3b23ba_student_resource/student_resource/dataset/
#      ├── train/  (train_source1.tsv, train_source2.tsv, train_source3.tsv, train_ground_truth.tsv)
#      └── test/   (test_source1.tsv, test_source2.tsv, test_source3.tsv)

# 3. Run the full pipeline
python code/business_entity_resolution/src/main.py

# 4. Outputs will be written to:
#    output/matching_results.tsv   (scored on leaderboard)
#    output/candidate_pairs.tsv    (blocking audit)
```

---

## Pipeline Overview

[TODO — fill in as the pipeline is built]

1. **Preprocessing** — [TODO]
2. **Blocking / Candidate Generation** — [TODO]
3. **Feature Engineering** — [TODO]
4. **Matching Model** — [TODO]
5. **Post-processing** — [TODO]

---

## Source Code Structure

```
code/business_entity_resolution/
├── src/
│   ├── main.py              [TODO — entry point]
│   └── ...                  [TODO — modules]
├── README.md                (this file)
└── requirements.txt         (pinned dependencies)
```

---

## Important Notes

- All data files are **tab-separated** (`.tsv`) — always use `sep='\t'`
- Model must be ≤ **8 billion parameters**
- Only **MIT or Apache 2.0 licensed** models/libraries
- **No external data** or APIs allowed (geocoding, business registries, etc.)
- `output/matching_results.tsv` must have exactly **1,732,545 rows** (one per S1 test entity)

---

## Validation

Before submitting, always validate:

```bash
python ../Data/6ab10eb3b23ba_student_resource/student_resource/utils/validate_submission.py \
    --matching output/matching_results.tsv \
    --candidate output/candidate_pairs.tsv \
    --test-dir ../Data/6ab10eb3b23ba_student_resource/student_resource/dataset/test
```

Must print `PASS` (exit 0).
