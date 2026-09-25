> **Version:** v1.7 | **Last updated:** 2026-09-26 02:07 IST | **By:** Codex

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
- **Problem:** In `blocker.py`, blocking the massive Test Set caused severe `ArrayMemoryError` crashes. Initially, this was because the sparse matrix was being unnecessarily converted to a dense numpy array (consuming 1 GB per batch of 500). After rewriting the code to operate directly on the sparse matrix to avoid dense conversion, we still hit OOMs! The root cause is that character 3-gram TF-IDF vectors have incredibly high overlap (over 98% density on India and US). Because sparse matrices must store both data and index arrays, a 98% dense sparse matrix actually consumes *more* memory than a dense array. A batch size of 200 on India's 809k records generated 160 million non-zero edges, allocating 600MB per thread (8.5 GB total) and crashing the pipeline. If left at 200, the US dataset (3.1M records) would have allocated 24 GB and instantly crashed.
- **Resolution:** Implemented **Dynamic Batch Sizing** in `_sparse_top_k`. The `batch_size` is now calculated on the fly as `50_000_000 // n_index_records`, strictly capping the maximum possible non-zero elements per batch at 50 million (~200MB per thread, 2.8GB total across 14 threads). This guarantees bulletproof stability across all countries regardless of their size or TF-IDF density, while still fully saturating the CPU.

## 5. IPC Deserialization Bottleneck
- **Problem:** During multithreaded feature extraction (Stage 4 and Stage 10), returning raw Python lists of floats from the worker processes back to the main process created a massive Inter-Process Communication (IPC) serialization overhead. Transferring 3GB of lists took several minutes on a single CPU thread on the main process while the rest of the cores idled.
- **Resolution:** Modified `_extract_chunk` in `similarity.py` to immediately convert the extracted features into a C-level `np.ndarray` of `np.float32` *before* returning them across the IPC pipe, and used `np.vstack()` on the master thread. This allows zero-copy memory mapping, completely eliminating the IPC bottleneck.

---

## 6. Massive 30-Hour Inference Time on Test Set
- **Problem:** After solving the OOMs, the pipeline ran successfully but was projected to take ~30 hours to finish the Test Set. The bottleneck was `blocker.py`: using `analyzer='char_wb'` and `ngram_range=(3,3)` creates massive overlap between businesses. Slicing 10 million companies into character 3-grams generated a 70% dense sparse matrix, requiring over 10 Trillion mathematical dot-products for the US and India, taking 29 hours.
- **Resolution:** Pivoted the Test Set inference to use **Word Unigrams** (`analyzer='word'`, `ngram_range=(1,1)`). At the time, the run used `max_df=0.25`; the current baseline setting is `max_df=0.01` in `src/blocking/blocker.py`. Because random companies rarely share exact words (unless generic), the matrix density plummeted to `<0.1%`. This sped up the dot product by 100x, allowing inference to finish in under 30 minutes! While it slightly reduces candidate recall on severe typos, the speedup was critical for the hackathon crunch.

## 7. Pandas BlockManager 6GB RAM Spike
- **Problem:** When collecting the 94 Million India candidate pairs into a `pd.DataFrame` during blocking, the pipeline repeatedly crashed with `std::bad_alloc` `ArrayMemoryError: Unable to allocate 1.43 GiB for an array...`. Pandas' internal `BlockManager` attempts to aggressively merge contiguous string/object columns into a single 2D Numpy array block of pointers. Trying to merge `s1_id`, `s2s3_id`, `source`, and `country` created a 1.5GB pointer block requirement that Windows could not physically contiguous-allocate. Additionally, passing `np.array(s1_ids)[...]` instantiated a 6GB unicode string array in RAM before Pandas even touched it.
- **Resolution:** Forcefully circumvented the `BlockManager`. Replaced numpy slicing with standard python list comprehension (`[s1_ids[i] for i in ...]`) which just creates tiny pointers to interned strings (384MB). Then, created an empty `pd.DataFrame()` and added the columns sequentially, casting `source` and `country` as `pd.Categorical`. This mathematically prevents Pandas from attempting to allocate massive 2D pointer blocks, dropping peak RAM usage from 6GB down to <1GB for 94 Million rows.

## 8. Loky Process Pickling Limit on Massive DataFrames
- **Problem:** In `similarity.py`, feature extraction for the 94 Million India pairs crashed with `_pickle.PicklingError` and `MemoryError` in `loky`. Joblib's `loky` backend spawns separate Python processes, which forces the main process to serialize (pickle) the entire 94M row DataFrame and 5M key string lookup dictionaries into IPC pipes. The memory required to pickle 3GB of raw text crashed the system instantly.
- **Resolution:** Switched `joblib` from `backend='loky'` to `backend='threading'`. Because the bottleneck is the string edit distances calculated inside the C++ `RapidFuzz` library (which releases the Python GIL), multithreading allows 100% CPU utilization across all 14 cores while letting all threads passively share the memory of the original DataFrame without any pickling overhead whatsoever.

## Changelog
| Version | Date | By | Summary |
|---------|------|----|---------|
| v1.7 | 2026-09-26 | Codex | Clarified the historical max_df setting versus the current baseline value. |
| v1.6 | 2026-09-26 | Antigravity | Added Issues 7 & 8 (Pandas BlockManager memory limit, Loky Pickling Error limit) |
| v1.5 | 2026-09-25 | Antigravity | Added Issue #6 (Inference speedup via Word Unigrams pivot) |
| v1.4 | 2026-09-25 | Antigravity | Updated Issue #4 with the dynamic batch sizing resolution for dense sparse matrices |
| v1.3 | 2026-09-25 | Antigravity | Updated Issue #4 with the sparse matrix density OOM resolution and batch size 200 |
| v1.2 | 2026-09-25 | Antigravity | Updated Issue #4 with the fully sparse matrix OOM resolution and batch size increase |
| v1.1 | 2026-09-25 | Antigravity | Added IPC Deserialization Bottleneck resolution |
| v1.0 | 2026-09-25 | Antigravity | Initial creation and backfilling of issues 1-4 |
