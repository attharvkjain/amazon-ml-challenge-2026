> **Version:** v1.4 | **Last updated:** 2026-09-25 14:26 IST | **By:** Antigravity

# Amazon ML Challenge 2026 — Project Master Index

**This is the single source of truth for the entire project.** Every teammate and every AI agent reads this file first. If you need to find anything in this repo, start here.

---

## Project Summary

| Field | Detail |
|-------|--------|
| **Competition** | Amazon ML Challenge 2026 |
| **Problem** | Business Entity Resolution — given business records from 3 independent data sources with noisy/inconsistent fields, determine which records across sources refer to the same real-world business entity |
| **Task** | Match Source 2 and Source 3 records to deduplicated Source 1 reference entities |
| **Evaluation Metric** | F₀.₅ (precision-heavy, macro-averaged per S1 entity) |
| **Hackathon Window** | Sep 25, 2026 9:00 AM IST – Sep 27, 2026 9:00 PM IST (72 hours) |
| **Submission Format** | `matching_results.tsv` (leaderboard upload) + `candidate_pairs.tsv` + code zip + methodology doc |
| **Constraints** | Model ≤ 8B parameters, MIT/Apache 2.0 license only, no external data/APIs |

### Team

| Member | Role | Contact |
|--------|------|---------|
| Member 1 | TBD | TBD |
| Member 2 | TBD | TBD |
| Member 3 | TBD | TBD |
| Member 4 | TBD | TBD |

> See [`context/team-roles.md`](context/team-roles.md) for detailed roles, focus areas, and availability.

---

## Master Index

> **For AI agents:** Use this table to locate any file or folder. Do NOT guess paths — if it's not listed here, ask.

| Path | Type | Description |
|------|------|-------------|
| [`project.md`](project.md) | File | **This file** — master index, single source of truth |
| [`agents.md`](agents.md) | File | Operating manual for AI coding agents |
| [`SUBMISSION/Documentation_template.md`](SUBMISSION/Documentation_template.md) | File | Methodology write-up for final submission (official template) |
| [`context/problem-and-data.md`](context/problem-and-data.md) | File | Problem statement, dataset schema, eval metric, constraints, data quirks |
| [`context/past-challenges-reference.md`](context/past-challenges-reference.md) | File | Prior-year reference of winning approaches and common pitfalls |
| [`skills/`](skills/) | Folder | Canonical provider-agnostic Agent Skills folder |
| [`context/eda-findings.md`](context/eda-findings.md) | File | Dated log of EDA insights |
| [`context/environment-setup.md`](context/environment-setup.md) | File | Local environment reproduction steps per teammate |
| [`context/experiment-log.md`](context/experiment-log.md) | File | **APPEND-ONLY** — every approach tried, params, CV score, commit |
| [`context/submission-log.md`](context/submission-log.md) | File | **APPEND-ONLY** — every leaderboard submission with public score |
| [`context/git-workflow.md`](context/git-workflow.md) | File | Branch naming, PR/merge rules, notebook conflict prevention |
| [`context/team-roles.md`](context/team-roles.md) | File | Team member roles, focus areas, availability during 72h |
| [`context/writeup-draft.md`](context/writeup-draft.md) | File | Living draft of the methodology document (internal WIP) |
| [`SUBMISSION/code/business_entity_resolution/src/`](SUBMISSION/code/business_entity_resolution/src/) | Folder | **All pipeline source code** — submission package location |
| [`SUBMISSION/code/business_entity_resolution/README.md`](SUBMISSION/code/business_entity_resolution/README.md) | File | Reproduction instructions (ships in submission zip) |
| [`SUBMISSION/code/business_entity_resolution/requirements.txt`](SUBMISSION/code/business_entity_resolution/requirements.txt) | File | Pinned dependencies (ships in submission zip) |
| [`SUBMISSION/output/`](SUBMISSION/output/) | Folder | Submission output files (`matching_results.tsv`, `candidate_pairs.tsv`) |
| [`scripts/package_submission.py`](scripts/package_submission.py) | File | Creates the submission zip from repo contents |
| [`Analysis and Research/`](Analysis%20and%20Research/) | Folder | Pre-competition analysis & winner playbook (existing) |
| [`Data/`](Data/) | Folder | Raw dataset — **DO NOT commit to git** (in `.gitignore`) |
| [`amazon docs given/`](amazon%20docs%20given/) | Folder | Official problem statement & guidelines PDFs |
| [`notebooks/`](notebooks/) | Folder | Jupyter notebooks (clear outputs before committing) |
| [`.gitignore`](.gitignore) | File | Git ignore rules — keeps raw data & large files out of version control |

---

## Current State Snapshot

> **Anti-regression anchor.** Before merging any result, check that it actually beats the current best. Update this section whenever a new best is achieved.

