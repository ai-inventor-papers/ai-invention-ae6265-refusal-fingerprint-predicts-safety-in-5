#!/usr/bin/env python3
"""Backfill metadata_parameter_count from safetensors index metadata (real HF numbers)."""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from huggingface_hub import HfApi

ROOT = Path(__file__).resolve().parent.parent
api = HfApi(token=os.environ.get("HF_TOKEN") or None)

REG_PATH = ROOT / "artifacts/registry.json"
reg = json.loads(REG_PATH.read_text())
examples = reg["datasets"][0]["examples"]

# 0) if already fully populated, skip the network pass
if all(r.get("metadata_parameter_count") is not None
       for r in examples if r.get("metadata_weight_format") != "spec"):
    print("all rows already have parameter_count; skipping fetch")
    totals = {}
else:
    # 1) fetch live totals per unique repo
    unique = sorted({r["metadata_repo_id"] for r in examples
                     if r.get("metadata_weight_format") != "spec"})
    totals: dict[str, int | None] = {}
    for repo in unique:
        try:
            info = api.model_info(repo, files_metadata=True)
            st = getattr(info, "safetensors", None)
            totals[repo] = getattr(st, "total", None)
            print(f"{repo:55s} total={totals[repo]}")
        except Exception as e:
            print(f"{repo:55s} ERR {type(e).__name__}: {str(e)[:70]}")
            totals[repo] = None

# 2) family fallback table from base/instruct rows with known sizes
family_size: dict[tuple[str, str], int | None] = {}
for r in examples:
    if r.get("metadata_variant_type") in ("base", "instruct"):
        fam, size = r.get("metadata_family"), r.get("metadata_size_label")
        if fam and size:
            family_size[(fam, size)] = r.get("metadata_parameter_count")

# 3) apply to rows
def size_of(repo: str) -> str | None:
    low = repo.lower()
    for s in ("8b", "4b", "1.7b", "1.5b", "0.6b", "0.5b", "2b", "1b"):
        if s in low:
            return s
    return None

n_filled = 0
for r in examples:
    repo = r["metadata_repo_id"]
    if r.get("metadata_weight_format") == "spec" and r.get("metadata_variant_type") == "self-abliterated":
        # inherit from source instruct row
        src = next((x for x in examples if x["metadata_repo_id"] == repo
                    and x.get("metadata_variant_type") == "instruct"), None)
        if src and src.get("metadata_parameter_count"):
            r["metadata_parameter_count"] = src["metadata_parameter_count"]
            r["metadata_config_fallback"] = (
                r.get("metadata_config_fallback", "")
                + " parameter_count from source instruct model"
            ).strip()
            n_filled += 1
        continue
    if r.get("metadata_parameter_count") is not None:
        continue
    val = totals.get(repo)
    if val is None:
        fam, size = r.get("metadata_family"), size_of(repo)
        val = family_size.get((fam, size)) if fam and size else None
    if val is not None:
        r["metadata_parameter_count"] = val
        if totals.get(repo) is None:
            r["metadata_config_fallback"] = (
                r.get("metadata_config_fallback", "")
                + f" parameter_count from family lookup ({fam or '?'}/{size or '?'})"
            ).strip()
        n_filled += 1

# 4) final pass: GGUF-only rows inherit from a same-family same-size safetensors row
for r in examples:
    if r.get("metadata_parameter_count") is not None:
        continue
    if r.get("metadata_weight_format") != "spec":
        fam, size = r.get("metadata_family"), size_of(r["metadata_repo_id"])
        src = next((x for x in examples
                    if x.get("metadata_family") == fam and size_of(x["metadata_repo_id"]) == size
                    and x.get("metadata_parameter_count") is not None), None)
        if src:
            r["metadata_parameter_count"] = src["metadata_parameter_count"]
            r["metadata_config_fallback"] = (
                r.get("metadata_config_fallback", "")
                + f" parameter_count from same-family safetensors row ({src['metadata_repo_id']})"
            ).strip()

reg["metadata"]["params_backfilled_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
REG_PATH.write_text(json.dumps(reg, indent=2))
print(f"\nupdated {n_filled} rows; wrote {REG_PATH}")
miss = [r["metadata_repo_id"] for r in examples if r.get("metadata_parameter_count") is None
        and r.get("metadata_weight_format") != "spec"]
print("rows still missing param count (non-spec):", miss)