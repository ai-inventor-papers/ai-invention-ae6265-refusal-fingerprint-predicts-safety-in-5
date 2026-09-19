#!/usr/bin/env python3
"""Saturation-search campaign: runs a list of queries through the aii web-search
script (scholarly or general) and logs ranked results to log/search_*.txt.
Usage: python3 search_campaign.py [--mode scholarly|general] [--sleep 4] [--tag phase]
"""
import argparse, subprocess, sys, time, os
from pathlib import Path

SKILL_DIR = "/ai-inventor/.claude/skills/aii-web-tools"
PY = "/ai-inventor/.claude/skills/.ability_client_venv/bin/python"
SCRIPT = os.path.join(SKILL_DIR, "scripts", "aii_fast_web_search.py")

QUERIES = {
    "G1_potency": [
        "refusal direction per-layer norm profile language model",
        "abliteration activation differences per-layer safety direction",
        "safety direction layer-wise norm across architectures",
        "refusal direction layer norm base instruct comparison",
    ],
    "G2_onset": [
        "refusal onset first token position hidden states LLM",
        "earliest layer refusal direction emerges language model layers",
        "refusal behavior emergence layer depth transformer",
        "when refusal is computed before generation first response token",
    ],
    "G3_redundancy": [
        "participation ratio effective dimensionality refusal direction representation",
        "dimensionality refusal subspace safety representation multiple directions",
        "effective rank refusal direction hidden states",
        "multiple category-specific refusal directions",
    ],
    "G4_classid": [
        "identify safety-tuned model activations base instruct abliterated",
        "distinguish abliterated checkpoint alignment provenance",
        "detect alignment fine-tuning from activations classifier",
        "model lineage fine-tuning detection activation signatures",
    ],
    "G5_kscaling": [
        "number of contrastive pairs direction estimate error scaling",
        "sample complexity representation direction estimation language model",
        "stability refusal direction few examples contrast pairs",
        "steering vector number of examples scaling law",
    ],
    "G6_dose": [
        "partial ablation refusal direction alpha sweep abliteration",
        "intervention strength sweep latent vulnerability refusal",
        "abliteration dose response refusal rate strength",
        "refusal direction removal strength effect sharpness",
    ],
    "P2_baselines": [
        "randomly initialized transformers interpretability scores auto-interp",
        "unrestricted alignment maps randomly initialized models causal abstraction",
        "control tasks probing selectivity Hewitt Liang",
        "random direction ablation refusal direction control",
        "activation patching reference conditions zero mean random ablation",
    ],
    "P4_anchors": [
        "RefusalBench refusal rates benchmark 2026",
        "AIR-Bench safety benchmark 2024",
        "SORRY-Bench safety benchmark refusal",
        "StrongREJECT jailbreak evaluation benchmark",
        "safety leaderboard huggingface refusal rate Qwen3",
        "latent safety score model evaluation arxiv",
    ],
}

def run(query, mode, tag, max_results=8):
    out = subprocess.run(
        [PY, SCRIPT, "--query", query, "--mode", mode, "--max-results", str(max_results)],
        capture_output=True, text=True, timeout=90,
    )
    text = (out.stdout or "") + ("\n[STDERR] " + out.stderr if out.stderr else "")
    return text

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", default="scholarly")
    ap.add_argument("--sleep", type=float, default=4.0)
    ap.add_argument("--tag", default="phase1")
    ap.add_argument("--queries", default=None, help="comma list of query keys")
    args = ap.parse_args()
    logdir = Path("log"); logdir.mkdir(exist_ok=True)
    for key, qs in QUERIES.items():
        if args.queries and key not in args.queries.split(","):
            continue
        for i, q in enumerate(qs):
            fname = logdir / f"search_{args.tag}_{key}_{i}_{args.mode}.txt"
            print(f"[{time.strftime('%H:%M:%S')}] {key}[{i}] {q!r} -> {fname}", flush=True)
            try:
                text = run(q, args.mode, key)
            except Exception as e:
                text = f"ERROR: {e}"
            fname.write_text(f"QUERY: {q}\nMODE: {args.mode}\nTIME: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n{text}")
            time.sleep(args.sleep)
    print("DONE", flush=True)

if __name__ == "__main__":
    main()