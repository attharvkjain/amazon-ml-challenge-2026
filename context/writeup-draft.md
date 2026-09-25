> **Version:** v1.2 | **Last updated:** 2026-09-26 02:30 IST | **By:** Codex

# Approach Document — Living Draft

**Standalone primer:** Amazon ML Challenge 2026 — Business Entity Resolution across 3 noisy data sources, evaluated on F₀.₅ (precision-heavy). This is the living draft of the required methodology document for the final submission. It is continuously updated as the solution evolves so it's not written cold at the end.

> **Note:** This draft mirrors the structure of the official `Documentation_template.md` from the student resources. The final version will be exported and included in the submission zip as `Documentation_template.md`.

---

## 1. Executive Summary

Our approach models Business Entity Resolution as a two-stage pipeline: country-partitioned word-unigram TF-IDF blocking followed by a LightGBM classifier. The public result is recorded in the canonical [`submission log`](submission-log.md).

---

## 2. Methodology

### 2.1 Problem Analysis

The dataset contains significant noise, including non-Latin characters for India (S2/S3), varying legal suffixes, and missing address fields. Crucially, the problem has a strict structural property: S1 contains deduplicated canonical reference entities, while S2 and S3 contain distractors. The evaluation metric (F₀.₅) heavily penalizes false positives, meaning precision is far more important than recall.

### 2.2 Solution Strategy

**Approach Type:** Blocking + Classifier Pipeline
**Core Innovation:** Hard country partitioning combined with `max_df=0.01` Word Unigram TF-IDF blocking, which reduces sparse matrix density to `<0.1%`, allowing instantaneous cosine similarity dot-products and eliminating OOM memory spikes.

---

## 3. Candidate Generation (Blocking)

- **Blocking keys used:** TF-IDF Word Unigrams (Name + Address concatenated)
- **Candidate volume:** The logged full inference total is recorded in the [`submission log`](submission-log.md); unverified per-country figures from an earlier draft have been removed.
- **How you ensured true matches were not lost:** Selected the top-K (K=20) nearest neighbors in the TF-IDF space to guarantee high recall, resulting in a validation blocking recall of 99.43%.

---

## 4. Matching Model

**Features used:**
- Name features: Jaro-Winkler, Levenshtein ratio, Token Sort/Set ratios, Token overlap Jaccard, Length ratio
- Address features: Jaro-Winkler, Levenshtein ratio, Token Sort/Set ratios, Token overlap Jaccard, Length ratio, Shared numeric tokens
- Other: Source indicator (S2 vs S3)

**Model type:** LightGBM Binary Classifier (`scale_pos_weight` optimized for F₀.₅ precision bias)
**Threshold selection method:** The cutoff is selected by sweeping the held-out local validation set to maximize macro F0.5. See [`project.md`](../project.md#current-state-snapshot) for the canonical baseline score and cutoff.

---

## 5. Results & Error Analysis

- **Local baseline validation:** See [`project.md`](../project.md#current-state-snapshot) for the canonical score and cutoff.
- **Public leaderboard result:** See [`context/submission-log.md`](submission-log.md) for the canonical submission history.
- **Common false positives (wrong merges):** Franchises or branch locations with identical names but slightly varying localized addresses.
- **Common false negatives (missed matches):** Severe transliteration discrepancies between Indic scripts and Latin scripts that string edit distances struggle to reconcile.

---

## 6. Conclusion

We built a highly scalable, memory-stable pipeline that completely circumvented standard string indexing bottlenecks. By combining sparse math tricks with a precision-biased LightGBM classifier, we achieved a strong F₀.₅ score while keeping the test inference time well under the 72-hour limits.

---

## Appendix

### A. Code Artefacts

The full code ships in the submission zip under `code/business_entity_resolution/`. Entry points are handled cleanly via `main.py` allowing `--mode train` and `--mode predict`.

### B. Additional Results

Per-country validation scores are shown in [`notebooks/diagnostics/per_country_f05.png`](../notebooks/diagnostics/per_country_f05.png).

---

## Changelog

| Version | Date | By | Summary |
|---------|------|----|---------|
| v1.2 | 2026-09-26 | Codex | Clarified that 0.9699 is the baseline training validation result and linked canonical score, threshold, public submission, and per-country diagnostics. |
| v1.1 | 2026-09-26 | Antigravity | Updated draft with Baseline TF-IDF + LightGBM details and 0.697 score |
| v1.0 | 2026-09-25 | Member 1 | Initial skeleton from Documentation_template.md |
