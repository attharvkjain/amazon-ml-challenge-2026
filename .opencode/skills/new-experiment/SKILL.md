---
name: new-experiment
description: >-
  Scaffolds a new experiment branch from the current best config.
  Triggers when starting a new modeling approach or experiment.
---

# New Experiment Skill

When starting a new experiment, you must isolate it and base it on the current best baseline.

1. **Check current best**: Read `project.md`'s "Current State Snapshot" to identify the current best approach and its commit hash.
2. **Branch out**: Create and checkout a new git branch named `exp/<your-name>-<experiment-topic>` (e.g., `exp/member1-tfidf-baseline`).
3. **Scaffold config**: Ensure the codebase configuration matches the current best baseline, so you are only testing the new variable.
4. **Wire logging**: Ensure your training script is pre-wired to output metrics that can be easily logged. Remind yourself to use the `log-experiment` skill when the run finishes.
