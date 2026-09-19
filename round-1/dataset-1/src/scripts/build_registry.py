#!/usr/bin/env python3
"""Live-verify the model zoo on the HF Hub and emit artifacts/registry.json.

Rows follow the exp_sel_data_out field conventions (input/output + metadata_*).
Folds: 'screen' (zoo + community abliterated cross-checks + self-ablit specs) and
'reserved' (Qwen3-8B pair + one community abliterated + alpha=0.35 self-ablit spec).
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from huggingface_hub import HfApi, hf_hub_download
from loguru import logger

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"
TOKEN = os.environ.get("HF_TOKEN") or None

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add(str(ROOT / "logs" / "registry.log"), rotation="30 MB", level="DEBUG")

API = HfApi()

# NOTE (verified 2026-09-19): the plan's assumed ids 'Qwen/Qwen3-*-Instruct' no longer
# resolve on the HF Hub (404, even with token). Qwen's current official naming for the
# original Qwen3 line is: 'Qwen/Qwen3-{size}' = instruct/chat checkpoint (card frontmatter
# base_model: Qwen3-{size}-Base; README contains /think, enable_thinking docs), and
# 'Qwen/Qwen3-{size}-Base' = pretrained base. Verified per-repo below. The -2507 line
# (Qwen3-4B-Instruct-2507 etc.) is a separate updated lineage and is NOT used for the
# base/instruct pairs (architecture/config identical, direct Base counterpart available).
ZOO = [
    ("Qwen/Qwen3-0.6B-Base", "qwen3", "0.6B", "base", "screen"),
    ("Qwen/Qwen3-0.6B", "qwen3", "0.6B", "instruct", "screen"),
    ("Qwen/Qwen3-1.7B-Base", "qwen3", "1.7B", "base", "screen"),
    ("Qwen/Qwen3-1.7B", "qwen3", "1.7B", "instruct", "screen"),
    ("Qwen/Qwen3-4B-Base", "qwen3", "4B", "base", "screen"),
    ("Qwen/Qwen3-4B", "qwen3", "4B", "instruct", "screen"),
    ("Qwen/Qwen2.5-0.5B", "qwen2.5", "0.5B", "base", "screen"),
    ("Qwen/Qwen2.5-0.5B-Instruct", "qwen2.5", "0.5B", "instruct", "screen"),
    ("Qwen/Qwen2.5-1.5B", "qwen2.5", "1.5B", "base", "screen"),
    ("Qwen/Qwen2.5-1.5B-Instruct", "qwen2.5", "1.5B", "instruct", "screen"),
    ("meta-llama/Llama-3.2-1B", "llama3.2", "1B", "base", "screen"),
    ("meta-llama/Llama-3.2-1B-Instruct", "llama3.2", "1B", "instruct", "screen"),
    ("google/gemma-2-2b", "gemma2", "2B", "base", "screen"),
    ("google/gemma-2-2b-it", "gemma2", "2B", "instruct", "screen"),
    ("Qwen/Qwen3-8B-Base", "qwen3", "8B", "base", "reserved"),
    ("Qwen/Qwen3-8B", "qwen3", "8B", "instruct", "reserved"),
]

# published-architecture cross-check table (used only when config.json is unreadable)
EXPECTED_CONFIG = {
    "Qwen/Qwen3-0.6B": dict(num_hidden_layers=28, hidden_size=1024),
    "Qwen/Qwen3-0.6B-Base": dict(num_hidden_layers=28, hidden_size=1024),
    "Qwen/Qwen3-1.7B": dict(num_hidden_layers=28, hidden_size=2048),
    "Qwen/Qwen3-1.7B-Base": dict(num_hidden_layers=28, hidden_size=2048),
    "Qwen/Qwen3-4B": dict(num_hidden_layers=36, hidden_size=2560),
    "Qwen/Qwen3-4B-Base": dict(num_hidden_layers=36, hidden_size=2560),
    "Qwen/Qwen3-8B": dict(num_hidden_layers=36, hidden_size=4096),
    "Qwen/Qwen3-8B-Base": dict(num_hidden_layers=36, hidden_size=4096),
    "Qwen/Qwen2.5-0.5B": dict(num_hidden_layers=24, hidden_size=512),
    "Qwen/Qwen2.5-1.5B": dict(num_hidden_layers=28, hidden_size=1536),
    "meta-llama/Llama-3.2-1B": dict(num_hidden_layers=16, hidden_size=2048),
    "google/gemma-2-2b": dict(num_hidden_layers=26, hidden_size=2304),
}

CHAT_FORMAT = {
    "qwen3": "chatml",
    "qwen2.5": "chatml",
    "llama3.2": "llama3",
    "gemma2": "gemma",
}


def chat_format_for(family: str, variant: str) -> str:
    if variant == "base":
        return "raw"
    return CHAT_FORMAT[family]


def read_config(repo_id: str, retries: int = 4) -> tuple[dict | None, bool]:
    """Return (config_json_or_None, config_verified_bool). Retries with backoff for HF throttling."""
    import time
    for attempt in range(retries):
        try:
            cf = hf_hub_download(repo_id, "config.json", token=TOKEN)
            return (json.loads(Path(cf).read_text()), True)
        except Exception as exc:  # noqa: BLE001 - collect all failure modes, log detail
            if attempt == retries - 1:
                logger.warning(f"config.json unreadable for {repo_id}: {type(exc).__name__} {str(exc)[:100]}")
                return (None, False)
            time.sleep(1.5 * (attempt + 1))


def model_info_retry(repo_id: str, retries: int = 5):
    """model_info with backoff; HF API is flaky under load."""
    import time
    last = None
    for attempt in range(retries):
        try:
            return API.model_info(repo_id, token=TOKEN)
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(2.0 * (attempt + 1))
    raise last  # type: ignore[misc]


def verify_model(repo_id: str, family: str, size_label: str, variant: str, fold: str) -> dict:
    info = model_info_retry(repo_id)
    siblings = [s.rfilename for s in info.siblings]
    has_safetensors = any(f.endswith(".safetensors") for f in siblings)
    has_gguf = any(f.endswith(".gguf") for f in siblings)
    has_safetensors_index = any("safetensors.index.json" in f for f in siblings)
    weight_format = ("both" if has_safetensors and has_gguf
                     else "safetensors" if has_safetensors else "gguf" if has_gguf else "unknown")
    license_str = None
    if info.cardData:
        license_str = getattr(info.cardData, "license", None)
    elif info.card_data:
        license_str = info.card_data.get("license")
    gated = info.gated  # None / 'auto' / 'manual'
    requires_token = gated in ("auto", "manual") or has_gguf

    config, config_ok = read_config(repo_id)
    cfg_out = {
        "num_layers": None, "hidden_size": None, "intermediate_size": None,
        "num_attention_heads": None, "num_key_value_heads": None,
        "architectures": None, "parameter_count": None,
    }
    if config is not None:
        cfg_out["num_layers"] = config.get("num_hidden_layers", config.get("num_layers"))
        cfg_out["hidden_size"] = config.get("hidden_size", config.get("d_model"))
        cfg_out["intermediate_size"] = config.get("intermediate_size", config.get("ffn_hidden_size"))
        cfg_out["num_attention_heads"] = config.get("num_attention_heads")
        cfg_out["num_key_value_heads"] = config.get("num_key_value_heads")
        cfg_out["architectures"] = config.get("architectures")
        cfg_out["parameter_count"] = config.get("num_parameters")
        # cross-check layers/dim against published table
        exp = EXPECTED_CONFIG.get(repo_id)
        if exp:
            if exp["num_hidden_layers"] != cfg_out["num_layers"]:
                logger.warning(f"{repo_id}: layers {cfg_out['num_layers']} != published {exp['num_hidden_layers']} (keeping config)")
            if exp["hidden_size"] != cfg_out["hidden_size"]:
                logger.warning(f"{repo_id}: hidden {cfg_out['hidden_size']} != published {exp['hidden_size']} (keeping config)")
    else:
        exp = EXPECTED_CONFIG.get(repo_id, {})
        cfg_out["num_layers"] = exp.get("num_hidden_layers")
        cfg_out["hidden_size"] = exp.get("hidden_size")
        cfg_out["config_verified_fallback"] = "HF model card / published configs"

    usable = has_safetensors and not cfg_out.get("config_verified_fallback")

    row = {
        "input": repo_id,
        "output": f"{size_label} {variant} ({fam_family(family)})",
        "metadata_repo_id": repo_id,
        "metadata_family": family,
        "metadata_size_label": size_label,
        "metadata_variant_type": variant,
        "metadata_fold": fold,
        "metadata_gated": str(gated) if gated else None,
        "metadata_requires_hf_token": requires_token,
        "metadata_weight_format": weight_format,
        "metadata_license": license_str or ("see gating page" if gated else None),
        "metadata_num_layers": cfg_out["num_layers"],
        "metadata_hidden_size": cfg_out["hidden_size"],
        "metadata_intermediate_size": cfg_out["intermediate_size"],
        "metadata_num_attention_heads": cfg_out["num_attention_heads"],
        "metadata_num_key_value_heads": cfg_out["num_key_value_heads"],
        "metadata_architectures": cfg_out["architectures"],
        "metadata_chat_format": chat_format_for(family, variant),
        "metadata_parameter_count": cfg_out["parameter_count"],
        "metadata_usable_for_activation_hooks": usable,
        "metadata_config_verified": config_ok,
        "metadata_has_safetensors_index": has_safetensors_index,
        "metadata_source_url": f"https://huggingface.co/{repo_id}",
        "metadata_verified_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "metadata_inference_note": (
            "raw continuation (no chat template)" if variant == "base"
            else "apply_chat_template; single fixed minimal system prompt; user content only"
        ),
    }
    return row


def fam_family(family: str) -> str:
    return {
        "qwen3": "Qwen3", "qwen2.5": "Qwen2.5", "llama3.2": "Llama 3.2", "gemma2": "Gemma 2",
    }[family]


def main() -> None:
    ART.mkdir(exist_ok=True)
    rows: list[dict] = []
    for repo_id, family, size, variant, fold in ZOO:
        logger.info(f"verifying {repo_id} ...")
        try:
            rows.append(verify_model(repo_id, family, size, variant, fold))
        except Exception as exc:  # noqa: BLE001
            logger.error(f"model_info failed for {repo_id}: {exc}")
            raise

    # ---- community abliterated search ----
    ablit_repos: list[str] = []
    for params in (
        dict(author="huihui-ai", search="abliterated"),
        dict(author="huihui-ai", search="Qwen3"),
        dict(author="huihui-ai", search="Qwen2.5"),
        dict(author="huihui-ai", search="gemma"),
        dict(author="huihui-ai", search="llama"),
    ):
        try:
            for m in API.list_models(**params, limit=100):
                ablit_repos.append(m.id)
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"list_models({params}) failed: {exc}")
    for q in ("Qwen3 abliterated", "Qwen2.5-1.5B-Instruct-abliterated",
              "gemma-2-2b abliterated", "Llama-3.2-1B abliterated",
              "Qwen3-0.6B-Instruct-abliterated", "Qwen3-1.7B-Instruct-abliterated",
              "Qwen3-8B-Instruct-abliterated"):
        try:
            for m in API.list_models(search=q, limit=25):
                ablit_repos.append(m.id)
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"list_models(search={q}) failed: {exc}")
    ablit_repos = sorted(set(ablit_repos))
    logger.info(f"candidate abliterated repos: {ablit_repos}")

    family_match = {
        # strict size patterns -> (family, label); excludes VL/Coder/Next/Omni/ASR/TTS
        "qwen3": ("Qwen3", ["qwen3-0.6b", "qwen3-1.7b", "qwen3-4b", "qwen3-8b"]),
        "qwen2.5": ("Qwen2.5", ["qwen2.5-0.5b", "qwen2.5-1.5b"]),
        "llama3.2": ("Llama-3.2", ["llama-3.2-1b"]),
        "gemma2": ("Gemma-2", ["gemma-2-2b"]),
    }
    allowed_authors = {"huihui-ai", "mylesgoose", "IlyaGusev"}
    blocklist = ("deepseek", "distill", "thinking-2507", "-thinking", "coder", "coding",
                 "vl-", "mlx", "-awq", "-gptq", "-exl2", "-fp8", "lora")

    def size_from_low(low: str) -> str | None:
        for needle, size in (("0.6b", "0.6B"), ("1.7b", "1.7B"), ("4b", "4B"), ("8b", "8B"),
                             ("0.5b", "0.5B"), ("1.5b", "1.5B"), ("1b", "1B"), ("2b", "2B")):
            if needle in low:
                return size
        return None

    # zoo source instruct architectures (family, size) -> config fields (config-verified above)
    zoo_arch_map: dict = {}
    for r in rows:
        if r["metadata_variant_type"] in ("base", "instruct") and r["metadata_config_verified"]:
            for needle, size in (("0.6b", "0.6B"), ("1.7b", "1.7B"), ("4b", "4B"), ("8b", "8B"),
                                 ("0.5b", "0.5B"), ("1.5b", "1.5B"), ("1b", "1B"), ("2b", "2B")):
                if needle in r["metadata_repo_id"].lower():
                    zoo_arch_map[(r["metadata_family"], size)] = {
                        "num_hidden_layers": r["metadata_num_layers"],
                        "hidden_size": r["metadata_hidden_size"],
                        "intermediate_size": r["metadata_intermediate_size"],
                        "num_attention_heads": r["metadata_num_attention_heads"],
                        "num_key_value_heads": r["metadata_num_key_value_heads"],
                        "architectures": r["metadata_architectures"],
                        "num_parameters": r["metadata_parameter_count"],
                    }
                    break

    registered_ablit: list[str] = []
    for rid in ablit_repos:
        low = rid.lower()
        if "abliterated" not in low:
            continue
        if any(b in low for b in blocklist):
            continue
        family = None
        for key, (lab, needles) in family_match.items():
            if any(n in low for n in needles):
                family = key
                break
        if family is None:
            continue
        author = rid.split("/")[0]
        if author not in allowed_authors:
            continue
        # safetensors-only repos are hook-usable; GGUF-only are not
        try:
            info = model_info_retry(rid)
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"model_info {rid}: {exc}")
            continue
        sibs = [s.rfilename for s in info.siblings]
        has_st = any(f.endswith(".safetensors") for f in sibs)
        has_gguf_only = (not has_st) and any(f.endswith(".gguf") for f in sibs)
        logger.info(f"abliterated candidate {rid}: safetensors={has_st} gguf-only={has_gguf_only}")
        cfg, cfg_ok = read_config(rid)
        cfg_fallback_note = None
        if cfg is None:
            # abliterated checkpoints share the architecture of their source instruct model:
            # inherit from the zoo row of the same family+size (already config-verified).
            inherit = zoo_arch_map.get((family, size_from_low(rid)))
            if inherit:
                cfg = inherit
                cfg_fallback_note = "architecture inherited from zoo source instruct model (config.json unreadable/gated)"
        rows.append({
            "input": rid,
            "output": f"community abliterated {family}",
            "metadata_repo_id": rid,
            "metadata_family": family,
            "metadata_size_label": "unknown",
            "metadata_variant_type": "abliterated",
            "metadata_fold": "reserved" if False else "screen",  # override below
            "metadata_gated": str(info.gated) if info.gated else None,
            "metadata_requires_hf_token": bool(info.gated),
            "metadata_weight_format": ("gguf" if has_gguf_only else "safetensors" if has_st else "unknown"),
            "metadata_license": (info.cardData.license if info.cardData and getattr(info.cardData, "license", None) else "see gating page" if info.gated else None),
            "metadata_num_layers": cfg.get("num_hidden_layers", cfg.get("num_layers")) if cfg else None,
            "metadata_hidden_size": cfg.get("hidden_size") if cfg else None,
            "metadata_intermediate_size": cfg.get("intermediate_size") if cfg else None,
            "metadata_num_attention_heads": cfg.get("num_attention_heads") if cfg else None,
            "metadata_num_key_value_heads": cfg.get("num_key_value_heads") if cfg else None,
            "metadata_architectures": cfg.get("architectures") if cfg else None,
            "metadata_chat_format": chat_format_for(family, "instruct"),
            "metadata_parameter_count": cfg.get("num_parameters") if cfg else None,
            "metadata_usable_for_activation_hooks": has_st,
            "metadata_config_verified": cfg_ok,
            "metadata_config_fallback": cfg_fallback_note,
            "metadata_has_safetensors_index": False,
            "metadata_source_url": f"https://huggingface.co/{rid}",
            "metadata_verified_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "metadata_inference_note": ("GGUF-only, not hook-usable" if has_gguf_only else "community abliterated; chat template of base instruct model"),
        })
        registered_ablit.append(rid)

    screen_ablit = [r for r in rows if r["metadata_variant_type"] == "abliterated"]
    # deterministic reserved pick: first family-matching hook-usable safetensors repo (sorted)
    hookable = sorted(r["metadata_repo_id"] for r in screen_ablit if r["metadata_usable_for_activation_hooks"])
    reserved_ablit_id = hookable[0] if hookable else None
    logger.info(f"reserved community abliterated pick: {reserved_ablit_id}")
    for r in rows:
        if r["metadata_variant_type"] == "abliterated" and r["metadata_repo_id"] == reserved_ablit_id:
            r["metadata_fold"] = "reserved"

    # ---- self-abliteration specs ----
    def self_ablit_spec(source_repo: str, alphas: list, fold: str = "screen") -> dict:
        return {
            "input": f"self-abliterated({source_repo}, alphas={alphas})",
            "output": "spec only - weights created at experiment time",
            "metadata_repo_id": source_repo,
            "metadata_family": "qwen3",  # overridden by caller
            "metadata_size_label": "spec",
            "metadata_variant_type": "self-abliterated",
            "metadata_fold": fold,
            "metadata_gated": None,
            "metadata_requires_hf_token": False,
            "metadata_weight_format": "spec",
            "metadata_license": "n/a (constructed at experiment time)",
            "metadata_num_layers": None,
            "metadata_hidden_size": None,
            "metadata_intermediate_size": None,
            "metadata_num_attention_heads": None,
            "metadata_num_key_value_heads": None,
            "metadata_architectures": None,
            "metadata_chat_format": chat_format_for("qwen3", "instruct"),
            "metadata_parameter_count": None,
            "metadata_usable_for_activation_hooks": False,
            "metadata_config_verified": False,
            "metadata_has_safetensors_index": False,
            "metadata_source_url": f"https://huggingface.co/{source_repo}",
            "metadata_verified_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "metadata_inference_note": "self-abliteration spec (Arditi et al. 2024): hook-time residual-stream orthogonalization, alpha-scaled; per-layer at experiment time",
            "metadata_self_ablit_alphas": alphas,
            "metadata_self_ablit_method": (
                "Arditi et al. 2024 hook-time residual-stream orthogonalization (SteeringVector-style), alpha-scaled"
            ),
        }

    instruct_zoo = [
        (r["metadata_repo_id"], r["metadata_family"])
        for r in rows
        if r["metadata_variant_type"] == "instruct" and r["metadata_fold"] == "screen"
    ]
    grid = [0.25, 0.5, 0.75, 1.0]
    for src, fam in sorted(instruct_zoo):
        spec = self_ablit_spec(src, grid)
        spec["metadata_family"] = fam
        spec["metadata_chat_format"] = chat_format_for(fam, "instruct")
        rows.append(spec)
    # reserved self-ablit spec at alpha 0.35 (off-grid)
    res_instruct = [r["metadata_repo_id"] for r in rows if r["metadata_variant_type"] == "instruct" and r["metadata_fold"] == "reserved"]
    if res_instruct:
        spec = self_ablit_spec(res_instruct[0], [0.35], fold="reserved")
        spec["metadata_family"] = "qwen3"
        rows.append(spec)

    folds = {}
    for r in rows:
        folds.setdefault(r["metadata_fold"], []).append(r["metadata_repo_id"])
    logger.info(f"fold assignment: { {k: len(v) for k, v in folds.items()} }")
    overlap = set(folds.get("screen", [])) & set(folds.get("reserved", []))
    assert not overlap, f"fold overlap: {overlap}"

    # provenance for the two reserved Qwen3-8B rows: verify config.json too
    for r in rows:
        if r["metadata_repo_id"] in ("Qwen/Qwen3-8B", "Qwen/Qwen3-8B-Base"):
            cfg, ok = read_config(r["metadata_repo_id"])
            if cfg is not None:
                r["metadata_num_layers"] = cfg.get("num_hidden_layers")
                r["metadata_hidden_size"] = cfg.get("hidden_size")
                r["metadata_intermediate_size"] = cfg.get("intermediate_size")
                r["metadata_num_attention_heads"] = cfg.get("num_attention_heads")
                r["metadata_num_key_value_heads"] = cfg.get("num_key_value_heads")
                r["metadata_architectures"] = cfg.get("architectures")
                r["metadata_parameter_count"] = cfg.get("num_parameters")
                r["metadata_config_verified"] = ok
                r["metadata_usable_for_activation_hooks"] = ok
    # TODO note: Qwen3-8B rows were verified via model_info during ZOO loop already; this pass refreshes config.

    # ---- final post-pass: fill any missing architecture fields ----
    # Verified live from config.json during this run (zoo rows) and used as the
    # source of truth for abliterated/GGUF rows whose config.json is unreadable/gated.
    arch_table: dict = {}
    for r in rows:
        if r["metadata_variant_type"] in ("base", "instruct") and r.get("metadata_num_layers"):
            size = size_from_low(r["metadata_repo_id"].lower())
            if size:
                arch_table[(r["metadata_family"], size)] = {
                    "num_layers": r["metadata_num_layers"],
                    "hidden_size": r["metadata_hidden_size"],
                    "intermediate_size": r["metadata_intermediate_size"],
                    "num_attention_heads": r["metadata_num_attention_heads"],
                    "num_key_value_heads": r["metadata_num_key_value_heads"],
                    "architectures": r["metadata_architectures"],
                }
    for r in rows:
        if r["metadata_variant_type"] not in ("base", "instruct", "abliterated"):
            continue
        if r.get("metadata_num_layers") is not None:
            continue
        size = size_from_low(r["metadata_repo_id"].lower())
        arch = arch_table.get((r["metadata_family"], size))
        if arch and r.get("metadata_config_fallback") is None:
            r["metadata_num_layers"] = arch["num_layers"]
            r["metadata_hidden_size"] = arch["hidden_size"]
            r["metadata_intermediate_size"] = arch["intermediate_size"]
            r["metadata_num_attention_heads"] = arch["num_attention_heads"]
            r["metadata_num_key_value_heads"] = arch["num_key_value_heads"]
            r["metadata_architectures"] = arch["architectures"]
            r["metadata_config_fallback"] = "architecture from zoo source model (config.json unreadable/gated)"
            logger.info(f"post-pass: filled architecture for {r['metadata_repo_id']} from zoo source model")

    # ---- self-abliterated specs inherit architecture + parameter count from source instruct model ----
    # (plan 3.5: layer/dim fields MUST be present on every registry row; the next iteration
    # needs them to standardize per-layer profiles for the primary abliteration design.)
    source_by_repo: dict = {
        r["metadata_repo_id"]: r
        for r in rows
        if r["metadata_variant_type"] == "instruct"
    }
    for r in rows:
        if r["metadata_variant_type"] != "self-abliterated":
            continue
        src = source_by_repo.get(r["metadata_repo_id"])
        if src is None:
            logger.warning(f"self-ablit spec has no instruct source row: {r['metadata_repo_id']}")
            continue
        for field in (
            "metadata_num_layers",
            "metadata_hidden_size",
            "metadata_intermediate_size",
            "metadata_num_attention_heads",
            "metadata_num_key_value_heads",
            "metadata_architectures",
            "metadata_parameter_count",
        ):
            r[field] = src[field]
        r["metadata_usable_for_activation_hooks"] = True  # hooks attach to the source instruct model
        r["metadata_config_verified"] = False  # spec carries source config, not its own weights
        r["metadata_config_fallback"] = (
            "architecture + parameter count inherited from source instruct model (spec; weights created at experiment time)"
        )
        logger.info(f"self-ablit spec {r['metadata_repo_id']} inherited L={r['metadata_num_layers']} H={r['metadata_hidden_size']} params={r['metadata_parameter_count']}")

    # community abliterated availability per family
    ablit_by_family: dict = {}
    for r in rows:
        if r["metadata_variant_type"] == "abliterated":
            ablit_by_family.setdefault(r["metadata_family"], []).append(r["metadata_repo_id"])
    family_availability = {
        fam: {
            "registered": sorted(ablit_by_family.get(fam, [])),
            "note": "available" if ablit_by_family.get(fam) else "not available (self-abliteration spec carries the family)",
        }
        for fam in ("qwen3", "qwen2.5", "llama3.2", "gemma2")
    }

    out = {
        "metadata": {
            "description": "Live-verified model registry for safety screening (folds screen/reserved never mixed)",
            "verified_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "fold_rule": "screen = zoo + community abliterated + self-ablit grid; reserved = Qwen3-8B pair + 1 community abliterated + alpha=0.35 spec",
            "qwen3_naming_note": (
                "Verified 2026-09-19: 'Qwen/Qwen3-{size}-Instruct' repo ids are gone (404 with token). "
                "Current official naming: 'Qwen/Qwen3-{size}' = instruct (card base_model: Qwen3-{size}-Base, "
                "README has /think + enable_thinking), 'Qwen/Qwen3-{size}-Base' = pretrained base. "
                "Registry uses these verified ids; plan ids updated accordingly."
            ),
            "community_abliterated_family_availability": family_availability,
        },
        "datasets": [{"dataset": "model_registry_v1", "examples": rows}],
    }
    (ART / "registry.json").write_text(json.dumps(out, indent=1))
    logger.info(f"WROTE artifacts/registry.json: {len(rows)} rows")


if __name__ == "__main__":
    main()