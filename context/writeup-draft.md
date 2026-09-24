> **Version:** v1.0 | **Last updated:** 2026-09-25 02:30 IST | **By:** Member 1

# Approach Document — Living Draft

**Standalone primer:** Amazon ML Challenge 2026 — Business Entity Resolution across 3 noisy data sources, evaluated on F₀.₅ (precision-heavy). This is the living draft of the required methodology document for the final submission. It is continuously updated as the solution evolves so it's not written cold at the end.

> **Note:** This draft mirrors the structure of the official `Documentation_template.md` from the student resources. The final version will be exported and included in the submission zip as `Documentation_template.md`.

---

## 1. Executive Summary

*[TODO] 2–3 sentence overview of your approach and key innovations. Write this last.*

---

## 2. Methodology

### 2.1 Problem Analysis

*[TODO] Key insights discovered during EDA — noise patterns, address variations, missing fields, country distribution, etc. Pull from [`context/eda-findings.md`](eda-findings.md).*

### 2.2 Solution Strategy

*[TODO] High-level approach description.*

**Approach Type:** [TODO — Blocking + Classifier / End-to-End / Graph-Based / Hybrid]
**Core Innovation:** [TODO]

---

## 3. Candidate Generation (Blocking)

*[TODO] Describe blocking strategy, keys used, candidate set size, recall guarantees.*

- **Blocking keys used:** [TODO]
- **Candidate pairs generated:** [TODO]
- **How you ensured true matches were not lost:** [TODO]

---

## 4. Matching Model

**Features used:**
- Name features: [TODO]
- Address features: [TODO]
- Other: [TODO]

**Model type:** [TODO]
**Threshold selection method:** [TODO — should be F₀.₅ optimization on validation set]

---

## 5. Results & Error Analysis

- **F₀.₅ Score (macro):** [TODO — best validation score]
- **Public LB Score:** [TODO — best leaderboard score]
- **Common false positives (wrong merges):** [TODO]
- **Common false negatives (missed matches):** [TODO]

---

## 6. Conclusion

*[TODO] 2–3 sentences: approach summary, key achievements, lessons learned.*

---

## Appendix

### A. Code Artefacts

*[TODO] Summarize the code structure and entry points. The full code ships in the submission zip under `code/business_entity_resolution/`.*

### B. Additional Results

*[TODO] Charts, graphs, ablation studies, per-country breakdowns.*

---

## Changelog

| Version | Date | By | Summary |
|---------|------|----|---------|
| v1.0 | 2026-09-25 | Member 1 | Initial skeleton from Documentation_template.md |
