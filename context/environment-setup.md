> **Version:** v1.3 | **Last updated:** 2026-09-26 02:30 IST | **By:** Codex

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
pip install -r SUBMISSION/code/business_entity_resolution/requirements.txt

# 5. Data setup — download/unzip the student resource into `data/` (see canonical paths below)
# Expected path after setup:
#   data/6ab10eb3b23ba_student_resource/student_resource/dataset/train/
#   data/6ab10eb3b23ba_student_resource/student_resource/dataset/test/
```

---

## Per-Teammate Setup

### Kingapplefruit

| Field | Value |
|-------|-------|
| **OS** | Microsoft Windows 11 Pro |
| **Python version** | Python 3.10.9 |
| **GPU** | NVIDIA GeForce RTX 5060, 8151 MiB |
| **RAM** | 31.11 GB |
| **Disk (F:)** | Free 133.59 GB / Total 196.78 GB |
| **Key Packages** | numpy 2.2.6, pandas 2.3.3, RapidFuzz 3.14.5, scikit-learn 1.7.2, tqdm 4.70.1 |
| **Special notes** | Default Python environment has no `torch` installed initially. |

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

The dataset is **not committed to git**; `.gitignore` excludes the checked-out `data/` directory. Submission TSV handling is documented separately in `project.md`.

### Expected directory structure

```
data/6ab10eb3b23ba_student_resource/student_resource/
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
| v1.3 | 2026-09-26 | Codex | Corrected the remaining setup example to the active lowercase data directory. |
| v1.2 | 2026-09-26 | Codex | Corrected lowercase data paths and the packaged requirements installation path. |
| v1.1 | 2026-09-25 | Antigravity | Added exact environment specs for Kingapplefruit. |
| v1.0 | 2026-09-25 | Member 1 | Initial skeleton created |
