> **Version:** v1.2 | **Last updated:** 2026-09-26 02:50 IST | **By:** Codex

# Reconciliation Log

**APPEND-ONLY.** Add each completed reconciliation as a new dated entry. Never rewrite earlier entries.

## 2026-09-26 - Post-milestone reconciliation

- **Scope audited:** `project.md`, `agents.md`, every file in `context/`, the Master Index paths, tracked repository paths, active pipeline configuration and entry point, skill locations, local data counts, submission outputs, and referenced diagnostic artifacts. `context/experiment-log.md` and `context/submission-log.md` were inspected as evidence; their existing rows were not edited.
- **DOC-ONLY work:** corrected active lowercase `data/` and research paths; fixed inconsistent training/test record counts, broken validator command paths, stale cleaner and sampling descriptions, unsupported feature/architecture claims, unresolved placeholder score references, and the submission archive layout. Kept unknown team roster and machine specifications open rather than guessing.
- **Approved code-adjacent work applied:** C1 uses the active lowercase data location; C2 training defaults to `SAMPLE_FRAC=1.0` while remaining configurable; C3 saves the tuned validation threshold and requires it in predict mode; C5 identifies 0.9699 as baseline training validation and preserves the documented 0.940 cutoff; C6 links the verified country diagnostics; C7 organizes the two historical matching TSVs as submissions 001 and 002.
- **Code-adjacent item left open:** C4 CV behavior remains for human review and was not changed. The stale `blocker.py` module docstring describing character n-gram blocking also remains for review; implementation uses the configured word-unigram TF-IDF setup.
- **Other open items:** team roles/contact values and per-machine environment specifications remain `TBD` in their canonical documents because this run did not have verified values. Removed the write-up draft's per-country candidate-volume figures because their run scope was not specified and they conflict with the canonical submission log's 94M full-inference total. Replaced stale architecture claims for cleaner status, feature inventory, veto rules, skill paths, and proposed baseline timing with verified implementation details; this also removed the obsolete broken-cleaner warning and build-first recommendation. These removals are recorded here. Other historical run details not backed by a canonical log remain open for later verification.
- **Commits:** see the commits on branch `reconcile/2026-09-26-0200`.


## 2026-09-26 - Approved follow-up

- Updated the `blocker.py` module docstring to describe the implemented word-unigram TF-IDF blocker. This was the approved C8 documentation-only correction; runtime behavior is unchanged.
- Added `miscelleaneous/` to `.gitignore` as requested and removed its previously tracked historical proposal from the Git index without deleting the local copy. The untracked Tanil draft remains local and ignored.
- C4 remains open and unchanged for later review.

## Changelog

| Version | Date | By | Summary |
|---------|------|----|---------|
| v1.2 | 2026-09-26 | Codex | Appended the approved C8 correction and the miscellaneous-directory ignore follow-up. |
| v1.1 | 2026-09-26 | Codex | Appended a reconciliation note documenting the removal of unverified, conflicting per-country candidate counts from the write-up. |
| v1.0 | 2026-09-26 | Codex | Started the append-only reconciliation run log and recorded this audit. |
