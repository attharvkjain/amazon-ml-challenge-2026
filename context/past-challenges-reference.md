> **Version:** v1.0 | **Last updated:** 2026-09-25 14:25 IST | **By:** Antigravity

# PRIOR-YEAR REFERENCE: Past Amazon ML Challenges

**⚠️ IMPORTANT:** This document contains research on *past* editions of the Amazon ML Challenge (2021–2025). This is **NOT** the specification for the current 2026 challenge. For the current 2026 problem statement and constraints, refer to [`context/problem-and-data.md`](problem-and-data.md).

---

## Challenge History & Recurring Themes

Based on our research into the winning approaches from previous Amazon ML Challenges, several consistent patterns emerge regarding data quality, modeling strategies, and common pitfalls.

| Year | Task | Modalities | Winning Strategies / Takeaways |
|------|------|------------|--------------------------------|
| **2021** | Browse-node classification (~10K classes) | Text metadata | Representation quality, efficient retrieval, and scalability are critical for extreme multi-class problems. |
| **2022** | *Archival Gap* | Unknown | *No reliable technical details recovered.* |
| **2023** | Product-length regression | Text + Product Type ID | Intelligent target transformation (e.g. log transform, clipping), strong pretrained text encoders (BERT/RoBERTa), and diverse ensembling. |
| **2024** | Image entity extraction (e.g. dimensions/weight) | Images + Query | Aggressive data curation, fine-tuning capable VLMs (e.g. Qwen-VL) with few-shot + SFT, and rigorous output normalization/post-processing. |
| **2025** | Smart Product Pricing | Text + Images | Strong local validation, multimodal feature engineering (handling pack quantity/brand effects), and ensembling diverse models instead of relying on a single monolith. |

---

## Key Patterns in Winning Approaches

1. **Aggressive Data Curation and Cleaning:**
   Amazon's datasets are famously noisy. Top teams invariably spend significant time filtering outliers, correcting labels where possible, and normalizing text/units before feeding data to their models.

2. **Explicit Metadata Exploitation:**
   Winning models don't just throw raw text/images at an encoder. They explicitly model structured metadata (like product type, brand, country) through categorical embeddings, derived features, or group-wise baselines.

3. **Intelligent Post-Processing:**
   Metrics in these challenges are highly sensitive to exact formatting. Normalizing units, bounding regression outputs within valid ranges, and calibrating probabilities yield substantial leaderboard gains. 

4. **Rigorous Local Validation:**
   Because the public leaderboard often evaluates on a subset of the data, top teams rely on a rock-solid local cross-validation strategy that perfectly mimics the official evaluation metric (e.g. optimizing directly for F-beta or SMAPE, not a proxy loss).

5. **Ensembling over Scaling:**
   Instead of maxing out the parameter limits with a single model, winners consistently ensemble diverse model architectures (e.g. combining different text backbones or mixing OCR pipelines with VLMs) to improve robustness and score.

---

## Common Pitfalls to Avoid

- **Blindly Trusting the Data:** Failing to account for highly skewed targets, missing modalities, or synthetic distractors.
- **Optimizing the Wrong Metric:** Training on standard loss (like MSE or Cross-Entropy) without aligning the final selection or thresholding to the challenge's specific metric.
- **Ignoring the Rules:** Many teams fail because they use external data (which is strictly prohibited and heavily policed) or violate the model size limits (e.g., >8B parameters).
- **Overfitting to the Train Distribution:** Building brittle, hand-crafted rules that fail on unseen data or test-only categories (e.g., zero-shot countries).

---

## Changelog

| Version | Date | By | Summary |
|---------|------|----|---------|
| v1.0 | 2026-09-25 | Antigravity | Initial creation of past challenges reference from 2021-2025 research. |
