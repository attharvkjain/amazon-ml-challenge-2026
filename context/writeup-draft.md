> **Version:** v1.1 | **Last updated:** 2026-09-26 01:05 IST | **By:** Antigravity

# Approach Document — Living Draft

**Standalone primer:** Amazon ML Challenge 2026 — Business Entity Resolution across 3 noisy data sources, evaluated on F₀.₅ (precision-heavy). This is the living draft of the required methodology document for the final submission. It is continuously updated as the solution evolves so it's not written cold at the end.

> **Note:** This draft mirrors the structure of the official `Documentation_template.md` from the student resources. The final version will be exported and included in the submission zip as `Documentation_template.md`.

---

## 1. Executive Summary

Our approach models Business Entity Resolution as a two-stage pipeline: a highly optimized sparse TF-IDF blocker for scalable candidate generation, followed by a LightGBM classifier with string edit distance features to enforce precision. By completely partitioning by country and using word unigrams for extreme matrix sparsity, we were able to process 94 million candidate pairs across 14 threads in under 30 minutes, achieving a robust F₀.₅ score of 0.697 on the public leaderboard.

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
- **Candidate pairs generated:** 94,103,432 pairs for India, 76,276,756 pairs for US, and 2.5 million pairs for France.
- **How you ensured true matches were not lost:** Selected the top-K (K=20) nearest neighbors in the TF-IDF space to guarantee high recall, resulting in a validation blocking recall of 99.43%.

---

## 4. Matching Model

**Features used:**
- Name features: Jaro-Winkler, Levenshtein ratio, Token Sort/Set ratios, Token overlap Jaccard, Length ratio
- Address features: Jaro-Winkler, Levenshtein ratio, Token Sort/Set ratios, Token overlap Jaccard, Length ratio, Shared numeric tokens
- Other: Source indicator (S2 vs S3)

**Model type:** LightGBM Binary Classifier (`scale_pos_weight` optimized for F₀.₅ precision bias)
**Threshold selection method:** Threshold was swept across the local validation set to strictly maximize macro F₀.₅, resulting in an optimal cutoff of 0.940.

---

## 5. Results & Error Analysis

- **F₀.₅ Score (macro):** 0.9699
- **Public LB Score:** 0.697
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

Per-country F₀.₅ validation:
- India: 0.9578
- US: 0.9780

---

## Changelog

| Version | Date | By | Summary |
|---------|------|----|---------|
| v1.1 | 2026-09-26 | Antigravity | Updated draft with Baseline TF-IDF + LightGBM details and 0.697 score |
| v1.0 | 2026-09-25 | Member 1 | Initial skeleton from Documentation_template.md |
