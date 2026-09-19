#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Assemble research_out.json, research_report.md, .sdk_openhands_agent_struct_out.json.
Run from the artifact workspace root."""
import json, sys, os
from datetime import date
from sources_data import SOURCES
from answer_text import TITLE, LAYMAN_SUMMARY, SUMMARY, FOLLOWUPS, ANSWER

WS = "/ai-inventor/aii_data/runs/run_fEjgpc8BQoQS/3_invention_loop/iter_2/gen_art/gen_art_research_1"

# ---- sanity checks -------------------------------------------------------
idx = [s["index"] for s in SOURCES]
assert idx == list(range(1, len(SOURCES) + 1)), "source index continuity"
cited = set()
for m in __import__("re").finditer(r"\[(\d+(?:\s*,\s*\d+)*)\]", ANSWER):
    for tok in m.group(1).split(","):
        cited.add(int(tok.strip()))
missing = sorted(cited - set(idx))
assert not missing, f"answer cites undefined source indices: {missing}"
used = sorted(cited)
print(f"sources={len(SOURCES)} cited={len(used)} unused={sorted(set(idx)-cited)}")

# ---- research_out.json (same fields as the sdk struct) --------------------
out = {
    "title": TITLE,
    "layman_summary": LAYMAN_SUMMARY,
    "summary": SUMMARY,
    "out_expected_files": {"output": "research_out.json"},
    "upload_ignore_regexes": ["(^|/)__pycache__/", "(^|/)qenv/", "(^|/)cache/"],
    "answer": ANSWER,
    "sources": SOURCES,
    "follow_up_questions": FOLLOWUPS,
}
with open(os.path.join(WS, "research_out.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)

# ---- .sdk_openhands_agent_struct_out.json ---------------------------------
sdk = {
    "title": TITLE,
    "layman_summary": LAYMAN_SUMMARY,
    "summary": SUMMARY,
    "out_expected_files": {"output": "research_out.json"},
    "upload_ignore_regexes": ["(^|/)__pycache__/", "(^|/)qenv/", "(^|/)cache/"],
    "answer": ANSWER,
    "sources": SOURCES,
    "follow_up_questions": FOLLOWUPS,
}
with open(os.path.join(WS, ".sdk_openhands_agent_struct_out.json"), "w", encoding="utf-8") as f:
    json.dump(sdk, f, ensure_ascii=False, indent=1)

# ---- research_report.md ---------------------------------------------------
report = f"""# Research report - write-up support pack for the safety-fingerprint paper

Artifact: gen_art_research_1 (iter_2). Executed 2026-09-19 (all URLs accessed this date).
Companion machine-readable output: `research_out.json` (same content, JSON).

## 0. Pre-flight summary
- Mech-interp handbook read; randomized-baseline norm (S9), knowledge-action gap (S3) and the write-up-time saturation directive applied; S-numbers cited where they ground requirements.
- Deps (iter_1) reused as binding: zoo matrix, Qwen3 naming/thinking facts, prior-art inventory. Re-checked at primary source where the plan demanded it (AMS sigma bands, N-GLARE venue id, dASR term).
- Pre-registered margins read from `gen_art_experiment_1/artifacts/screen_protocol.json` (LOMO |rho|>=0.85, OVR AUROC>=0.90, K-scaling 1.5x dispersion rule, random-direction + randomized-init controls, partial Spearman log10-param covariates, fragility-vs-dASR partial Spearman>=0.5, N=200 judge validation).
- Executed margin numbers: NOT FOUND in the run tree (no exp_eval outputs) -> Phase 6 positioning written as conditionals and marked PROVISIONAL.
- Contrast-pair construction in `contrast_pairs.json` uses transformation "topic_substitution" -> interacts with the topic-matched-contrast finding below (Contradiction Flag F4).

## 1. Saturation-search verdict table (six guards) + per-guard detail
(Table and detail identical to Section 1 of `research_out.json` answer; reproduced there verbatim.)

Summary verdicts:
| Guard | Verdict | Key prior executed claim (citation) |
|---|---|---|
| G1 potency profiles | FOUND-RELATED | per-layer cosine curves [23]; single optimal layer AMS [13]; layer windows [15]; write-sites [24] |
| G2 onset | FOUND-RELATED | first-half response window [20]; write-site decodability AUROC 0.99 [24] |
| G3 redundancy | FOUND-RELATED | dominant+orthogonal directions [17]; category directions + shared knob [43]; rank-1..12 residue [21] |
| G4 class-ID | FOUND-EXECUTED | AMS sigma bands/taxonomy [13,14]; audit AUROC 0.95 n=273 [16]; family-ID 100% n=76 [19] |
| G5 K-scaling | NOT-FOUND-IN-THIS-SEARCH | neighbors: 128/32 Arditi [23]; 16 pairs AMS [13]; few-hundred prompts [21]; contrast-baseline effect [18] |
| G6 dose-response | FOUND-RELATED | LVS/audit-gap [22]; random-orthogonal controls [21,24]; defenses perturbing the signal [39,40] |

Per-guard detail: see `research_out.json` Section 1 (G1-G6 blocks with queries, candidates, quotes, delta, positioning sentences, confidence).

