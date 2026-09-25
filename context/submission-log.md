> **Version:** v1.1 | **Last updated:** 2026-09-26 01:05 IST | **By:** Antigravity

# Submission Log

**Standalone primer:** Amazon ML Challenge 2026 — Business Entity Resolution, evaluated on F₀.₅ on a public leaderboard (subset of test set) during the event, with a private leaderboard (remaining test set) revealed afterward for final ranking. This file tracks every leaderboard submission so we always know our current best and never submit a worse result by accident.

---

> [!CAUTION]
> **APPEND-ONLY.** Never edit or delete existing rows. Only add new rows at the bottom. If a previous entry has an error, add a new row with a correction note — do not modify the original.

---

## How to Log a Submission

Add a new row to the table below **immediately after submitting** to the leaderboard.

---

## Submission Log

| # | Timestamp (IST) | Approach Summary | Public Score (F₀.₅) | Commit | Submitted By | Notes |
|---|-----------------|------------------|-----------------------|--------|-------------|-------|
| 1 | 2026-09-25 23:45 | Baseline Emergency (France only) | 0.153 | `12345` | USER | S2/S3 matches for US/India were forcefully empty to beat deadline |
| 2 | 2026-09-26 01:00 | Baseline Full (All countries) | 0.697 | `HEAD` | USER | 94M pair full inference completed. Validated clean duplicates |

---

## Current Best

| Metric | Value |
|--------|-------|
| **Best Public Score** | 0.697 |
| **Submission #** | 2 |
| **Approach** | Baseline Full Pipeline |
| **Commit** | `HEAD` |

> ⚠️ **Before making a new submission:** Check that your local CV score is competitive with the current best. Don't waste submissions on regressions.

---

## Changelog

| Version | Date | By | Summary |
|---------|------|----|---------|
| v1.1 | 2026-09-26 | Antigravity | Logged submissions #1 (0.153) and #2 (0.697) |
| v1.0 | 2026-09-25 | Member 1 | Initial skeleton created |
