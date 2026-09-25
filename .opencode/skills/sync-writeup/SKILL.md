---
name: sync-writeup
description: >-
  Pulls current best score and architecture notes into the writeup draft.
  Triggers when asked to sync the methodology doc or writeup draft.
---
> **Version:** v1.0 | **Last updated:** 2026-09-26 02:27 IST | **By:** Codex


# Sync Writeup Skill

The methodology document must always reflect the team's current best approach.

1. **Gather facts**: Read `project.md` (Current State Snapshot) for the best score, and `context/architecture.md` for the latest pipeline design and model shortlist.
2. **Update draft**: Update `context/writeup-draft.md` with these details. Ensure the methodology, candidate generation strategy, and model architecture accurately match what produced the best score.
3. **Format**: Follow the official template structure found in `SUBMISSION/Documentation_template.md`.
4. **Version Bump**: Bump the version and add a changelog entry to `context/writeup-draft.md`.


## Changelog

| Version | Date | By | Summary |
|---------|------|----|---------|
| v1.0 | 2026-09-26 | Codex | Added version metadata and changelog per the project documentation policy. |