| Metric | Value | Details |
|--------|-------|---------|
| **Best Local CV Score (F₀.₅)** | N/A | No experiments run yet |
| **Best Public LB Score** | N/A | No submissions yet |
| **Approach** | N/A | — |
| **Commit Hash** | N/A | — |
| **Produced By** | N/A | — |
| **Date** | N/A | — |

> See [`context/experiment-log.md`](context/experiment-log.md) for full experiment history and [`context/submission-log.md`](context/submission-log.md) for submission history.

---

## Rules & Guidelines

### Coding Conventions

- Python 3.10+
- Type hints encouraged
- f-strings over `.format()`
- All data files are **tab-separated** — always use `sep='\t'` when reading/writing
- Keep logic in `.py` modules under `SUBMISSION/code/business_entity_resolution/src/`; use thin Jupyter notebooks for exploration only

### Commit & Branch Conventions

- See [`context/git-workflow.md`](context/git-workflow.md) for full details
- Branch naming: `feat/<name>-<topic>`, `fix/<name>-<topic>`, `exp/<name>-<topic>`
- Squash-merge to `main` preferred
- **Rule: Log an experiment before you merge it.** Every approach must have a row in [`context/experiment-log.md`](context/experiment-log.md) before its branch is merged to `main`.

### Data Handling

- **Never commit raw data or large model files.** The `Data/` folder is in `.gitignore`.
- Model weights, pickled objects, and other large artifacts must not be committed (blocked by `.gitignore`).
- Submission output files in `SUBMISSION/output/` **are tracked** — push them so teammates can pull the latest results.
- Each teammate stores the dataset locally; see [`context/environment-setup.md`](context/environment-setup.md) for expected paths.

---

## Critical Notes Log

> Dated log of gotchas, decisions, and mid-event changes. **Newest entry on top.**

### 2026-09-25 — Repo restructured to match submission package layout

**By:** Member 1

- Source code now lives at `SUBMISSION/code/business_entity_resolution/src/` (matches the official submission zip structure).
- Old top-level `src/` removed (was empty).
- `SUBMISSION/Documentation_template.md` added at repo root (official template for methodology write-up).
- `.gitignore` relaxed: `SUBMISSION/output/` and `.tsv` submission files are now tracked in git.
- Added `scripts/package_submission.py` to generate the submission zip.

### 2026-09-25 — Project initialized

**By:** Member 1

- Documentation system stood up: `project.md`, `agents.md`, `context/` folder with 8 topic files.
- Problem statement released: Business Entity Resolution, F₀.₅ metric.
- Key risk identified: France is zero-shot (test only, no training data) — ~15% of test S1 entities.

---

## Grounding Rules for AI Agents

> **If you are an AI agent, read this section carefully.**

1. **Read `project.md` first** — always. Then consult the Master Index above to find the specific file for your task.
2. **Never assume.** If information isn't in the docs, say "not in the docs" — do not guess or infer.
3. **Check the Current State Snapshot** before claiming any result is an improvement.
4. **Check [`context/experiment-log.md`](context/experiment-log.md)** before starting an experiment — someone may have already tried your approach.
5. **Check [`context/submission-log.md`](context/submission-log.md)** before making a submission — never submit something worse than our current best.
6. **Never edit existing rows** in experiment-log.md or submission-log.md — append only.
7. **Follow the versioning rule below** for any file you edit.
8. **For your full operating manual**, see [`agents.md`](agents.md).

---

## Versioning Policy

> **This is a project-wide, non-optional rule for every `.md` file in this repo.**

### The Rule

Every markdown file starts with:

```
> **Version:** vX.Y | **Last updated:** YYYY-MM-DD HH:MM IST | **By:** <name>
```

Every markdown file ends with a `## Changelog` section (newest entry on top):

```markdown
## Changelog

| Version | Date | By | Summary |
|---------|------|----|---------|
| vX.Y | YYYY-MM-DD | Name | What changed |
```

### When to Bump

- **Any content edit** → bump the minor version (v1.0 → v1.1) and add a changelog row.
- **Major structural changes** (new sections, reorganization) → bump the major version (v1.1 → v2.0).
- **Typo fixes or formatting only** → still bump the minor version. No exceptions.

### Why

With 4 people and multiple AI agents editing docs during a 72-hour hackathon, we need to know at a glance: who changed what, when, and whether we're looking at the latest version.

---

## Changelog

| Version | Date | By | Summary |
|---------|------|----|---------|
| v1.4 | 2026-09-25 | Antigravity | Added skills/ and past-challenges-reference.md to Master Index. Fixed REPO path references to SUBMISSION. |
| v1.1 | 2026-09-25 | Member 1 | Restructured repo to match submission package layout; updated master index, .gitignore, code paths |
| v1.0 | 2026-09-25 | Member 1 | Initial skeleton created |
