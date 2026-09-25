> **Version:** v1.0 | **Last updated:** 2026-09-25 12:55 IST | **By:** Antigravity

# Umbrella Research Findings: Business Entity Resolution

This document synthesizes the findings from an extensive research phase on the paradigms outlined in the research plan. The focus is on offline, single-node scalable solutions (e.g., DuckDB, Polars), hybrid ML architectures, handling multilingual/cross-script data, and maximizing the F0.5 score within the 8B parameter limit.

---

## 1. Blocking & Candidate Generation
The goal of blocking is to reduce the $O(N^2)$ search space efficiently without losing true matches (maximizing recall at this stage).

*   **DuckDB + Splink:** [Splink](https://moj-analytical-services.github.io/splink/) is currently a state-of-the-art open-source probabilistic record linkage library. Running Splink on top of **DuckDB** provides massive single-node performance, avoiding the overhead of Spark while handling 24M+ records easily. It uses the Fellegi-Sunter model and allows for complex SQL-based blocking rules.
*   **Semantic Blocking with FAISS:** Instead of relying entirely on lexical rules (which fail on heavy noise or cross-script), modern pipelines use **Dense Retrieval**. By embedding business names using lightweight models and indexing them with **FAISS (Facebook AI Similarity Search)**, we can perform fast approximate nearest neighbor (ANN) searches to generate candidate pairs.

## 2. Cross-Lingual & Cross-Script Paradigms (Zero-Shot & Indic)
Given the presence of 8+ Indian scripts and zero-shot French data, purely lexical matching will fail.

*   **Indic NLP & Transliteration:** 
    *   **IndicXlit** (from AI4Bharat) is the current SOTA for offline transliteration of Indian languages to a common script (Romanization).
    *   **Indic NLP Library** is highly recommended for script normalization and preprocessing before matching.
*   **Multilingual Representation (MuRIL):** **MuRIL** (Multilingual Representations for Indian Languages) is specifically pre-trained to handle the linguistic nuances and code-mixing of Indic languages, making it superior to standard BERT for this dataset.
*   **Zero-Shot Transfer (France):** Research shows that **SentencePiece** tokenization preserves morphological structure better than BPE for low-resource and zero-shot settings. Using multilingual embeddings like **LaBSE** (Language-agnostic BERT Sentence Embedding) or **E5-multilingual** can map English, French, and transliterated Hindi into a shared vector space, allowing a model trained on US/India data to generalize to French records zero-shot.

## 3. Entity Matching & Classification (Hybrid Pipelines)
To achieve the best possible leaderboard score within an 8B parameter limit, a **Hybrid Framework** is the industry standard for 2024.

*   **Stage 1: Fast ML Re-ranking (The Workhorse):** 
    *   After blocking, extract features (Levenshtein distance, Jaro-Winkler, Cosine similarity of embeddings, Phonetic overlap).
    *   Train an **XGBoost** or **LightGBM** classifier on these features. This handles 90% of the matching with extremely high speed and solid accuracy.
*   **Stage 2: Small LLM / Cross-Encoder (The Judge):** 
    *   For "borderline" cases where the XGBoost model is uncertain (e.g., probability between 0.4 and 0.6), pass the records to a deeper model.
    *   **Cross-Encoders:** Models like `XLM-RoBERTa` can take `[Record A] [SEP] [Record B]` and output a highly accurate match probability.
    *   **Small LLMs:** Open-source models under 8B parameters (e.g., **Llama-3-8B**, **Qwen-2-7B**) can be fine-tuned via LoRA/QLoRA or prompted zero-shot to act as the final judge for the hardest cases.

## 4. Distractor Rejection & F0.5 Optimization
The F0.5 metric heavily penalizes false positives (merging distinct entities or matching a distractor). Since ~25-28% of S2/S3 are distractors (singletons), aggressive pruning is required.

*   **Asymmetric Loss Functions:** Standard Cross-Entropy treats false positives and false negatives equally. SOTA approaches use **Focal Loss** or custom **Asymmetric Loss** to heavily penalize false positives during training. This forces the ML model (XGBoost or neural network) to learn a conservative decision boundary natively.
*   **Hard Rule-Based Vetoes:** Machine learning models are great for recall but can hallucinate matches. Post-ML, implement hard heuristics to veto matches (e.g., "If the country is different, immediately reject" or "If numerical digits in the address differ entirely, veto the match").
*   **Risk-Based Threshold Tuning:** Do not use a flat 0.5 probability threshold. Calibrate the threshold using the validation set to explicitly maximize the F0.5 score. Conformal prediction can be used to output prediction sets, and we only accept matches with near-certain confidence.

## 5. Next Steps for Implementation
1.  **Set up the Data Engine:** Initialize DuckDB or Polars for fast single-node data manipulation.
2.  **Baseline Blocking:** Implement lexical blocking keys and measure candidate recall.
3.  **Transliteration Pipeline:** Integrate IndicXlit to romanize the dataset.
4.  **Feature Extraction & ML Baseline:** Compute string/embedding similarities and train an XGBoost baseline.

---

## Changelog

| Version | Date | By | Summary |
|---------|------|----|---------|
| v1.0 | 2026-09-25 | Antigravity | Initial creation of the umbrella research findings |
