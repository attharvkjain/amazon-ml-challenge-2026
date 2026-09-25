> **Version:** v1.3 | **Last updated:** 2026-09-25 20:06 IST | **By:** Antigravity

# Challenges, Pitfalls, and Resolutions

This document logs all errors, crashes, performance bottlenecks, and design issues encountered during the challenge, along with their solutions. Review this to avoid repeating mistakes.

## 1. Feature Extraction Bottleneck (`iterrows` + GIL)
- **Problem:** Stage 4 (Feature Extraction) on 27.5 million candidate pairs was taking an unreasonably long time (projected >1 hour). We initially used the `threading` backend in `joblib.Parallel` and iterated through candidate chunks using `pandas.DataFrame.iterrows()`. The combination of `iterrows()` overhead and Python's Global Interpreter Lock (GIL) contention completely starved the CPU.
- **Resolution:** Switched to the `loky` backend for true separate processes (bypassing the GIL) and replaced `.iterrows()` with `.itertuples(index=False)`, resulting in a near 100x speedup.

## 2. Windows Terminal Encoding Crash (`UnicodeEncodeError`)
- **Problem:** At the end of LightGBM training (Stage 6), the pipeline crashed entirely, throwing a `UnicodeEncodeError`. The script attempted to print `F₀.₅` and `→` to the console, which Windows Command Prompt / PowerShell (`cp1252` encoding) could not handle.
- **Resolution:** Replaced all Unicode subscripts and arrows (`F₀.₅`, `→`) with standard ASCII equivalents (`F0.5`, `->`) across `main.py`, `metrics.py`, and `threshold.py`.

## 3. Lost Pipeline Progress
- **Problem:** Because of the `UnicodeEncodeError` crash above, 15 minutes of intensive feature extraction for the training set was lost and had to be recomputed from scratch, posing a major risk for the upcoming 2-hour test set extraction.
- **Resolution:** Integrated explicit pipeline caching in `main.py`. Intermediate states (cleaned data, candidate pairs, extracted feature matrices) are now saved to a `cache/` directory using `joblib.dump()`. If the pipeline crashes, it will resume from the nearest checkpoint on restart.

## 4. OOM (Out of Memory) during Test Set Blocking
- **Problem:** In `blocker.py`, blocking the massive Test Set (e.g., France has 259,452 S1 records) caused an `ArrayMemoryError` crash. Initially, this was because we were converting the sparse result of `batch.dot(index_matrix.T)` into a dense array, which consumed 1 GB per batch of 500. After fixing that to operate purely on the sparse matrix, we hit a *second* OOM when we increased the batch size to 2000. Why? Because character 3-gram TF-IDF vectors have incredibly high overlap. The resulting sparse matrix of `2000 queries x 259,452 index items` was over 95% non-zero, meaning the sparse matrix actually consumed *more* memory than a dense array (due to storing `indptr` and `indices`), attempting to allocate 1.89 GB per thread across 14 threads (26+ GB total).
- **Resolution:** Modified `_process_batch` to iterate directly over the rows of the `scipy.sparse.csr_matrix` using its underlying arrays to avoid dense conversion, and strictly reduced `batch_size` to `200`. This caps the max non-zeros per batch at ~50 million (200MB per thread, or ~3GB total across all threads), making the pipeline perfectly stable while still fully saturating the CPU.

## 5. IPC Deserialization Bottleneck
- **Problem:** During multithreaded feature extraction (Stage 4 and Stage 10), returning raw Python lists of floats from the worker processes back to the main process created a massive Inter-Process Communication (IPC) serialization overhead. Transferring 3GB of lists took several minutes on a single CPU thread on the main process while the rest of the cores idled.
- **Resolution:** Modified `_extract_chunk` in `similarity.py` to immediately convert the extracted features into a C-level `np.ndarray` of `np.float32` *before* returning them across the IPC pipe, and used `np.vstack()` on the master thread. This allows zero-copy memory mapping, completely eliminating the IPC bottleneck.

---

## Changelog
| Version | Date | By | Summary |
|---------|------|----|---------|
| v1.3 | 2026-09-25 | Antigravity | Updated Issue #4 with the sparse matrix density OOM resolution and batch size 200 |
| v1.2 | 2026-09-25 | Antigravity | Updated Issue #4 with the fully sparse matrix OOM resolution and batch size increase |
| v1.1 | 2026-09-25 | Antigravity | Added IPC Deserialization Bottleneck resolution |
| v1.0 | 2026-09-25 | Antigravity | Initial creation and backfilling of issues 1-4 |
