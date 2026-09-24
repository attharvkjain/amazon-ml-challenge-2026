> **Version:** v1.0 | **Last updated:** 2026-09-25 02:30 IST | **By:** Member 1

# Environment Setup

**Standalone primer:** Amazon ML Challenge 2026 — Business Entity Resolution hackathon with a 4-person team. This file documents the exact steps to reproduce each teammate's local development environment so anyone (or any AI agent) can get running without re-deriving setup.

---

## Common Requirements

| Requirement | Value |
|-------------|-------|
| **Python** | 3.10+ |
| **Package manager** | pip (with `requirements.txt`) |
| **Core libraries** | pandas, numpy, scikit-learn, rapidfuzz, tqdm |
| **Data format** | Tab-separated `.tsv` — always use `sep='\t'` |

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/attharvkjain/amazon-ml-challenge-2026.git
cd amazon-ml-challenge-2026

# 2. Create virtual environment
python -m venv .venv

# 3. Activate
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# Linux/macOS:
source .venv/bin/activate

# 4. Install dependencies (when requirements.txt is available)
pip install -r requirements.txt

# 5. Data setup — download/unzip the student resource into Data/
# Expected path after setup:
#   Data/6ab10eb3b23ba_student_resource/student_resource/dataset/train/
#   Data/6ab10eb3b23ba_student_resource/student_resource/dataset/test/
```

---

## Per-Teammate Setup

### Member 1

| Field | Value |
|-------|-------|
| **OS** | TBD |
| **Python version** | TBD |
| **GPU** | TBD |
| **Special notes** | TBD |

### Member 2

| Field | Value |
|-------|-------|
| **OS** | TBD |
| **Python version** | TBD |
| **GPU** | TBD |
| **Special notes** | TBD |

### Member 3

| Field | Value |
|-------|-------|
| **OS** | TBD |
| **Python version** | TBD |
| **GPU** | TBD |
| **Special notes** | TBD |

### Member 4

| Field | Value |
|-------|-------|
| **OS** | TBD |
| **Python version** | TBD |
| **GPU** | TBD |
| **Special notes** | TBD |

---

## Data Setup

The dataset is **not committed to git** (`.gitignore` excludes `Data/` and `*.tsv`). Each teammate must have the data locally.

### Expected directory structure

```
Data/6ab10eb3b23ba_student_resource/student_resource/
├── dataset/
│   ├── train/
│   │   ├── train_source1.tsv      (Source 1 training — 2.2M records)
│   │   ├── train_source2.tsv      (Source 2 training — 5.0M records)
│   │   ├── train_source3.tsv      (Source 3 training — 5.3M records)
│   │   └── train_ground_truth.tsv (Ground truth labels)
│   └── test/
│       ├── test_source1.tsv       (Source 1 test — 1.7M records)
│       ├── test_source2.tsv       (Source 2 test — 4.9M records)
│       └── test_source3.tsv       (Source 3 test — 5.1M records)
├── utils/
│   └── validate_submission.py
├── Documentation_template.md
└── README.md
```

---

## OS-Specific Gotchas

- **Windows**: Use PowerShell; venv activation is `.\.venv\Scripts\Activate.ps1`
- **macOS/Linux**: Standard bash/zsh activation
- **File paths**: Use forward slashes in Python (`Path()` handles this), backslashes only in Windows shell commands
- **Line endings**: Configure git to handle line endings — `git config core.autocrlf true` on Windows

---

## Changelog

| Version | Date | By | Summary |
|---------|------|----|---------|
| v1.0 | 2026-09-25 | Member 1 | Initial skeleton created |
