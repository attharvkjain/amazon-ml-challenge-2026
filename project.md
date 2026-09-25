> **Version:** v3.2 | **Last updated:** 2026-09-26 02:50 IST | **By:** Codex

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
| **Hackathon Window** | See official window in [`context/problem-and-data.md`](context/problem-and-data.md) |
| **Submission Format** | `matching_results.tsv` leaderboard payload; see official requirements and submission history for packaging details |
| **Constraints** | See [`context/problem-and-data.md`](context/problem-and-data.md) |

### Team

> Team roster, roles, contacts, and availability: see [`context/team-roles.md`](context/team-roles.md).

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
| [`skills/`](skills/) | Folder | Canonical tracked, provider-agnostic Agent Skills folder; provider directories mirror the canonical files for agent discovery; maintain skills in `skills/` |
| [`context/eda-findings.md`](context/eda-findings.md) | File | Dated log of EDA insights |
| [`context/environment-setup.md`](context/environment-setup.md) | File | Local environment reproduction steps per teammate |
| [`context/experiment-log.md`](context/experiment-log.md) | File | **APPEND-ONLY** — every approach tried, params, CV score, commit |
| [`context/submission-log.md`](context/submission-log.md) | File | **APPEND-ONLY** — every leaderboard submission with public score |
| [`context/challenges_faced.md`](context/challenges_faced.md) | File | Log of pitfalls, errors, crashes, and performance bottlenecks encountered and resolved |
| [`context/git-workflow.md`](context/git-workflow.md) | File | Branch naming, PR/merge rules, notebook conflict prevention |
| [`context/team-roles.md`](context/team-roles.md) | File | Team member roles, focus areas, availability during 72h |
| [`context/writeup-draft.md`](context/writeup-draft.md) | File | Living draft of the methodology document (internal WIP) |
| [`context/umbrella-research.md`](context/umbrella-research.md) | File | Consolidated umbrella research findings on paradigms and optimizations |
| [`context/architecture.md`](context/architecture.md) | File | Pipeline architecture design — repo layout, data flow, validation, model shortlist, risks |
| [`context/reconciliation-log.md`](context/reconciliation-log.md) | File | **APPEND-ONLY** — recurring documentation reconciliation runs and open findings |
| [`SUBMISSION/code/business_entity_resolution/src/`](SUBMISSION/code/business_entity_resolution/src/) | Folder | **All pipeline source code** — submission package location |
| [`SUBMISSION/code/business_entity_resolution/README.md`](SUBMISSION/code/business_entity_resolution/README.md) | File | Reproduction instructions (ships in submission zip) |
| [`SUBMISSION/code/business_entity_resolution/requirements.txt`](SUBMISSION/code/business_entity_resolution/requirements.txt) | File | Dependency list (ships in submission zip) |
| [`SUBMISSION/output/`](SUBMISSION/output/) | Folder | Tracked leaderboard matching files and local ignored candidate audit output |
| [`scripts/package_submission.py`](scripts/package_submission.py) | File | Creates the submission zip from repo contents |
| [`analysis and research/`](analysis%20and%20research/) | Folder | Pre-competition research and winner playbook |
| [`analysis and research/amazon_ml_challenge_2026_analysis.md`](analysis%20and%20research/amazon_ml_challenge_2026_analysis.md) | File | Competition analysis; canonical dataset facts link to `context/problem-and-data.md` |
| [`analysis and research/mit-initial-Ditto Arcnitecture research-ChatGPT-Business Entity Matching-20260925-1227.md`](analysis%20and%20research/mit-initial-Ditto%20Arcnitecture%20research-ChatGPT-Business%20Entity%20Matching-20260925-1227.md) | File | Initial matching-architecture research notes |
| [`analysis and research/amazon_ml_challenge_winner_playbook.xlsx`](analysis%20and%20research/amazon_ml_challenge_winner_playbook.xlsx) | File | Prior challenge winner playbook |
| [`analysis and research/research_sources.xlsx`](analysis%20and%20research/research_sources.xlsx) | File | Cited sources for the umbrella research |
| [`data/`](data/) | Folder | Local raw dataset and official student resource — **DO NOT commit** |
| [`SUBMISSION/output/history/`](SUBMISSION/output/history/) | Folder | Archived leaderboard matching TSVs, named by submission-log number |
| [`amazon docs given/`](amazon%20docs%20given/) | Folder | Official problem statement & guidelines PDFs |
| [`notebooks/`](notebooks/) | Folder | Jupyter notebooks (clear outputs before committing) |
| [`.gitignore`](.gitignore) | File | Git ignore rules — keeps raw data & large files out of version control |

---

## Current State Snapshot

> **Anti-regression anchor.** Before merging any result, check that it actually beats the current best. Update this section whenever a new best is achieved.

| Metric | Value | Details |
|--------|-------|---------|
| **Best Local Validation Score (F₀.₅)** | 0.9699 | Baseline validation during training; threshold 0.940 |
| **Best Public LB Score** | See [`context/submission-log.md`](context/submission-log.md) | Canonical submission history |
| **Approach** | See [`context/architecture.md`](context/architecture.md) | Implemented baseline |
| **Commit Hash** | `HEAD` | — |
| **Produced By** | Antigravity | — |
| **Date** | 2026-09-26 | — |

> See [`context/experiment-log.md`](context/experiment-log.md) for experiment history and [`context/submission-log.md`](context/submission-log.md) for canonical submission scores.

---

## Rules & Guidelines

### Coding Conventions

