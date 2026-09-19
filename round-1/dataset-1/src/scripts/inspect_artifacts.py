#!/usr/bin/env python3
"""Inspect final artifacts (registry, reference_scores, temp sources)."""
import json
from collections import Counter
from pathlib import Path

WS = Path(__file__).resolve().parent.parent
ART = WS / "artifacts"


def main() -> None:
    # --- registry ---
    reg = json.loads((ART / "registry.json").read_text())
    ex = reg["datasets"][0]["examples"]
    print(f"registry rows: {len(ex)}")
    for row in ex[:10]:
        print(
            row.get("metadata_repo_id"), "|",
            row.get("metadata_variant_type"), "|",
            row.get("metadata_gated"), "|",
            row.get("metadata_config_verified"), "|",
            row.get("metadata_fold"), "|",
            "L", row.get("metadata_num_layers"), "H", row.get("metadata_hidden_size"), "|",
            str(row.get("metadata_architectures"))[:45],
        )
    print("\nvariant counts:", Counter(x.get("metadata_variant_type") for x in ex))
    print("folds:", Counter(x.get("metadata_fold") for x in ex))
    missing = [x.get("metadata_repo_id") for x in ex
               if not x.get("metadata_num_layers") or not x.get("metadata_hidden_size")]
    print("missing layer/dim:", missing)

    # --- reference scores ---
    ref = json.loads((ART / "reference_scores.json").read_text())
    rex = ref["datasets"][0]["examples"]
    print(f"\nreference rows: {len(rex)}")
    for row in rex:
        print(
            row.get("metadata_model_repo_id") or row.get("metadata_repo_id"), "|",
            row.get("metadata_benchmark", ""), "|",
            row.get("metadata_metric", ""), "|",
            row.get("metadata_value", ""), "|",
            str(row.get("metadata_source_url", ""))[:55], "| conf:",
            row.get("metadata_confidence", ""),
        )

    # --- temp sources ---
    print("\n--- temp/datasets ---")
    for p in sorted((WS / "temp/datasets").rglob("*")):
        if p.is_file() and p.suffix in (".json", ".csv", ".jsonl"):
            print(f"{p.relative_to(WS / 'temp')}  {p.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()