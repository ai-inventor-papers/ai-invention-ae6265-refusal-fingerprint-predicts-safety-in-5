#!/usr/bin/env python3
"""Final documentation pass: N-GLARE check note in reference_scores; manifest updates."""
import json
from datetime import datetime, timezone
from pathlib import Path

WS = Path(__file__).resolve().parent.parent
ART = WS / "artifacts"

NOW = datetime.now(timezone.utc).isoformat(timespec="seconds")

# --- reference_scores: add N-GLARE check note ---
p = ART / "reference_scores.json"
ref = json.loads(p.read_text())
note = (
    "N-GLARE (arXiv 2511.14195, ACL 2026; plan draft cited 2505.15010 - corrected): "
    "paper reports latent-separability safety evaluation on Qwen3-4B variants among 40+ models, "
    "but no public repo/per-model score table for this small zoo was found on 2026-09-19; "
    "no rows added (never invent values). XSTest rows below are computed from repo-shipped "
    "automated evaluation labels (model_completions/)."
)
if "metadata" not in ref:
    ref["metadata"] = {}
ref["metadata"]["notes_updated_at"] = NOW
ref["metadata"]["nglare_check"] = note
p.write_text(json.dumps(ref, indent=2))

# --- dataset_summary.md: refresh with final registry facts ---
reg = json.loads((ART / "registry.json").read_text())
rows = reg["datasets"][0]["examples"]
n_ablit = sum(1 for r in rows if r["metadata_variant_type"] == "abliterated")
n_self = sum(1 for r in rows if r["metadata_variant_type"] == "self-abliterated")
n_valid = sum(1 for r in rows if r.get("metadata_config_verified"))
lines = [
    "# Safety Screening Data Platform (manifest; also artifacts/manifest_sources.json)\n",
    f"**Last verified**: {NOW} (post-construct audit: registry re-verified live, "
    "parameter counts backfilled from safetensors index metadata).\n",
    "## Content warning",
    "Contains harmful REQUEST TEXT only (no model outputs). Standard benchmark data under permissive",
    "licenses (MIT / CC-BY-4.0 / CC BY-SA 3.0); intended for safety research.\n",
    "## Deliverables",
    "| file | content |",
    "|---|---|",
    "| artifacts/data_out.json (+full/mini/preview) | 7 prompt sections, 928 rows total (schema exp_sel_data_out) |",
    f"| artifacts/registry.json (+full/mini/preview) | {len(rows)} rows: 8 base + 8 instruct + {n_ablit} community abliterated + {n_self} self-ablit specs; {n_valid}/33 live config-verified; every row has layer/dim + parameter_count + fold |",
    "| artifacts/reference_scores.json (+full/mini/preview) | cross-check layer (not primary targets); N-GLARE checked, no public per-zoo table |",
    "| artifacts/screen_protocol.json | pre-registered protocol + selection margins |",
    "| artifacts/contrast_pairs.json | the 16 curated pairs (harmful/harmless + transformation ids) |",
    "| scripts/verify.py -> logs/verify_run3.log | 15/15 validation gates green |\n",
    "## Counts (verified)",
    "refusal_120=120 | xstest=450 (250 safe-label + 200 unsafe-label) |",
    "jailbreak=60 (30 pairs x 2 roles) | contrast_base=32 (16 pairs) |",
    "contrast_membership=186 (93 pair-instances x 2 roles) | canonical=5 | benign=75 (40 dolly + 35 templates)\n",
    "## Seeds",
    "refusal=42 (category quota), contrast=7, benign=7, jailbreak=123 (6 behaviors x 5 engines), K-subsets seeds={0,1,2} x K in {1,2,4,8,16}.\n",
    "## Sources & licenses (commit SHAs where captured)",
    "- **HarmBench**: github.com/centerforaisafety/HarmBench, `data/behavior_datasets/harmbench_behaviors_text_all.csv` (400 rows), license **MIT** (verified LICENSE file; plan expected CC-BY-4.0 - actual is MIT).",
    "- **XSTest**: github.com/paul-rottger/xstest @ d7bb5bd (git clone verified), `xstest_prompts.csv` (450 rows: 250 safe-label / 200 unsafe-label, 18 type classes), license **CC-BY-4.0** (verified). Refs: Rottger et al., NAACL 2024 (aclanthology 2024.naacl-long.301).",
    "- **JailbreakBench**: JBB-Behaviors `data/harmful-behaviors.csv` (100 rows), plus JailbreakBench/artifacts attack-artifacts (5 engines: dsn/gcg/jbc/pair/prompt_with_random_search), license **MIT** (both repos verified).",
    "- **dolly-15k**: databricks/databricks-dolly-15k (SHA bdd27f4d94b9...), license **CC BY-SA 3.0** (verified cc-by-sa-3.0).",
    "- XSTest repo also ships model_completions + automated evaluation labels -> harvested into reference_scores.json.\n",
    "## Verified deviations from plan (all documented, deterministic)",
    "1. **Qwen3 repo ids changed**: old 'Qwen/Qwen3-{size}-Instruct' ids no longer resolve on HF (404 with token; re-verified live 2026-09-19). Current official naming: 'Qwen/Qwen3-{size}' = instruct (card base_model: Qwen3-{size}-Base), 'Qwen/Qwen3-{size}-Base' = base. Registry uses verified ids.",
    "2. **XSTest canonical set**: walledai/XSTest and cais/harmbench model repos do not resolve (404) on HF Hub (checked 2026-09-19); used the official 450-row GitHub CSV (full released suite). All rows carry type/label for downstream subsetting.",
    "3. **HarmBench test cases not public**: released CSV has **7 coarse SemanticCategories** (copyright 100, cybercrime_intrusion 67, illegal 65, misinformation_disinformation 65, chemical_biological 56, harassment_bullying 25, harmful 22); the 13-class paper taxonomy is not in the released file; refusal-120 quota is per actual category. Decision: behavior text as prompt (HarmBench-style).",
    "4. **Plan's expected-config table partially wrong**: Qwen2.5-0.5B hidden_size is 896 (not 512); live config.json used everywhere (cross-check warned, kept config value). N-GLARE arXiv id corrected to 2511.14195.",
    "5. **Abliterated zoo**: live-verified 2026-09-19; huihui-ai + mylesgoose Qwen3/Qwen2.5/Llama-3.2/gemma variants are public (not gated); Qwen2.5-1.5B has no community abliterated under allowed authors -> 'not available' (self-ablit spec carries the family).",
    "6. **Parameter counts**: config.json does not expose num_parameters; backfilled from HF safetensors index metadata (real totals) on 2026-09-19; GGUF-only repos inherit same-family safetensors totals (documented per-row in metadata_config_fallback).",
    "7. **Self-abliteration spec rows** now inherit source instruct model architecture + parameter count (plan 3.5: layer/dim on every row) with usable_for_activation_hooks=true (hooks attach at experiment time).\n",
    "## Construction pseudocode",
    "```",
    "harmbench_csv -> refusal_120 (seed 42, per-category quota on 'standard' split, sorted by BehaviorID)",
    "              -> contrast harmful sides (seed 7, disjoint by BehaviorID + ngram-Jaccard<=0.6)",
    "contrast benign sides: hand-curated + transformation id (payload_swap / topic_substitution / minimal_substitution), char_len within +/-25%",
    "P = sorted pair ids; for seed in {0,1,2}: perm=RNG(seed); for K in {1,2,4,8,16}: subset=perm[:K] -> membership rows",
    "canonical: 5 hand-written fixed prompts",
    "benign: dolly-15k standalone instructions (seed 7, n=40) + 35 in-house templates",
    "xstest: official CSV verbatim (450 rows)",
    "jailbreak: 6 behavior indices (seed 123, disjoint) x 5 engines -> plain + wrapped rows",
    "registry: live model_info + config.json reads; folds screen/reserved never mixed; params from safetensors index",
    "```",
]
# save
(ART / "dataset_summary.md").write_text("\n".join(lines) + "\n")
print("wrote dataset_summary.md")
print("referce_scores note added")