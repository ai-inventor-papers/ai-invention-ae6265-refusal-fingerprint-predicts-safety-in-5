#!/usr/bin/env python3
"""Check reserved-fold rows and all reference_scores rows."""
import json
from pathlib import Path

WS = Path(__file__).resolve().parent.parent
ART = WS / "artifacts"


def main() -> None:
    reg = json.loads((ART / "registry.json").read_text())
    ex = reg["datasets"][0]["examples"]
    print("=== reserved fold rows ===")
    for row in ex:
        if row.get("metadata_fold") == "reserved":
            print(
                row.get("metadata_repo_id"), "|", row.get("metadata_variant_type"),
                "|", row.get("metadata_size_label"),
            )
            if "alpha" in str(row.get("input", "")):
                print("   input:", row.get("input")[:120])

    ref = json.loads((ART / "reference_scores.json").read_text())
    rex = ref["datasets"][0]["examples"]
    print("\n=== all reference_scores rows (compact) ===")
    for row in rex:
        meta = {k: v for k, v in row.items() if k.startswith("metadata_")}
        print(meta.get("metadata_model_repo_id", "?"), "|",
              meta.get("metadata_benchmark", "?"), "|",
              meta.get("metadata_metric", "?"), "|",
              meta.get("metadata_value", "?"), "|",
              meta.get("metadata_confidence", "?"), "|",
              str(meta.get("metadata_source_url", ""))[:50])


if __name__ == "__main__":
    main()