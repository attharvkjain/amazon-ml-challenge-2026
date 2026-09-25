> **Version:** v2.0 | **Last updated:** 2026-09-26 00:25 IST | **By:** Antigravity

# Git Workflow

**Standalone primer:** Amazon ML Challenge 2026 — 4-person team working on a Business Entity Resolution pipeline during a 72-hour hackathon, syncing through GitHub (`github.com/attharvkjain/amazon-ml-challenge-2026`). This file defines branch naming, merge rules, and strategies to avoid conflicts (especially with Jupyter notebooks).

---

## Branch Naming

Use prefixes to signal intent:

| Prefix | Use For | Example |
|--------|---------|---------|
| `feat/<name>-<topic>` | New features or pipeline components | `feat/member1-blocking` |
| `fix/<name>-<topic>` | Bug fixes | `fix/member2-tsv-parsing` |
| `exp/<name>-<topic>` | Experiments (may or may not merge) | `exp/member3-tfidf-threshold` |
| `doc/<topic>` | Documentation updates | `doc/eda-findings` |

- `<name>` = your member name or handle (keeps ownership clear)
- `<topic>` = short description of what the branch does

---

## Workflow Rules

1. **Work on feature branches.** Never push directly to `main`.
2. **PR to `main`** when your work is ready. Describe what changed and link relevant experiment-log entries.
3. **At least 1 review before merge** — but during crunch time (last 6 hours), self-merge is allowed with a comment explaining why.
4. **Squash-merge preferred** — keeps `main` history clean with one commit per logical change.
5. **Log before merge:** Every experiment must have a row in [`context/experiment-log.md`](experiment-log.md) before its branch is merged to `main`.
6. **Pull before push:** Always `git pull --rebase origin main` before pushing your branch to reduce merge conflicts.

---

## Commit Message Format

```
[category] short description

Examples:
[feat] add TF-IDF blocking on name + address
[fix] correct TSV parsing separator
[exp] run XGBoost with threshold=0.7
[doc] update EDA findings with null analysis
[data] add preprocessing script for Indic transliteration
```

---

## Avoiding Notebook Merge Conflicts

Jupyter notebooks are notoriously merge-unfriendly. Follow these rules:

### Option A: Clear outputs before commit (preferred)

```bash
# Clear all outputs from a notebook
jupyter nbconvert --clear-output --inplace notebooks/my_notebook.ipynb

# Then commit
git add notebooks/my_notebook.ipynb
git commit -m "[exp] run baseline blocking experiment"
```

### Option B: Keep logic in `.py` modules

- Put reusable logic in `src/` as Python modules
- Use thin notebooks that import from `src/` for exploration and visualization
- This makes the actual code diff-friendly and testable

### Option C: Avoid parallel edits

- If two people need to work on the same notebook, coordinate — don't both edit it at the same time
- Consider duplicating the notebook temporarily (`notebook_v2_member2.ipynb`) and merging results later

---

## Data Rules

- **Never commit** raw data, `.tsv` files, `.csv` files, model weights, or large binaries
- The `.gitignore` is configured to exclude these — don't override it
- If you need to share a small derived dataset (< 1MB), put it in a clearly named folder and add a note

---

## Emergency Procedures (Last 6 Hours)

During the final push:

- **Hard Code Freeze at 5:00 PM IST on Day 3 (4 hours before deadline).** No more experimental merges or new features are allowed. This block of time is exclusively reserved for full-scale model training and inference on the test set.
- Self-merge is allowed with a PR comment
- Skip squash if faster — but write clear commit messages
- Prioritize getting the best `matching_results.tsv` submitted over clean git history
- **Always validate** before submitting: `python utils/validate_submission.py ...`

---

## Changelog

| Version | Date | By | Summary |
|---------|------|----|---------|
| v2.0 | 2026-09-26 | Antigravity | Added hard code-freeze policy for the final 4 hours to reserve time for full-scale training and inference. |
| v1.0 | 2026-09-25 | Member 1 | Initial skeleton created |
