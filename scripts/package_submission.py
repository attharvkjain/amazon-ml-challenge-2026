#!/usr/bin/env python3
"""
Package the submission zip for Amazon ML Challenge 2026.

Usage:
    python scripts/package_submission.py [--team-name TEAM_NAME]

Creates: <team_name>_submission.zip containing:
    output/matching_results.tsv
    output/candidate_pairs.tsv
    code/business_entity_resolution/  (src/, README.md, requirements.txt)
    Documentation_template.md
"""

import argparse
import os
import sys
import zipfile
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
REPO_DIR = WORKSPACE_ROOT / "REPO"

REQUIRED_FILES = [
    "output/matching_results.tsv",
    "output/candidate_pairs.tsv",
    "code/business_entity_resolution/README.md",
    "code/business_entity_resolution/requirements.txt",
    "Documentation_template.md",
]

SRC_DIR = "code/business_entity_resolution/src"

# Files to skip inside the zip
SKIP_NAMES = {".gitkeep", "__pycache__", ".DS_Store", "Thumbs.db"}


def package(team_name: str) -> None:
    zip_name = f"{team_name}_submission.zip"
    zip_path = WORKSPACE_ROOT / zip_name

    # ── Check required files ──
    missing = [f for f in REQUIRED_FILES if not (REPO_DIR / f).exists()]

    # Check that src/ has at least one .py file
    src_path = REPO_DIR / SRC_DIR
    py_files = list(src_path.rglob("*.py")) if src_path.exists() else []
    if not py_files:
        missing.append(f"{SRC_DIR}/*.py (no Python files found)")

    if missing:
        print("ERROR - missing required files:")
        for m in missing:
            print(f"  x {m}")
        print("\nFix these before packaging.")
        sys.exit(1)

    # ── Build the zip ──
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Add required files
        for f in REQUIRED_FILES:
            zf.write(REPO_DIR / f, f)

        # Add all files under code/business_entity_resolution/src/
        for file_path in src_path.rglob("*"):
            if file_path.is_file() and file_path.name not in SKIP_NAMES:
                arcname = str(file_path.relative_to(REPO_DIR))
                zf.write(file_path, arcname)

    size_kb = zip_path.stat().st_size / 1024
    print(f"[OK] Created {zip_name} ({size_kb:.1f} KB)")
    print(f"\nContents:")
    with zipfile.ZipFile(zip_path, "r") as zf:
        for name in sorted(zf.namelist()):
            info = zf.getinfo(name)
            size_str = f"{info.file_size / 1024:.1f} KB" if info.file_size > 0 else "dir"
            print(f"  {name}  ({size_str})")

    print(f"\n[OK] Ready to submit: {zip_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Package the Amazon ML Challenge 2026 submission zip."
    )
    parser.add_argument(
        "--team-name",
        default="team",
        help="Team name for the zip filename (default: 'team')",
    )
    args = parser.parse_args()
    package(args.team_name)
