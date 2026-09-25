> **Version:** v1.2 | **Last updated:** 2026-09-25 19:59 IST | **By:** Antigravity

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
- **Problem:** In `blocker.py`, the original implementation converted the sparse `batch.dot(index_matrix.T)` result into a dense numpy array before applying `np.argpartition` to find the top K candidates. For the massive Test Set (e.g., France has 259,452 S1 records), this dense array for a batch of 500 queries consumed 1 GB of memory. Across 14 threads, this caused a 14+ GB memory spike and an `ArrayMemoryError` crash.
- **Resolution:** Modified `_process_batch` to iterate directly over the rows of the `scipy.sparse.csr_matrix` using its underlying `indptr`, `indices`, and `data` arrays. By running `np.argpartition` exclusively on the non-zero elements of the sparse array, memory usage dropped to virtually zero, allowing us to safely increase `batch_size` back up to 2000 for faster processing.

## 5. IPC Deserialization Bottleneck
- **Problem:** During multithreaded feature extraction (Stage 4 and Stage 10), returning raw Python lists of floats from the worker processes back to the main process created a massive Inter-Process Communication (IPC) serialization overhead. Transferring 3GB of lists took several minutes on a single CPU thread on the main process while the rest of the cores idled.
- **Resolution:** Modified `_extract_chunk` in `similarity.py` to immediately convert the extracted features into a C-level `np.ndarray` of `np.float32` *before* returning them across the IPC pipe, and used `np.vstack()` on the master thread. This allows zero-copy memory mapping, completely eliminating the IPC bottleneck.

---

## Changelog
| Version | Date | By | Summary |
|---------|------|----|---------|
| v1.2 | 2026-09-25 | Antigravity | Updated Issue #4 with the fully sparse matrix OOM resolution and batch size increase |
| v1.1 | 2026-09-25 | Antigravity | Added IPC Deserialization Bottleneck resolution |
| v1.0 | 2026-09-25 | Antigravity | Initial creation and backfilling of issues 1-4 |
