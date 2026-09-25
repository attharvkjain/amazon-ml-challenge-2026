---
name: eda-report
description: >-
  Generates and logs an EDA report.
  Triggers when you finish data exploration or are asked to log EDA findings.
---
> **Version:** v1.0 | **Last updated:** 2026-09-26 02:27 IST | **By:** Codex


# EDA Report Skill

When you uncover new data quirks, noise patterns, or statistical insights about the dataset, log them.

1. **Format findings**: Write a concise, bulleted summary of the findings, including any relevant row counts, null percentages, or specific noise examples.
2. **Append to log**: Append this report as a dated entry to `context/eda-findings.md`.
3. **Update Data Quirks**: If the finding is a critical trap or rule (e.g. zero-shot countries, delimiter issues), also append it to the "Data Quirks" section in `context/problem-and-data.md`.
4. **Version Bump**: Bump the version and add a changelog entry in the modified markdown files.


## Changelog

| Version | Date | By | Summary |
|---------|------|----|---------|
| v1.0 | 2026-09-26 | Codex | Added version metadata and changelog per the project documentation policy. |
