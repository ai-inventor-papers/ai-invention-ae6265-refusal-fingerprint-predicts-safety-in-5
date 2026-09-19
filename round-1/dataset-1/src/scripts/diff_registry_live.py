#!/usr/bin/env python3
"""Compare EVERY non-spec registry row against live HF model_info; print mismatches."""
import json
import os
from pathlib import Path

from huggingface_hub import HfApi
from huggingface_hub.utils import RepositoryNotFoundError

WS = Path(__file__).resolve().parent.parent
api = HfApi(token=os.environ.get("HF_TOKEN") or None)

REG = json.loads((WS / "artifacts/registry.json").read_text())
rows = [r for r in REG["datasets"][0]["examples"]
        if r.get("metadata_weight_format") != "spec"]

mismatches = []
ok = 0
for r in rows:
    repo = r["metadata_repo_id"]
    try:
        info = api.model_info(repo, files_metadata=False)
    except RepositoryNotFoundError:
        mismatches.append((repo, "REPO NOT FOUND", r.get("metadata_variant_type")))
        continue
    except Exception as e:
        mismatches.append((repo, f"ERR {type(e).__name__}", str(e)[:80]))
        continue
    live_gated = info.gated if info.gated else False
    reg_gated = r.get("metadata_gated") or False
    live_lic = (info.card_data or {}).get("license")
    reg_lic = r.get("metadata_license")
    probs = []
    if bool(live_gated) != bool(reg_gated):
        probs.append(f"gated reg={reg_gated} live={live_gated}")
    if live_lic and reg_lic and live_lic not in str(reg_lic) and "gating" not in str(reg_lic):
        probs.append(f"license reg={reg_lic} live={live_lic}")
    if probs:
        mismatches.append((repo, "; ".join(probs), r.get("metadata_variant_type")))
    else:
        ok += 1

print(f"checked {len(rows)} rows; {ok} match; {len(mismatches)} mismatches")
for repo, prob, vt in sorted(mismatches):
    print(f"  {repo} [{vt}] -> {prob}")