# Amazon ML challenge project documentation structure

**Created:** 9/25/2026 2:10:39  
**Updated:** 9/25/2026 13:02:49  
**Exported:** 9/25/2026 13:06:38  
**Link:** [https://claude.ai/chat/8e3ba5a0-0a6a-4d1b-aea8-9181ade928f0](https://claude.ai/chat/8e3ba5a0-0a6a-4d1b-aea8-9181ade928f0)  

## Assistant:

> 9/25/2026 13:02:49

> Structuring detailed content and prompts for each phase.
>
> - Structuring detailed content and prompts for each phase.
> - **Done**

Yes — add phases. Two phases (design → build) is too coarse for an ML competition; the biggest risk in a 72-hour hackathon isn't messy code, it's *having nothing submittable if you run out of time mid-build*. So insert a baseline phase between design and full build, and a few short ones at the tail.

## Recommended full workflow

| # | Phase | Produces | New chat? |
|---|---|---|---|
| 0 | Setup & Docs | project.md, agents.md, context/ | ✅ done |
| 1 | Research | context/problem-and-data.md, eda-findings.md | ✅ done |
| 2 | **Architecture & Design** | context/architecture.md (plan only, no code) | 👉 now, fresh chat |
| 3 | **Baseline Build** | dumbest possible end-to-end pipeline → one valid leaderboard submission | fresh chat |
| 4 | **Core Build** | real data/feature/model modules per architecture.md | fresh chat, or per-teammate chats |
| 5 | Iterative Experimentation | tuned models, all runs in experiment-log.md | can reuse chat 4, or fresh if it gets long |
| 6 | Ensembling / Model Selection | final model choice, logged best score | fresh chat near deadline |
| 7 | Final Submission Packaging | verified submission file matching required format | fresh chat |
| 8 | Write-up Finalization | context/writeup-draft.md → final 1-2 pager | can run in parallel with 6-7 |
| 9 | Buffer / Smoke Test | clean-machine re-run of full pipeline before deadline | fresh chat |

Why phase 3 exists: in a scored hackathon, an ugly submission beats an elegant one that never gets zipped up. Get *something* on the leaderboard in the first few hours, then spend the rest of the time improving on top of a working pipeline — you're never at risk of a zero.

Start a **new chat per phase** (or per teammate within phase 4) on purpose — long chats drift and start hallucinating repo state. Your project.md/context/ system exists precisely so a brand-new chat can bootstrap itself cold instead of needing scrollback.

## Prompt to use right now (Phase 2 — Architecture & Design)

```
New session. Before doing anything else, read project.md, agents.md, and
context/problem-and-data.md and context/eda-findings.md in full. Do not
write or scaffold any implementation code in this phase — this phase
produces a design document only, to be reviewed by the team before we build.

Task: produce context/architecture.md covering:
1. SUBMISSION/code layout — proposed src/ module breakdown (data loading,
   cleaning, feature engineering, training, inference, submission
   generation) and where notebooks vs scripts belong
2. Data pipeline design — ingestion → cleaning → feature engineering steps,
   based on what's actually in context/problem-and-data.md and
   context/eda-findings.md (don't invent data characteristics not in those
   files — flag anything you're unsure about instead)
3. Validation strategy — CV scheme appropriate to this problem/metric,
   chosen specifically to avoid overfitting to the public leaderboard
4. Model shortlist — 2-4 candidate approaches with rationale, given the
   eval metric, data size/type, and our ~72hr time budget (favor
   fast-to-iterate models first, expensive ones only if time allows)
5. Experiment tracking hook — how each training run will get logged into
   context/experiment-log.md (ideally a helper function, not manual)
6. Risk list — things most likely to break or eat time (data leakage,
   environment mismatch across our 4 machines, format mismatches on
   submission, etc.)

Give this a version header per our versioning rule, and update project.md's
master index and current-state snapshot to point to it. Ask me before
assuming anything not already documented in context/.
```

## Prompt for Phase 3 — Baseline Build (use once architecture.md is approved)

```
New session. Read project.md, agents.md, context/architecture.md, and
context/git-workflow.md first.

We are now in Baseline Build phase. Goal: the simplest possible end-to-end
pipeline that produces one valid, correctly-formatted submission file —
even with a mediocre score. Do not implement the full feature set or model
shortlist from architecture.md yet; pick the single fastest path through
data → minimal features → simplest model → prediction → submission file.

- Follow the branch/commit rules in context/git-workflow.md
- Log this run in context/experiment-log.md with its score
- Log the submission in context/submission-log.md
- Update project.md's current-state snapshot with this as our current best
- Confirm the submission file matches the competition's required format
  exactly before declaring this phase done
```

## Prompt for Phase 4 — Core Build (use after baseline is on the leaderboard)

```
New session. Read project.md, agents.md, context/architecture.md,
context/git-workflow.md, and context/experiment-log.md (for current best)
first.

We are now in Core Build phase, implementing the full pipeline from
architecture.md on top of the working baseline. Build one module at a time
in the order specified in architecture.md, each as a small, reviewable
commit. Add a minimal sanity check per module (shape/type checks, no
formal test suite needed given time constraints). Never deviate from
architecture.md without flagging the change first. After any run that
changes the score, log it in context/experiment-log.md and update
project.md's current-state snapshot only if it beats the existing best —
never overwrite a better logged result with a worse one.
```

Phases 5-8 reuse the same bootstrap line (*"read project.md + relevant context files first"*) with a one-line task swapped in — happy to write those out too once you're actually there, since they'll depend on what the baseline score and architecture review turn up.

Powered by Claude Exporter (https://www.ai-chat-exporter.net)