## 2. Randomized-baseline citations (B1-B5) with one-line applicability
- B1 Hewitt & Liang 2019, D19-1275 [27]: control-task/selectivity norm -> our randomized-init arm cannot encode the concept by construction.
- B2 Arditi et al. 2024, 2406.11717 [23, 59]: directional ablation x' <- x - rhat rhat^T x; the orthogonalized random-direction control is now standard [24, 21] -> our random-direction perturbation baseline.
- B3 Heap et al. 2025, 2501.17727 [25]: random transformers score like trained on auto-interp metrics -> our UNCONDITIONAL randomized-initialization control.
- B4 Sutter et al. 2025, 2507.08802, NeurIPS 2025 Spotlight [26]: unrestricted alignment maps vacuous -> our frozen difference-of-means estimate is a constrained map.
- B5 Heimersheim & Turner 2024, 2404.15255 [28]: activation-patching reference conditions; circuit breakers [29] for intervention-sweep tradition.

## 3. Evaluator pins, verbatim (Phase 3)
Reproduced verbatim in `research_out.json` Section 3 with locators. Key facts:
- HarmBench: classifier default cais/HarmBench-Llama-2-13b-cls [1,3]; binary yes/no labels, label-1=behavior-instance [4]; 512-token truncation, temperature 0, 1 token [3]; per-behavior mean then unweighted mean over behaviors [3]; LLAMA2_CLS_PROMPT full text in source 4; commit pin 8e1604d [2].
- JailbreakBench: ASR via Llama3-70B jailbreak judge ('unsafe' positive) and Llama3-8B refusal judge ('Yes') with verbatim prompts [5,6]; 'dASR' occurs 0 times in [7] and [8] -> convention must be pinned explicitly (Flag F3).
- XSTest: 450 prompts; 'contrast_' = unsafe [9]; strmatch prefixes [10]; GPT-4 3-class rubric verbatim [11]; repo rows only for its 5 legacy models [12,55]; zoo coverage still MISSING (checked 2026-09-19).

## 4. External-anchor table (Phase 4)
See `research_out.json` Section 4. Highlights: N-GLARE zoo rows figure-only (Qwen2.5-0.5B/1.5B-Instruct, gemma-2-2b-it) [31]; AMS per-class sigma bands re-fetched from primary source (4.7-8.4 / 3.3 / 1.1-1.3 / 0.7; calibrated on 15 models x 4 architectures) [13]; AMS per-model sigma published for Llama-3.1-abliterated (3.33), Gemma-2-9b-abliterated (4.54), DarkIdol (5.45) [14]; RefusalBench frontier-only [33]; HarmBench rows predate the zoo [56]; XSTest anchors for 5 non-zoo models [12,55].

## 5. Statistical conventions (Phase 5)
As in `research_out.json` Section 5: model-level LOMO permutation (B=100k, two-sided |rho|, p=(1+#extreme)/(1+B), MC-SE, 10k-vs-100k stability check; scipy) [45,50,51,60]; partial Spearman via pingouin + residual cross-check [46,52,53]; Cohen's kappa via sklearn with kappa+accuracy+confusion+CI and Landis&Koch bands [47,48,49]; raw pre-registered p with optional Holm sensitivity.

## 6. Positioning paragraphs (Phase 6) - PROVISIONAL
Full paragraphs (vs N-GLARE, AMS, RAS/SafeVec, and short notes vs GradSafe/RefusalBench/off-target effects) in `research_out.json` Section 6, written as PASS/NARROWED conditionals because no executed margin numbers existed at write time.

## 7. CONTRADICTION-FLAGS (adjust framing, never margins)
F1 class-ID AUROC already executed (0.95 binary [16]; 100% family-ID [19]); F2 AMS executed sigma-vs-compliance correlations r=-0.546/rho=-0.423 far below our |rho|>=0.85 target [14] - must be discussed; F3 'dASR' undefined in canonical sources [7,8] - pin the behavioral-ASR convention; F4 topic-matched contrast baseline failure [18] vs our topic-substitution pairs; F5 AMS threshold basis is 15 models/4 architectures, not the dep's 14 configs [13]; F6 no published numeric anchors for zoo rows (XSTest/N-GLARE figure-only/HarmBench predates) [12,31,56]; F7 fingerprint-evasion defenses AMRA + Fool's Gold [39,40]; F8 activation-only detection ceiling (AMS class-4 [14]; LVS dissociated models [22]).

## 8. Search-log appendix (queries + dates)
Full query list with timestamps (2026-09-19 04:32-04:39 UTC) in `research_out.json` Section 8; per-guard queries and the general lookups are enumerated there, including engine glitches (OpenAlex miss on AIR-Bench resolved via arXiv API; Sumandora raw README fetch timed out twice and was dropped, with the tool-dose sub-point covered by the cross-architecture comparison paper [41]).

---
Generated {date.today().isoformat()} by gen_art_research_1 (build_outputs.py). Confidence statement and QA checklist in `research_out.json` Section 8/9.
"""
with open(os.path.join(WS, "research_report.md"), "w", encoding="utf-8") as f:
    f.write(report)

print("WROTE:", "research_out.json", "research_report.md", ".sdk_openhands_agent_struct_out.json")
print("answer chars:", len(ANSWER), "| sources:", len(SOURCES), "| followups:", len(FOLLOWUPS))