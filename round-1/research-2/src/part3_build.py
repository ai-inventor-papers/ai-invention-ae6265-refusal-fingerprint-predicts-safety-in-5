"""Assemble research_out.json, research_report.md and .sdk_openhands_agent_struct_out.json."""
import json, sys, datetime
from pathlib import Path

WORK = Path(__file__).resolve().parent
sys.path.insert(0, str(WORK))

from part1_sources import SOURCES  # noqa: E402
from part2_answer import ANSWER  # noqa: E402

TITLE = "Model zoo and safety-score sources check"
LAYMAN = ("Verifies which small open-weights models exist on HuggingFace in fp16 under acceptable "
          "gating/licenses, collects their published safety scores, and documents chat templates so the "
          "activation-hooking experiment starts from a corrected model list.")
SUMMARY = (
    "Research artifact that de-risks the downstream activation-hooking experiment by resolving, with fetched evidence, the "
    "entire open-weights model zoo. Key corrections: (1) Qwen3 has no 1.8B and no Qwen3-{size}-Instruct repo ids at all — the "
    "official post-trained (safety-finetuned) models ARE Qwen/Qwen3-{size} (2504, thinking default ON) plus the ungated "
    "Qwen/Qwen3-4B-Instruct-2507 refresh; the plan's '1.8B' is corrected to 1.7B. (2) All 4 huihui-ai Qwen3 v2 abliterated "
    "repos (0.6B/1.7B/4B/8B) exist ungated as fp16 safetensors, so the held-out 8B triple and the whole within-family design "
    "are executable; the only gated huihui variant is v1 (gated='auto', contact-info). (3) huihui's Qwen2.5/Llama-3.2 "
    "abliterated repos are no longer public; fp16 replacements are the Goekdeniz-Guelmez Josiefied series (Qwen2.5) and "
    "mylesgoose (Llama-3.2). (4) meta-llama/Llama-3.2-1B and google/gemma-2-2b(-it) are gated=manual (token + license "
    "acceptance) with ungated fallbacks (unsloth mirror for Llama base; Miiyamoto255 and benniepie for Gemma abliterated). "
    "Delivered per-repo availability matrix (exists/gated/license/fp16-vs-GGUF-only/layers/hidden + evidence URL), corrected "
    "machine-readable zoo, external safety scores (N-GLARE covers Qwen2.5-0.5B/1.5B-Instruct and gemma-2-2b-it; XSTest and "
    "HarmBench MISSING for the zoo; saturation flags: abliterated rows expect floor saturation), and verbatim "
    "chat-template/thinking-mode facts (enable_thinking default True, literal ' thinking'/' response' stream markers, token "
    "151668, /think /no_think, no greedy decoding; huihui v2 tokenizer has NO chat_template — must be injected; Llama and "
    "Gemma template quirks quoted). Everything is evidence-backed with UNVERIFIED marks where applicable."
)
FOLLOW_UPS = [
    "Gated rows (meta-llama/Llama-3.2-1B, google/gemma-2-2b(-it)): is the run allowed to use an HF token + license acceptance for the official checkpoints, or must it stay fully anonymous and use the ungated fallbacks (unsloth base mirror; mylesgoose/Miiyamoto255 abliterated), dropping the official instruct row of those two families?",
    "Should the Qwen3 'instruct' class be standardized as Qwen/Qwen3-{size} (2504 post-trained, thinking default ON) with Qwen/Qwen3-4B-Instruct-2507 as the optional non-thinking 4B refresh, and should the new latent metric be evaluated head-to-head against N-GLARE's JSS on the shared model subset as a required baseline?",
    "N-GLARE's per-model JSS numbers are only in scatter figures (no machine-readable table): do we need to extract them (figure/PDF mining) or is the plan's own fixed ~120-prompt reference refusal-rate set plus XSTest-EN sufficient as the primary behavioral target?",
]

out = {
    "title": TITLE,
    "layman_summary": LAYMAN,
    "summary": SUMMARY,
    "answer": ANSWER,
    "sources": SOURCES,
    "follow_up_questions": FOLLOW_UPS,
    "out_expected_files": {"output": "research_out.json"},
    "upload_ignore_regexes": ["(^|/)__pycache__/"],
}

