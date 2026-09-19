#!/usr/bin/env python3
"""Live-verify a sample of registry repos against the HF Hub (independent re-check)."""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from huggingface_hub import HfApi  # noqa: E402

WS = Path(__file__).resolve().parent.parent
api = HfApi(token=os.environ.get("HF_TOKEN") or None)

REG = json.loads((WS / "artifacts/registry.json").read_text())
rows = [r for r in REG["datasets"][0]["examples"]
        if r.get("metadata_weight_format") != "spec"]

# Unique repos: check ~10 key ones + special checks
keys = [
    ("Qwen/Qwen3-0.6B", "instruct"),
    ("Qwen/Qwen3-0.6B-Base", "base"),
    ("Qwen/Qwen2.5-1.5B-Instruct", "instruct"),
    ("meta-llama/Llama-3.2-1B-Instruct", "instruct"),
    ("google/gemma-2-2b-it", "instruct"),
    ("google/gemma-2-2b", "base"),
    ("Qwen/Qwen3-8B", "instruct"),
    ("huihui-ai/Huihui-Qwen3-0.6B-abliterated-v2", "abliterated"),
    ("huihui-ai/Huihui-Qwen3-4B-Instruct-2507-abliterated", "abliterated"),
    ("IlyaGusev/gemma-2-2b-it-abliterated", "abliterated"),
]

print("=== live HF check of registry claims ===")
for repo_id, expected_variant in keys:
    try:
        info = api.model_info(repo_id, files_metadata=False)
        card = (info.card_data or {})
        cfg = None
        try:
            cfg = api.hf_hub_download(repo_id, "config.json")
            import json as _j
            cfg = _j.loads(Path(cfg).read_text())
        except Exception as e:
            cfg = f"ERR:{type(e).__name__}"
        L = cfg.get("num_hidden_layers") if isinstance(cfg, dict) else None
        H = cfg.get("hidden_size") if isinstance(cfg, dict) else None
        arch = cfg.get("architectures") if isinstance(cfg, dict) else None
        sibs = [s.rfilename for s in (info.siblings or [])]
        has_st = any(s.endswith(".safetensors") for s in sibs)
        has_gguf = any(s.endswith(".gguf") for s in sibs)
        print(
            f"{repo_id}\n  gated={info.gated} requires_token={info.requires_auth if hasattr(info,'requires_auth') else '?'} "
            f"license={card.get('license')} arch={arch}\n  L={L} H={H} safetensors={has_st} gguf={has_gguf} "
            f"base_model={card.get('base_model')}"
        )
    except Exception as e:
        print(f"{repo_id}: ERROR {type(e).__name__}: {str(e)[:120]}")

print("\n=== special: old naming + walledai gating claims ===")
for repo_id in ["Qwen/Qwen3-0.6B-Instruct", "walledai/XSTest", "cais/harmbench"]:
    try:
        info = api.model_info(repo_id)
        print(f"{repo_id}: EXISTS gated={info.gated}")
    except Exception as e:
        print(f"{repo_id}: {type(e).__name__}: {str(e)[:100]}")