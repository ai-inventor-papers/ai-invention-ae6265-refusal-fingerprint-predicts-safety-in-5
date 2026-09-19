#!/usr/bin/env python3
"""Deeper registry/reference inspection."""
import json
from pathlib import Path

WS = Path(__file__).resolve().parent.parent
ART = WS / "artifacts"


def main() -> None:
    reg = json.loads((ART / "registry.json").read_text())
    ex = reg["datasets"][0]["examples"]
    print("=== rows missing layer/dim (or value==0/None) ===")
    for row in ex:
        L, H = row.get("metadata_num_layers"), row.get("metadata_hidden_size")
        if not L or not H:
            print(
                row.get("metadata_repo_id"), "|",
                row.get("metadata_variant_type"), "|",
                "L:", L, "H:", H, "| src:", row.get("metadata_source_url", "")[:60],
            )
    print("\n=== self-abliterated spec rows (3) ===")
    n = 0
    for row in ex:
        if row.get("metadata_variant_type") == "self-abliterated" and n < 3:
            print(json.dumps(row, indent=1)[:900])
            n += 1
    print("\n=== abliterated rows (first 4) ===")
    n = 0
    for row in ex:
        if row.get("metadata_variant_type") == "abliterated" and n < 4:
            print(
                row.get("metadata_repo_id"), "| L:", row.get("metadata_num_layers"),
                "H:", row.get("metadata_hidden_size"), "| verified:",
                row.get("metadata_config_verified"), "| gun:", row.get("metadata_gated"),
                "| hooks:", row.get("metadata_usable_for_activation_hooks"),
            )
            n += 1

    ref = json.loads((ART / "reference_scores.json").read_text())
    rex = ref["datasets"][0]["examples"]
    print("\n=== reference_scores first row full ===")
    print(json.dumps(rex[0], indent=1))


if __name__ == "__main__":
    main()