# Validate source indices 1..N unique
idxs = sorted(s["index"] for s in SOURCES)
assert idxs == list(range(1, len(SOURCES) + 1)), "source index gap: %r" % idxs

research_out = {
    "title": TITLE,
    "answer": ANSWER,
    "sources": SOURCES,
    "follow_up_questions": FOLLOW_UPS,
    "summary": SUMMARY,
    "generated": datetime.datetime.utcnow().isoformat() + "Z",
    "note": "Research artifact (gen_art_research_2_idx3): model zoo + safety score sources. Raw evidence files under evidence/.",
}
(WORK / "research_out.json").write_text(json.dumps(research_out, indent=1, ensure_ascii=False), encoding="utf-8")
(WORK / ".sdk_openhands_agent_struct_out.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")

# Narrative report
report = """# Model zoo and safety-score sources — research report

**Artifact:** gen_plan_research_2_idx3 (research) · **Date:** 2026-09-19 · **Method:** pure web research (HuggingFace API, raw config.json/tokenizer_config.json/README fetches, primary pages, leaderboard page checks). No weights downloaded, no inference, no LLM APIs.

## Summary of headline findings
1. **Qwen3 has no 1.8B and no `Qwen3-{size}-Instruct` repos.** The post-trained (safety-finetuned) dense models ARE `Qwen/Qwen3-{size}` (2504, thinking default ON, Apache-2.0, ungated); `Qwen/Qwen3-4B-Instruct-2507` is the ungated non-thinking 4B refresh. The plan's '1.8B' must be corrected to 1.7B.
2. **The full triple zoo is executable for Qwen3 0.6B/1.7B/4B/8B:** `Qwen3-{size}-Base` (ungated fp16) / `Qwen3-{size}` (post-trained) / `huihui-ai/Huihui-Qwen3-{size}-abliterated-v2` (all four ungated fp16). The held-out 8B pair is fully resolved.
3. **huihui-ai Qwen2.5/Llama-3.2 abliterated repos are gone (401/absent from search);** fp16 substitutes: Goekdeniz-Guelmez/Josiefied-* (Qwen2.5) and mylesgoose (Llama-3.2).
4. **Gated rows:** meta-llama/Llama-3.2-1B(-Instruct) and google/gemma-2-2b(-it) are gated=manual — HF token + license acceptance; ungated fallbacks listed per row. huihui v1 is gated='auto' but v2 is not.
5. **External scores are sparse but N-GLARE (ACL 2026) covers 4 zoo-adjacent models** (Qwen2.5-0.5B-Instruct, Qwen2.5-1.5B-Instruct, gemma-2-2b-it, Llama-3.2-3B-Instruct) and uses the Qwen3-4B base/aligned/safety-removed triple in its motivating figure; XSTest and HarmBench have no zoo entries (MISSING). Saturation: abliterated rows expect floor saturation (design intent).
6. **Template traps:** Qwen3 thinking trace is literal text in the token stream (` thinking` / ` response`, token 151668), enable_thinking=True default, no greedy decoding; huihui v2 tokenizer_config has NO chat_template (inject it); Gemma template rejects system role and requires alternating roles.

## Availability matrix
(Full per-role matrix with exists/gated/license/fp16-vs-GGUF/layers/hidden/evidence is in the `answer` of `research_out.json`; every row was verified via `<repo>/api/models` JSON, raw `config.json`, `tokenizer_config.json` or `README.md` fetches with recorded HTTP status. Cross-family config table: Qwen3-0.6B(-Base) 28/1024/16/8, Qwen3-1.7B(-Base) 28/2048/16/8, Qwen3-4B(-Base) 36/2560/32/8, Qwen3-8B(-Base) 36/4096/32/8; Qwen2.5-0.5B 24/896/14/2, Qwen2.5-1.5B 28/1536/12/2; Llama-3.2-1B 16/2048/32/8; Gemma-2-2b(-it) 26/2304/8/4, head_dim 256.)

## External safety scores
See the score table in `research_out.json` answer Section 3 (N-GLARE JSS ranks for 4 zoo-adjacent models with UNVERIFIED exact values; XSTest/HarmBench MISSING; StrongREJECT/AIR-Bench/HELM UNVERIFIED; saturadion flags on abliterated rows).

## Fallback matrix
- `Qwen3-1.8B(-Instruct)` → `Qwen/Qwen3-1.7B(-Base / plain)` (official family) [6, 7].
- Qwen3 'instruct' roles → `Qwen/Qwen3-{size}` (2504) or `Qwen/Qwen3-4B-Instruct-2507` (non-thinking 4B refresh) [8, 10].
- huihui Qwen2.5 abliterated → `Goekdeniz-Guelmez/Josiefied-Qwen2.5-{0.5B,1.5B}-Instruct-abliterated-v{1,2}` [36, 37].
- huihui Llama-3.2 abliterated → `mylesgoose/Llama-3.2-1B-Instruct-abliterated` [38].
- Llama-3.2-1B base (gated) → `unsloth/Llama-3.2-1B` (ungated mirror) [22].
- Llama-3.2-1B instruct (gated) → accept gating with token, or size-substitute `Llama-3.2-3B-Instruct` (has N-GLARE scores) [42].
- Gemma-2-2b(-it) (gated) → accept gating with token; abliterated ungated: `Miiyamoto255/SimplyAI-2B-Uncensored` (it-derived), `benniepie/gemma` (base-derived) [25, 40]. GGUF-only mirrors flagged UNUSABLE for hooking.
- Option note: if any abliterated role cannot be obtained in fp16, self-abliteration (Arditi-style orthogonalization on the base+instruct weights) remains available in the experiment iteration.

## Known traps (for the experiment iteration)
1. Do NOT request `Qwen/Qwen3-{size}-Instruct` — the id 401s like a nonexistent repo; use `Qwen/Qwen3-{size}`.
2. huihui v2 tokenizers ship without `chat_template` → inject the Qwen3 jinja before `apply_chat_template`; verify `enable_thinking` kwargs work with their tokenizer.
3. Qwen3 thinking mode: thinking tokens are part of the generation stream (prompt-adjacent positions for the 'onset' feature); NEVER greedy-decode in thinking mode (endless repetition); disable via `enable_thinking=False` or `/no_think` for the non-thinking conditions.
4. Gated repos return 401 for raw config.json even when the API metadata is public — the harness will need `HF_TOKEN` for meta-llama and google repos.
5. Gemma-2 template: no system role (raises exception), strict user/assistant alternation, `<end_of_turn>` required for well-formed turns.
6. Expected saturation: abliterated rows at the unsafe floor — keep them as anchor rows, don't fit regressions to them alone.
7. N-GLARE (ACL 2026 Long 1334) already occupies 'latent-only safety eval without generation'; differentiate (e.g., benign-only prompts, calibrated risk score, 0–few prompts) or cite it as the incumbent baseline.

## Sources
All 44 sources with URLs and per-fact traceability are in `research_out.json` (field `sources`). Key ones: HF APIs/collections for every repo [1-5, 10-30, 34-40], official Qwen3 GitHub README [6] and blog [7], Qwen3-4B card+templia [8, 9], huihui cards/tokenizers [31-33], HF search API [41], N-GLARE [42], XSTest [43], HarmBench [44].
"""
(WORK / "research_report.md").write_text(report, encoding="utf-8")

# quick self-check
chk = json.loads((WORK / ".sdk_openhands_agent_struct_out.json").read_text(encoding="utf-8"))
assert chk["title"] and chk["layman_summary"] and chk["summary"] and chk["answer"] and chk["sources"] and chk["follow_up_questions"]
for s in chk["sources"]:
    assert set(s) >= {"index", "url", "title", "summary"}
    for p in s.get("supporting_passages", []):
        assert p.get("quote"), s["url"]
print("OK: research_out.json, research_report.md, .sdk_openhands_agent_struct_out.json written and validated")
print("bytes:", len(ANSWER), "answer;", len(SOURCES), "sources")