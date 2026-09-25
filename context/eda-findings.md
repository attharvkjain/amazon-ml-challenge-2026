> **Version:** v1.2 | **Last updated:** 2026-09-26 02:07 IST | **By:** Codex

# EDA Findings

**Standalone primer:** Amazon ML Challenge 2026 — Business Entity Resolution across 3 noisy data sources (~24M records total). This file is a dated log of Exploratory Data Analysis insights discovered during the competition. Entries are newest-first.

---

## How to Add an Entry

Add your finding at the **top** of the log below (newest first). Use this template:

```markdown
### YYYY-MM-DD HH:MM — [Short Title]

**By:** [Name] | **Commit:** [hash or "uncommitted"]

[Your findings here. Include numbers, examples, charts if helpful.]
```

---

## Findings Log

### 2026-09-25 16:00 — Blocking & Script Baseline Analysis

**By:** Antigravity | **Commit:** uncommitted

#### 1. Country Blocking Verification ✅

**Exhaustively checked all 7,638,365 match pairs in training ground truth. Zero cross-country matches found. Country blocking is provably safe.**

Country distribution (train):
- S1: US 59.98%, India 40.02%
- S2: US 59.92%, India 40.08%
- S3: US 59.98%, India 40.02%

Country distribution (test):
- S1: India 46.75%, US 38.27%, France 14.98%
- S2: India 47.32%, US 38.29%, France 14.39%
- S3: India 47.32%, US 38.28%, France 14.40%

**Records per S1 entity by country (test):**
- US: S2/S1 = 2.8×, S3/S1 = 2.9×
- India: S2/S1 = 2.9×, S3/S1 = 3.0×
- France: S2/S1 = 2.7×, S3/S1 = 2.8×

#### 2. Non-Latin Script Analysis 🔑

**Critical finding: S1 is 100% Latin script (0 non-Latin characters in any field).** This means transliteration is strictly a one-way operation: convert S2/S3 non-Latin → Latin to match S1.

| Source | Field | Non-Latin % |
|--------|-------|------------|
| S1 | name | 0.00% |
| S1 | address | 0.00% |
| S2 | name | 9.49% |
| S2 | address | 9.53% |
| S2 | any field | 16.70% |
| S3 | name | 5.27% |
| S3 | address | 9.04% |
| S3 | any field | 13.02% |

(S2/S3 percentages from 500K sample, extrapolated.)

#### 3. Match Distribution

- **Singletons:** 123,247 / 2,206,821 = 5.58%
- **Non-singleton match count:** median 4, mean 3.67, max 11
- **Distribution:** 1 match: 5.4%, 2: 17.0%, 3: 24.1%, 4: 21.9%, 5: 14.6%, 6: 7.5%, 7: 2.9%, 8: 0.9%, 9+: <0.2%
- **S2 per S1:** mean 1.77, max 5
- **S3 per S1:** mean 1.89, max 6
- **99.99th percentile total matches:** 10

#### 4. S2/S3 Uniqueness & Distractors

- **S2/S3 uniqueness:** Each matched S2/S3 ID maps to exactly 1 S1 entity (0 duplicates confirmed)
- **S2 distractors:** 1,340,997 / 5,034,616 = 26.6%
- **S3 distractors:** 1,340,857 / 5,285,603 = 25.4%

#### 5. Blocking K Calibration

Since each S2/S3 record maps to at most 1 S1 entity, and the max matches per S1 is 11, a blocking K=20 is very generous for finding the single correct S1 match for each S2/S3 record. Must validate blocking recall on training set (target ≥98%).

#### 6. Test S1 Count Discrepancy

**Test S1 count from actual file: 1,732,544.** The earlier note about verifying this count is resolved. Reconciliation counted data rows (excluding headers) in all seven TSVs; see [`problem-and-data.md`](problem-and-data.md) for canonical source counts.

*(No entries yet — add the first EDA finding above this line.)*

---

## Changelog

| Version | Date | By | Summary |
|---------|------|----|---------|
| v1.2 | 2026-09-26 | Codex | Closed the test-row verification note and linked canonical source counts. |
| v1.1 | 2026-09-25 | Antigravity | First EDA: country blocking verified, non-Latin script analysis, match distributions, distractor rates, blocking K calibration |
| v1.0 | 2026-09-25 | Member 1 | Initial skeleton created |
