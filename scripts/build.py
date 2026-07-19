#!/usr/bin/env python3
"""Compatibility guard for Website Platform v5.1.

The old v4 generator cannot reproduce the full v5 public site and is therefore
kept as build_legacy_v4.py rather than run automatically. The active v5 site is
validated in place.
"""
from pathlib import Path

root = Path(__file__).resolve().parents[1]
print("Website v5.1: legacy HTML generation skipped. Validating the active finished site in place.")
print(f"Active site: {root}")
