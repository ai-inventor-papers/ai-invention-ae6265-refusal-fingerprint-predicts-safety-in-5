#!/usr/bin/env python3
"""Validation gates for the safety-screening data platform.

Gates:
 (1) schema shape of data_out.json (exp_sel_data_out conventions)
 (2) per-set row counts
 (3) nested K-subset property per seed
 (4) cross-group disjointness (exact-normalized) + nearest-10 Jaccard report
 (5) registry: every zoo/abliterated repo resolves via model_info; layer/dim + fold fields present
 (6) RNG determinism: rebuild from sources reproduces identical prompt texts
 (7) every row has input/output/metadata_fold and non-empty prompt text
 (8) no prompt exceeds 512 tokens (word-count proxy + char guard)
 (9) file sizes sane
"""

from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

from loguru import logger
import requests

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"

logger.remove()
logger.add(sys.stdout, level="INFO", format="{time:HH:mm:ss}|{level:<7}|{message}")
logger.add(str(ROOT / "logs" / "verify.log"), rotation="30 MB", level="DEBUG")

PASS = []
FAIL = []


def gate(name: str, ok: bool, detail: str = "") -> None:
    (PASS if ok else FAIL).append(name)
    (logger.info if ok else logger.error)(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" - {detail}" if detail else ""))


def norm_text(s: str) -> str:
    t = re.sub(r"[^a-z0-9\s]", " ", s.lower())
    return re.sub(r"\s+", " ", t).strip()


def ngram_jaccard(a: str, b: str, n: int = 3) -> float:
    def grams(t: str):
        tt = norm_text(t).replace(" ", "")
        if len(tt) < n:
            return set()
        return {tt[i:i + n] for i in range(len(tt) - n + 1)}
    ga, gb = grams(a), grams(b)
    if not ga or not gb:
        return 0.0
    return len(ga & gb) / len(ga | gb)


