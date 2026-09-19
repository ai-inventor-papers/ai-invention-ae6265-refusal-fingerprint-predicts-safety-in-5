#!/usr/bin/env python3
"""Write .sdk_openhands_agent_struct_out.json (final structured artifact output)."""
import json
from pathlib import Path

WS = Path(__file__).resolve().parent.parent

out = {
    "title": "Safety Screening Prompts and Model Registry",
    "layman_summary": (
        "Prompt-only benchmark platform for measuring how LLMs handle unsafe requests: six disjoint prompt "
        "sets, a live-verified model zoo registry, published reference scores, and a pre-registered screening "
        "protocol. No model weights included."
    ),
    "summary": (
        "Single evidence platform the full safety-screen runs on; prompt text only (no weights), a few MB, CPU-only.\n"
        "\n"
        "DATA (928 rows, schema exp_sel_data_out, validated by aii-json; all sets disjoint by normalized-text dedup "
        "plus manual Jaccard review, 0 exact duplicates across sets):\n"
        "  refusal_120: 120 HarmBench-style refusal targets from the official centerforaisafety/HarmBench behavior "
        "CSV (MIT), seed 42 per-category quota over the 7 actual released SemanticCategories.\n"
        "  xstest: full 450-row XSTest-EN release (github.com/paul-rottger/xstest @ d7bb5bd, CC-BY-4.0; "
        "250 safe-label / 200 unsafe-label rows, each carrying type+label for downstream overrefusal subsets).\n"
        "  jailbreak: 60 rows = 30 (plain, jailbreak-wrapped) pairs, seed 123, 6 JBB behaviors x 5 attack engines "
        "(dsn/gcg/jbc/pair/pws from JailbreakBench/artifacts, MIT); dASR computable per pair.\n"
        "  contrast_base: 16 harmful/harmless pairs (32 rows) from HarmBench (seed 7, disjoint from refusal set), "
        "matched harmless rephrasings with documented transformation ids (payload_swap / topic_substitution / "
        "minimal_substitution), char_len within +/-25%.\n"
        "  contrast_membership: 186 rows, nested K-subsets for K in {1,2,4,8,16} x seeds {0,1,2} (K=1 subset of "
        "K=2 ... of K=16 per seed, verified by gate g3) so error-vs-K falls out of one file.\n"
        "  canonical: 5 fixed hand-written harmful prompts (bomb/malware/phishing/hate/synthesis), pinned, "
        "seeds null.\n"
        "  benign: 75 clearly-safe prompts (40 real databricks/dolly-15k CC BY-SA 3.0 instructions seed 7 + 35 "
        "in-house templates).\n"
        "\n"
        "MODEL REGISTRY (registry.json, 41 rows): 8 base + 8 instruct (Qwen/Qwen3-0.6B/1.7B/4B plus -Base, "
        "Qwen/Qwen2.5-0.5B/1.5B plus -Instruct, meta-llama/Llama-3.2-1B plus -Instruct, google/gemma-2-2b plus -it; "
        "official repo ids live-verified 2026-09-19 - the plan's Qwen3 '-Instruct' suffix 404s on HF, instruct = "
        "unsuffixed id whose card declares base_model Qwen3-{size}-Base) + 17 community abliterated (huihui-ai + "
        "mylesgoose + IlyaGusev; old huihui Qwen3-*-abliterated repos verified gated 403, Huihui-*/v2 repos "
        "public) + 8 self-abliteration specs (Arditi et al. 2024 hook-time residual-stream orthogonalization, "
        "alpha-scaled; grid alphas {0.25,0.5,0.75,1.0}). Every row carries num_layers / hidden_size / "
        "intermediate_size / num_attention_heads / num_key_value_heads / architectures / parameter_count (real "
        "totals from safetensors index metadata; GGUF-only rows inherit same-family totals, fallback documented "
        "per row) / chat_format / inference note / fold. Folds: screen=37, reserved=4 (Qwen3-8B pair + IlyaGusev "
        "gemma-2-2b-it-abliterated + off-grid alpha 0.35 self-ablit spec), never mixed (gate g5c).\n"
        "\n"
        "PRE-REGISTRATION (screen_protocol.json, written before any screen runs): 4 candidates - cand_fingerprint "
        "(per-layer potency profile from base-to-instruct activation differences on contrast pairs + onset + "
        "redundancy, nested K-subsets), cand_weightspec (task-vector spectral profile, zero prompts), "
        "cand_5prompt (refusal-vs-compliance logit gap on the canonical 5), cand_universal (projection of a "
        "refusal subspace onto benign-pool activations). Unified measure: leave-one-model-out Pearson r + "
        "Spearman rho vs refusal_rate / overrefusal_rate with permutation p over models (not prompts); 3-class "
        "alignment AUROC (base / instruct / abliterated, one-vs-rest) + self-ablit alpha-ordering Kendall tau; "
        "partial Spearman on refusal rate controlling log10(parameter_count). Mandatory baselines/controls: plain "
        "per-layer norm (no onset/redundancy), logit-scope behavioral baseline, random-direction perturbation "
        "control, randomized-initialization control. Selection margins: PASS if LOMO |rho| >= 0.85 on the refusal "
        "target across all 3 seeds (or >= 0.8 in every seed), alignment AUROC >= 0.90, K=8 within 1.5x the K=16 "
        "seed dispersion of the K=64 estimate, and candidate beats plain-norm + random controls by >= 0.1 |rho|; "
        "NARROWED if 0.6 <= |rho| < 0.85 (within-family only) or onset+redundancy add < 0.05 |rho| over plain "
        "norm; DISCONFIRMED below 0.6. Reserved-fold rule: evaluate once at the very end, never tune on it.\n"
        "\n"
        "REFERENCE SCORES (reference_scores.json): 11 rows computed from XSTest repo-shipped automated evaluation "
        "labels (model_completions/ plus gpteval/streval); N-GLARE (arXiv 2511.14195, ACL 2026; plan draft's "
        "2505.15010 corrected) checked on 2026-09-19 - no public per-zoo-model table found, nothing invented; "
        "cross-check layer only, behavioral targets are computed downstream by running the registered models.\n"
        "\n"
        "VALIDATION: scripts/verify.py -> logs/verify_final2.log, 15/15 gates green (schema shape, section "
        "counts, XSTest split, jailbreak pair count, nested-subset property per seed, exact disjointness + "
        "nearest cross-set pair review with 0 pairs above 0.6 Jaccard, registry repo resolution via model_info, "
        "layer/dim/fold on every row, fold disjointness, RNG determinism unit test (682 ids identical on re-run), "
        "row basics, token budget <=512 (max 495), file sizes < 5 MB). Every seed, source, license, commit SHA, "
        "and construction decision recorded in dataset_summary.md + manifest_sources.json; content warning "
        "included (harmful request text only, no model outputs).\n"
        "\n"
        "DELIVERABLES: data.py (canonical build entry) + full_data_out.json / mini_data_out.json / "
        "preview_data_out.json at workspace root; artifacts/ carries the same trio (data_out.json + variants), "
        "registry.json (+variants), screen_protocol.json, reference_scores.json (+variants), contrast_pairs.json, "
        "manifest_sources.json, dataset_summary.md, verify_output.log; pyproject.toml pins all 47 dependencies."
    ),
    "out_expected_files": {
        "script": "data.py",
        "datasets": [
            {
                "full": ["full_data_out.json"],
                "mini": "mini_data_out.json",
                "preview": "preview_data_out.json",
            }
        ],
    },
    "upload_ignore_regexes": [
        "(^|/)\\.venv/",
        "(^|/)temp/",
        "(^|/)logs/",
        "(^|/)__pycache__/",
        "(^|/)scripts/__pycache__/",
    ],
}

(WS / ".sdk_openhands_agent_struct_out.json").write_text(json.dumps(out, indent=2))
print("wrote", WS / ".sdk_openhands_agent_struct_out.json")