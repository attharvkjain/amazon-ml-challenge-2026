---
name: reconcile-project
description: Reconcile project documentation against the live repository after milestones, submissions, architecture changes, or before packaging. Reports discrepancies, applies approved documentation-only fixes, and gates behavior-affecting changes on item-specific human approval.
---
> **Version:** v1.0 | **Last updated:** 2026-09-26 02:30 IST | **By:** Codex

# Reconcile Project

Use this skill for a recurring repository reconciliation run. Follow the live repository state over prior notes or memory. Read [`project.md`](../../project.md) first, then [`agents.md`](../../agents.md) and every file in `context/` in full; inspect append-only logs without editing their existing rows.

## Audit and report

1. Inventory tracked and relevant local files. Verify every path in the project Master Index and identify relevant files present but not indexed.
2. Check duplicated facts, paths, constants, constraints, score provenance, skill locations, current implementation, stale decisions, and unresolved questions against source files, configuration, diagnostics, and the current tree. Distinguish historical recommendations from implemented behavior.
3. Present a Reconciliation Report before editing. Put every finding in exactly one category:
   - **DOC-ONLY:** documentation-only correction that cannot change runtime behavior.
   - **CODE-ADJACENT:** involves pipeline code, configuration, or behavior, or is ambiguous. Propose a specific fix and reason. Do not make the change until the human confirms that item.
4. Never guess missing facts. Preserve open questions as open. Do not edit `context/experiment-log.md` or `context/submission-log.md` rows; both are append-only.

## Apply approved work

1. After presenting the report and receiving the required approvals, create a dedicated `reconcile/YYYY-MM-DD-HHmm` branch. Never edit directly on `main`.
2. Apply approved DOC-ONLY fixes. Apply a CODE-ADJACENT fix only after explicit item-specific approval. Keep each change small, group commits by topic, and stage explicit paths rather than all workspace files.
3. Preserve unrelated local and untracked artifacts. Never delete content unless the reconciliation log records what was removed and why.
4. Follow the project's Markdown versioning policy for every Markdown edit. Preserve YAML frontmatter as the first content in Agent Skills and put the version line directly after it.

## Record and formalize

1. Create `context/reconciliation-log.md` if absent, then append one entry describing scope, documentation fixes, confirmed changes, remaining findings, and branch/commit references. Do not rewrite prior entries.
2. Update `project.md` and `agents.md` when this practice or its triggers change. Use these concrete triggers: after each leaderboard submission, after an accepted major pipeline/architecture revision, before final packaging or handoff, and when official rules or data paths change.
3. Add the log to the project Master Index. Keep facts in one canonical location and link to them elsewhere.
4. Report the final changes, commits, verification performed, and any unresolved CODE-ADJACENT items. Stop for the human on unapproved behavior changes.

## Changelog

| Version | Date | By | Summary |
|---------|------|----|---------|
| v1.0 | 2026-09-26 | Codex | Created the recurring repository reconciliation procedure. |
