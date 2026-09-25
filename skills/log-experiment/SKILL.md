---
name: log-experiment
description: >-
  Logs a new experiment to context/experiment-log.md.
  Triggers when you finish a training run or are asked to log an experiment.
---

# Log Experiment Skill

When the user asks you to log an experiment, or when you complete a training run, you must update the experiment log.

1. **Locate the log**: The log is at `context/experiment-log.md`.
2. **Append only**: Never edit or delete existing rows. Add a new row to the bottom of the table.
3. **Capture details**: The row must include the date, approach/parameters, local CV score, commit hash (if applicable), and who ran it (e.g. the current agent or team member).
4. **Update Current Best**: Check `project.md`'s "Current State Snapshot". If the new F₀.₅ score is strictly better than the current best, update `project.md`'s snapshot with the new details. If it's not better, leave `project.md` alone.
5. **Version Bump**: Always bump the version and add a changelog entry in both `context/experiment-log.md` and `project.md` (if modified).
