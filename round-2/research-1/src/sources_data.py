#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Source records (1-60). Base records live in sources_p1/p2/p3; if
sources_repaired.json exists (produced by repair3.py with verifier-exact
passages), it takes precedence. All URLs accessed 2026-09-19."""
import json
import os

_BASE = os.path.dirname(os.path.abspath(__file__))
_REPAIRED = os.path.join(_BASE, "sources_repaired.json")

if os.path.exists(_REPAIRED):
    with open(_REPAIRED, encoding="utf-8") as _f:
        SOURCES = json.load(_f)
else:
    from sources_p1 import PART1
    from sources_p2 import PART2
    from sources_p3 import PART3
    SOURCES = PART1 + PART2 + PART3

assert [s["index"] for s in SOURCES] == list(range(1, len(SOURCES) + 1)), "index continuity broken"

if __name__ == "__main__":
    print("total sources:", len(SOURCES))
    print("source of truth:", "sources_repaired.json" if os.path.exists(_REPAIRED) else "parts")
    bad = [s["index"] for s in SOURCES if not s.get("url") or not s.get("title") or not s.get("summary")]
    print("records missing url/title/summary:", bad)