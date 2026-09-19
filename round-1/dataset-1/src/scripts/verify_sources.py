#!/usr/bin/env python3
"""Verify downloaded source files: row counts, columns, label distributions."""
import csv
import json
from collections import Counter
from pathlib import Path

WS = Path(__file__).resolve().parent.parent
TD = WS / "temp/datasets"


def load_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def main() -> None:
    # ---- XSTest ----
    x = load_csv(TD / "xstest_prompts_raw.csv")
    print(f"XSTest csv: {len(x)} rows; cols={list(x[0].keys())}")
    print("  type dist:", Counter(r.get("type") or r.get("Type") or "?" for r in x).most_common(10))
    print("  sample:", {k: v for k, v in x[0].items()})

    # ---- HarmBench ----
    h = load_csv(TD / "harmbench_behaviors_text_all.csv")
    print(f"\nHarmBench csv: {len(h)} rows; cols={list(h[0].keys())}")
    catcol = "SemanticCategory" if "SemanticCategory" in h[0] else ("CategoryID" if "CategoryID" in h[0] else None)
    print("  category col:", catcol, Counter(r.get(catcol) for r in h).most_common(20) if catcol else "")
    print("  sample:", {k: v for k, v in h[0].items()})

    # ---- JBB behaviors ----
    jb = load_csv(TD / "jbb/data/harmful-behaviors.csv")
    print(f"\nJBB harmful-behaviors: {len(jb)} rows; cols={list(jb[0].keys())}")
    print("  sample:", {k: v for k, v in jb[0].items()})

    # ---- JBB attacks ----
    for name in ["dsn_vicuna13b", "gcg_gpt4", "jbc_gpt4", "pair_gpt4", "pws_gpt4"]:
        p = TD / "jbb_attacks" / f"{name}.json"
        try:
            d = json.loads(p.read_text())
        except FileNotFoundError:
            print(f"\nJBB attacks {name}: MISSING")
            continue
        if isinstance(d, dict):
            attacks = d.get("attacks", d)
            n = len(attacks)
            first = attacks[0] if isinstance(attacks, list) and attacks else list(attacks.items())[:1]
            print(f"JBB attacks {name}: {n} rows; type={type(attacks).__name__}; sample={str(first)[:200]}")
        elif isinstance(d, list):
            print(f"JBB attacks {name}: {len(d)} rows; sample keys={list(d[0].keys()) if d and isinstance(d[0], dict) else d[:1]}")

    # ---- dolly ----
    dp = TD / "dolly15k.jsonl"
    rows = [json.loads(l) for l in dp.read_text().splitlines()[:2000]]
    print(f"\ndolly15k: {sum(1 for _ in open(dp))} rows (sampled first 2000 for dist)")
    print("  sample keys:", list(rows[0].keys()))
    print("  context non-empty:", sum(1 for r in rows if r.get("context", "").strip()))


if __name__ == "__main__":
    main()