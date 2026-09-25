---
name: validate-submission
description: >-
  Validates a submission payload before zipping it.
  Triggers when asked to validate, check, or test a submission.
---

> **Version:** v1.0 | **Last updated:** 2026-09-26 02:07 IST | **By:** Codex

# Validate Submission Skill

Before creating a submission zip or finishing an inference task, you must validate the output format.

1. **Locate the script**: The validation script is located at `data/6ab10eb3b23ba_student_resource/student_resource/utils/validate_submission.py`.
2. **Run validation**: Execute the script against the output files.
   ```bash
   python data/6ab10eb3b23ba_student_resource/student_resource/utils/validate_submission.py \
       --matching SUBMISSION/output/matching_results.tsv \
       --candidate SUBMISSION/output/candidate_pairs.tsv \
       --test-dir data/6ab10eb3b23ba_student_resource/student_resource/dataset/test
   ```
3. **Handle errors**: If the script prints anything other than `PASS` (exit 0), you must fix the formatting errors in the output files and re-run the validation until it passes. Do not proceed with submission packaging until validation passes.

## Changelog

| Version | Date | By | Summary |
|---------|------|----|---------|
| v1.0 | 2026-09-26 | Codex | Added project version metadata and corrected validation paths to the active lowercase data directory. |
