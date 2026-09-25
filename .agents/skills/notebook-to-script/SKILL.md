---
name: notebook-to-script
description: >-
  Extracts reusable logic from a Jupyter notebook to a python script.
  Triggers when you need to modularize code or before committing a notebook.
---
> **Version:** v1.0 | **Last updated:** 2026-09-26 02:27 IST | **By:** Codex


# Notebook to Script Skill

Jupyter notebooks should be thin and used only for exploration. When a notebook contains reusable pipeline logic (data loading, preprocessing, modeling), extract it.

1. **Extract logic**: Move the core functions and classes from the `.ipynb` file into the appropriate `.py` module under `SUBMISSION/code/business_entity_resolution/src/`.
2. **Refactor notebook**: Update the notebook to import the logic from the newly created or updated `.py` module.
3. **Clear outputs**: Always clear all cell outputs and execution counts in the `.ipynb` file before committing it to version control, to prevent bloated diffs.
4. **Test**: Ensure the refactored script and notebook still run successfully.


## Changelog

| Version | Date | By | Summary |
|---------|------|----|---------|
| v1.0 | 2026-09-26 | Codex | Added version metadata and changelog per the project documentation policy. |