- Python 3.10+
- Type hints encouraged
- f-strings over `.format()`
- All data files are **tab-separated** — always use `sep='\t'` when reading/writing
- Keep logic in `.py` modules under `SUBMISSION/code/business_entity_resolution/src/`; use thin Jupyter notebooks for exploration only
- **Maximize Hardware Utilization**: Given the 72-hour time crunch, ensure maximum practical utilization of CPU resources. Use multiprocessing/multithreading for heavy pipeline stages to saturate the CPU. Avoid single-threaded bottlenecks.
- **Proactive Bottleneck Resolution**: If any process is taking an unreasonably long time, stop it immediately, reconfigure/improve the code (e.g. swap `iterrows` for `itertuples`, use `loky` backend), and restart. Going forward, do a full pass of the code for performance bottlenecks before execution to ensure the fastest possible runtime given the implementation goals.
- **Pipeline Caching / Checkpointing**: Always save intermediate assets (models, features, blocked candidate pairs, cleaned data) using `pickle` or `joblib` so that if the pipeline fails, work is not lost and can be resumed from the nearest save point to save time.

### Commit & Branch Conventions

- See [`context/git-workflow.md`](context/git-workflow.md) for full details
- Branch naming: `feat/<name>-<topic>`, `fix/<name>-<topic>`, `exp/<name>-<topic>`, `reconcile/<YYYY-MM-DD-HHmm>`
- Squash-merge to `main` preferred
- **Rule: Log an experiment before you merge it.** Every approach must have a row in [`context/experiment-log.md`](context/experiment-log.md) before its branch is merged to `main`.

### Data Handling

- **Never commit raw data or large model files.** The lowercase `data/` folder is in `.gitignore`.
- The misspelled `miscelleaneous/` folder contains local-only historical drafts and is ignored in Git.
- Model weights, pickled objects, and other large artifacts must not be committed (blocked by `.gitignore`).
- Leaderboard `matching_results.tsv` files in `SUBMISSION/output/` and its `history/` folder are tracked. The very large `candidate_pairs.tsv`, model threshold, and caches are local generated artifacts and are ignored.
- Each teammate stores the dataset locally; see [`context/environment-setup.md`](context/environment-setup.md) for expected paths.

---

## Critical Notes Log

> Dated log of gotchas, decisions, and mid-event changes. **Newest entry on top.**

### 2026-09-26 — External Review Audit and Single Source of Truth Enforcement

**By:** Antigravity

- Added a strict "Single Source of Truth Rule" to eliminate conflicting duplicate documentation.
- Identified that there is currently **no off-machine backup plan** for expensive intermediate pickles. Local caching is the only failsafe.
- The earlier all-singletons validation reminder was superseded by the submissions recorded in [`context/submission-log.md`](context/submission-log.md).
- Verified test S1 row count is exactly 1,732,544.
- Verified random seeds (RANDOM_STATE=42) are properly used across splits and training.

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

## Single Source of Truth Rule

> **This is a project-wide, non-optional rule.**
Every discrete fact, decision, or number lives in exactly ONE file. Any other file that needs it must link to the canonical location instead of restating it. This prevents documentation drift and conflicting values across the repository.

---

## Reconciliation Practice

Run the `reconcile-project` skill:

- After every leaderboard submission.
- After a major pipeline or architecture revision is accepted.
- Before final packaging or handoff.
- When official challenge rules, dataset paths, or submission requirements change.

The audit is presented before documentation edits. DOC-ONLY fixes may be committed on a dedicated reconciliation branch. CODE-ADJACENT findings require item-specific human approval before implementation. Record every run and remaining item in [`context/reconciliation-log.md`](context/reconciliation-log.md).

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

For Agent Skill `SKILL.md` files, valid YAML frontmatter must remain the first content in the file. Put the standard version line immediately after the closing frontmatter fence and keep the changelog at the end.

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
| v3.2 | 2026-09-26 | Codex | Recorded the local-only miscellaneous folder policy and removed its archived draft from the tracked-file index. |
| v3.1 | 2026-09-26 | Codex | Clarified that provider skill folders are discovery mirrors of the canonical `skills/` directory. |
| v3.0 | 2026-09-26 | Codex | Reconciled tracked paths, score references, output archive policy, and added recurring reconciliation practice and skill index. |
| v2.1 | 2026-09-26 | Antigravity | Updated Current State Snapshot with 0.697 LB score and full pipeline completion |
| v2.0 | 2026-09-26 | Antigravity | Added Single Source of Truth Rule, updated Agent Skills path, and added audit summary to Critical Notes. |
| v1.8 | 2026-09-25 | Antigravity | Added context/challenges_faced.md to Master Index |
| v1.7 | 2026-09-25 | Antigravity | Added Pipeline Caching / Checkpointing rule to save intermediate progress |
| v1.6 | 2026-09-25 | Antigravity | Added Proactive Bottleneck Resolution rule to Coding Conventions |
| v1.5 | 2026-09-25 | Antigravity | Added Maximize Hardware Utilization rule to Coding Conventions |
| v1.4 | 2026-09-25 | Antigravity | Added skills/ and past-challenges-reference.md to Master Index. Fixed REPO path references to SUBMISSION. |
| v1.3 | 2026-09-25 | Antigravity | Added context/architecture.md to Master Index |
| v1.2 | 2026-09-25 | Antigravity | Added context/umbrella-research.md and Analysis and Research/research_sources.xlsx to Master Index |
| v1.1 | 2026-09-25 | Member 1 | Restructured repo to match submission package layout; updated master index, .gitignore, code paths |
| v1.0 | 2026-09-25 | Member 1 | Initial skeleton created |
