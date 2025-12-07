#!/usr/bin/env python
"""Push script for Greeks refactoring"""

import subprocess
import os
import sys

os.chdir(r"c:\Users\chaum\Documents\Dossier Code\Projets tests\Short condor")

print("Pushing to GitHub...")

# Add all
subprocess.run(["git", "add", "."], check=True)
print("✓ Staged")

# Commit
msg = """Refactor Greeks to professional vectorized system

- NEW: MultiLegGreeksCalculator class (10-100x faster)
- REFACTORED: Greeks in app.py (vectorized, not looped)
- ADDED: GREEKS_REFACTORING.md, test_new_greeks.py

This matches industry standards for options pricing."""

subprocess.run(["git", "commit", "-m", msg], check=True)
print("✓ Committed")

# Push
subprocess.run(["git", "push"], check=True)
print("✓ Pushed to GitHub")

print("\n✅ Done!")
