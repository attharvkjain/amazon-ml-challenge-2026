> **Version:** v1.0 | **Last updated:** 2026-09-25 02:30 IST | **By:** Member 1

# Problem Statement & Data

**Standalone primer:** Amazon ML Challenge 2026 is a 72-hour hackathon (Sep 25–27, 2026) focused on Business Entity Resolution — matching noisy business records across 3 independent data sources to identify which records refer to the same real-world entity. This file covers the problem statement, dataset schema, evaluation metric, output format, constraints, and known data quirks.

> For the full deep-dive analysis, see [`Analysis and Research/amazon_ml_challenge_2026_analysis.md`](../Analysis%20and%20Research/amazon_ml_challenge_2026_analysis.md).

---

## Problem Statement

Given business records from **3 independent sources**, determine which records across sources refer to the **same real-world business entity**.

- **Source 1** is the deduplicated reference. You match S2 and S3 records *to* S1 entities.
- Each S1 entity may match **zero** (singleton), **one**, or **many** records from S2 and S3.
- Each S2/S3 record maps to **at most one** S1 entity.
- ~25% of S2 and ~28% of S3 records are **distractors** (no match in S1).

---

## Dataset Schema

Each source file has **4 columns** (tab-separated `.tsv`):

| Column | Description | Completeness |
|--------|-------------|--------------|
| `entity_id` | Unique ID, prefixed `S1-`, `S2-`, or `S3-` | 100% |
| `business_name` | Business name (noisy) | ~100% (2–59 nulls in S2/S3) |
| `business_address` | Address (noisy) | S1: 100%, S2/S3: ~97% (3.3% missing) |
| `country` | Country label | 100% |

### Record Counts

| Split | Source 1 | Source 2 | Source 3 | Total |
|-------|----------|----------|----------|-------|
| **Train** | 2,206,821 | 5,034,617 | 5,285,604 | 12,527,042 |
| **Test** | 1,732,545 | 4,887,274 | 5,082,317 | 11,702,136 |

### Country Distribution

| Country | Train | Test | Note |
|---------|-------|------|------|
| US | 59.95% | 38.28% | Present in both |
| India | 40.05% | 47.24% | Present in both |
| France | 0.00% | 14.48% | ⚠️ **Zero-shot — test only!** |

### File Paths (relative to repo root)

```
../Data/6ab10eb3b23ba_student_resource/student_resource/dataset/
├── train/
│   ├── train_source1.tsv
│   ├── train_source2.tsv
│   ├── train_source3.tsv
│   └── train_ground_truth.tsv
└── test/
    ├── test_source1.tsv
    ├── test_source2.tsv
    └── test_source3.tsv
```

---

## Evaluation Metric

**F₀.₅ Score** — precision-heavy (precision weighted 2× over recall).

```
F₀.₅ = (1.25 × Precision × Recall) / (0.25 × Precision + Recall)
```

- **Macro-averaged**: F₀.₅ computed per S1 entity, then averaged across all S1 entities.
- **Singletons**: S1 entity with no true matches + empty prediction → score 1.0. S1 entity with no true matches + any prediction → score 0.0.
- **Implication**: When in doubt, **don't merge**. A false merge (FP) costs far more than a missed match (FN).

---

## Output Format

Two tab-separated files in `REPO/output/`:

### `matching_results.tsv` (scored on leaderboard)

| Column | Description |
|--------|-------------|
| `source1_entity_id` | S1 entity ID |
| `matched_entity_ids` | Comma-separated S2/S3 IDs (empty for singletons) |

- Exactly 1,732,545 rows (one per S1 test entity)
- No duplicate IDs within a list, no duplicate S1 rows

### `candidate_pairs.tsv` (audit only, not scored)

Same format, column `candidate_entity_ids` — the candidate set before final matching.

### Validation

```bash
python ../Data/6ab10eb3b23ba_student_resource/student_resource/utils/validate_submission.py \
    --matching REPO/REPO/output/matching_results.tsv \
    --candidate REPO/REPO/output/candidate_pairs.tsv \
    --test-dir ../Data/6ab10eb3b23ba_student_resource/student_resource/dataset/test
```

---

## Constraints

- Model ≤ **8 billion parameters**
- **MIT or Apache 2.0 license** only
- **No external data** (APIs, geocoding, business registries, etc.)

---

## Data Quirks (fill as discovered)

> Add findings here as EDA progresses. See also [`context/eda-findings.md`](eda-findings.md) for dated entries.

### Noise Patterns

- **Business name**: Typos, abbreviations, cross-script transliteration (8+ Indian scripts), synthetic aliases, domain-name formats, legal suffix variation
- **Business address**: Abbreviations, reordering, severe truncation, landmark references, ~3.3% missing in S2/S3
- **S2 vs S3**: Different noise profiles — S3 has more aggressive noise (synthetic aliases, domain names, accent injection)

### Known Traps

1. **France zero-shot**: ~15% of test S1 entities are French, with zero French training data
2. **Cross-script Indian names**: Standard string similarity returns 0.0 between Latin and Indic script versions
3. **Tab-separated files**: Reading without `sep='\t'` silently produces a single column

---

## Changelog

| Version | Date | By | Summary |
|---------|------|----|---------|
| v1.0 | 2026-09-25 | Member 1 | Initial skeleton with known details from problem statement |
