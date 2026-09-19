#!/usr/bin/env python3
"""data.py - canonical entry point for the safety-screening prompt platform.

Builds the complete exp_sel_data_out-conformant data product from the source
files staged in temp/datasets/ (see scripts/build_platform.py for the single
deterministic construction implementation) and writes:

  full_data_out.json     - all rows (schema exp_sel_data_out)
  mini_data_out.json     - first 3 examples (see aii-json format step)
  preview_data_out.json  - first 3 examples, strings truncated (aii-json)

The 6 chosen datasets (7 prompt sections; contrast is split into a base pair
view and a nested K-subset membership view):

  refusal_120          120 HarmBench-style refusal targets      (seed 42)
  xstest               450 XSTest-EN prompts (250 safe / 200 unsafe labels)
  jailbreak             60 rows = 30 plain + 30 wrapped pairs    (seed 123)
  contrast_base         32 rows = 16 harmful/harmless pairs      (seed 7)
  contrast_membership  186 rows = nested K-subsets x {0,1,2} x K in {1,2,4,8,16}
  canonical              5 fixed hand-written harmful prompts
  benign                75 safe prompts (40 real dolly-15k + 35 templates)

Usage:
  uv run data.py          # or: .venv/bin/python data.py
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))

from build_platform import main as build_platform_main  # noqa: E402  (single deterministic builder)
from build_platform import ART  # noqa: E402


def main() -> None:
    # 1) deterministic construction (same seeds/sources as the artifacts/ build)
    build_platform_main()

    # 2) stage the root-level deliverable (byte-identical copy of the built product)
    src = ART / "data_out.json"
    out = ROOT / "full_data_out.json"
    shutil.copyfile(src, out)
    print(f"WROTE {out}: {out.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()