def main() -> None:
    data = json.loads((ART / "data_out.json").read_text())
    rows = data["datasets"][0]["examples"]

    # ---- gate 1: schema shape ----
    schema_ok = True
    for r in rows:
        if not isinstance(r.get("input"), str) or not isinstance(r.get("output"), str):
            schema_ok = False
            break
        for k in r:
            if k not in ("input", "output") and not k.startswith("metadata_"):
                schema_ok = False
                break
    gate("g1_schema_shape", set(data.keys()) <= {"metadata", "datasets"} and schema_ok,
         f"{len(rows)} rows")

    # ---- gate 2: counts ----
    from collections import Counter
    counts = Counter(r["metadata_set"] for r in rows)
    gate("g2_counts",
         counts["refusal_120"] == 120
         and counts["xstest"] == 450
         and counts["jailbreak"] == 60
         and counts["contrast_base"] == 32
         and counts["contrast_membership"] == 186
         and counts["canonical"] == 5
         and counts["benign"] == 75,
         f"{dict(counts)}")
    xs = [r for r in rows if r["metadata_set"] == "xstest"]
    gate("g2b_xstest_split", sum(1 for r in xs if r["metadata_xstest_label"] == "safe") == 250
         and sum(1 for r in xs if r["metadata_xstest_label"] == "unsafe") == 200,
         f"safe={sum(1 for r in xs if r['metadata_xstest_label']=='safe')} unsafe={sum(1 for r in xs if r['metadata_xstest_label']=='unsafe')}")
    jb = sorted({r["metadata_pair_id"] for r in rows if r["metadata_set"] == "jailbreak"})
    gate("g2c_jailbreak_pairs", len(jb) == 30, f"{len(jb)} pairs")

    # ---- gate 3: nested property ----
    mem = [r for r in rows if r["metadata_set"] == "contrast_membership"]
    nested_ok = True
    for seed in (0, 1, 2):
        subsets = {}
        for K in (1, 2, 4, 8, 16):
            subsets[K] = {r["metadata_pair_id"] for r in mem
                          if r["metadata_seed"] == seed and r["metadata_k_size"] == K}
        for a, b in ((1, 2), (2, 4), (4, 8), (8, 16)):
            if not subsets[a] <= subsets[b]:
                nested_ok = False
                logger.error(f"seed {seed}: K={a} not subset of K={b}")
        if len(subsets[16]) != 16:
            nested_ok = False
        if len(subsets[1]) != 1 or len(subsets[2]) != 2 or len(subsets[4]) != 4 or len(subsets[8]) != 8:
            nested_ok = False
    gate("g3_nested_subsets", nested_ok)

    # ---- gate 4: cross-group disjointness + nearest-10 Jaccard ----
    def group_of(r: dict) -> str:
        s = r["metadata_set"]
        return "contrast" if s.startswith("contrast") else s
    seen = {}
    dup = 0
    for r in rows:
        k = norm_text(r["input"])
        g = group_of(r)
        if k in seen and seen[k] != g:
            dup += 1
        else:
            seen[k] = g
    gate("g4_disjoint_exact", dup == 0, f"{dup} cross-group duplicates")
    # nearest cross-set pairs by ngram Jaccard (first row per (group,text))
    first_by_group_text = {}
    for r in rows:
        first_by_group_text.setdefault((group_of(r), norm_text(r["input"])), r["input"])
    texts = list(first_by_group_text.values())
    gs = list(first_by_group_text.keys())
    pairs = []
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            if gs[i][0] == gs[j][0]:
                continue
            sim = ngram_jaccard(texts[i], texts[j])
            if sim >= 0.4:
                pairs.append((round(sim, 3), gs[i][0], gs[j][0], texts[i][:60], texts[j][:60]))
    pairs.sort(reverse=True)
    logger.info(f"g4_nearest_cross_set_pairs (sim>=0.4): {len(pairs)}")
    for p in pairs[:10]:
        logger.info(f"   J={p[0]} [{p[1]} vs {p[2]}] {p[3]!r} ~~ {p[4]!r}")
    over06 = [p for p in pairs if p[0] >= 0.6]
    gate("g4b_no_near_duplicates", not over06,
         f"{len(pairs)} near pairs (0.4-0.6) below duplicate threshold; {len(over06)} >= 0.6 (would be duplicates)")

    # ---- gate 5: registry ----
    reg = json.loads((ART / "registry.json").read_text())
    rrows = reg["datasets"][0]["examples"]
    no_layer = [r["metadata_repo_id"] for r in rrows
                if r["metadata_variant_type"] in ("base", "instruct", "abliterated")
                and (r.get("metadata_num_layers") is None or r.get("metadata_hidden_size") is None)]
    gate("g5_layer_dim_fields", not no_layer, f"missing: {no_layer}")
    no_fold = [r["metadata_repo_id"] for r in rrows if r["metadata_fold"] not in ("screen", "reserved")]
    gate("g5b_fold_fields", not no_fold, f"missing fold: {no_fold}")
    screen_ids = {r["metadata_repo_id"] for r in rrows if r["metadata_fold"] == "screen"}
    reserved_ids = {r["metadata_repo_id"] for r in rrows if r["metadata_fold"] == "reserved"}
    gate("g5c_fold_disjoint", not (screen_ids & reserved_ids))
    # live resolution of real repos (skip self-ablit spec rows)
    from huggingface_hub import HfApi
    api = HfApi()
    real = [r["metadata_repo_id"] for r in rrows if r["metadata_variant_type"] != "self-abliterated"]
    unresolved = []
    for rid in sorted(set(real)):
        ok = False
        for _ in range(2):
            try:
                api.model_info(rid)
                ok = True
                break
            except Exception:
                time.sleep(2)
        if not ok:
            unresolved.append(rid)
    gate("g5d_repos_resolve", not unresolved, f"unresolved: {unresolved}")

    # ---- gate 6: RNG determinism ----
    import importlib.util
    spec = importlib.util.spec_from_file_location("build_platform", ROOT / "scripts" / "build_platform.py")
    bp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bp)  # type: ignore[union-attr]
    src = bp.load_sources()
    refusal = bp.build_refusal(src["harmbench"])
    cb, cm, _ = bp.build_contrast(
        src["harmbench"],
        {r["metadata_prompt_id"].replace("refusal_", "") for r in refusal},
        refusal_texts=[r["input"] for r in refusal],
    )
    canon = bp.build_canonical()
    benign = bp.build_benign(src["dolly"])
    xs = bp.build_xstest(src["xstest"])
    rebuilt = {r["metadata_prompt_id"]: r["input"] for r in refusal + cb + cm + canon + benign + xs}
    saved = {r["metadata_prompt_id"]: r["input"] for r in rows}
    mism = [k for k in rebuilt if k in saved and rebuilt[k] != saved[k]]
    gate("g6_rng_determinism", not mism, f"{len(rebuilt)} ids compared, mismatches: {mism[:5]}")

    # ---- gate 7: row basics ----
    bad = [r["metadata_prompt_id"] for r in rows if not r.get("input") or "metadata_fold" not in r]
    gate("g7_row_basics", not bad, f"bad rows: {bad[:5]}")

    # ---- gate 8: prompt length (real tokenizer, Qwen2.5-0.5B) ----
    from transformers import AutoTokenizer
    _tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-0.5B")
    long = []
    max_tok = 0
    for r in rows:
        n = len(_tok.encode(r["input"], add_special_tokens=False))
        max_tok = max(max_tok, n)
        if n > 512:
            long.append((r["metadata_prompt_id"], n))
    gate("g8_token_budget", not long,
         f"rows > 512 tokens: {long[:3]} (max tokens={max_tok})")

    # ---- gate 9: file sizes ----
    sizes = {p.name: p.stat().st_size for p in sorted(ART.glob("*.json")) + sorted(ART.glob("*.md"))}
    for f, s in sizes.items():
        logger.info(f"size {f}: {s/1024:.1f} KB")
    gate("g9_sizes", all(v < 5 * 1024 * 1024 for v in sizes.values()), "all artifacts < 5 MB")

    logger.info("=" * 60)
    logger.info(f"TOTAL: {len(PASS)} passed, {len(FAIL)} failed")
    if FAIL:
        logger.error(f"FAILED GATES: {FAIL}")
        sys.exit(1)
    logger.info("ALL VALIDATION GATES GREEN")


if __name__ == "__main__":
    main()