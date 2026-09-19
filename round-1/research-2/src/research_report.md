# Model zoo and safety-score sources check

## Summary

Research artifact that de-risks the downstream activation-hooking experiment by resolving, with fetched evidence, the entire open-weights model zoo. Key corrections: (1) Qwen3 has no 1.8B and no Qwen3-{size}-Instruct repo ids at all — the official post-trained (safety-finetuned) models ARE Qwen/Qwen3-{size} (2504, thinking default ON) plus the ungated Qwen/Qwen3-4B-Instruct-2507 refresh; the plan's '1.8B' is corrected to 1.7B. (2) All 4 huihui-ai Qwen3 v2 abliterated repos (0.6B/1.7B/4B/8B) exist ungated as fp16 safetensors, so the held-out 8B triple and the whole within-family design are executable; the only gated huihui variant is v1 (gated='auto', contact-info). (3) huihui's Qwen2.5/Llama-3.2 abliterated repos are no longer public; fp16 replacements are the Goekdeniz-Guelmez Josiefied series (Qwen2.5) and mylesgoose (Llama-3.2). (4) meta-llama/Llama-3.2-1B and google/gemma-2-2b(-it) are gated=manual (token + license acceptance) with ungated fallbacks (unsloth mirror for Llama base; Miiyamoto255 and benniepie for Gemma abliterated). Delivered per-repo availability matrix (exists/gated/license/fp16-vs-GGUF-only/layers/hidden + evidence URL), corrected machine-readable zoo, external safety scores (N-GLARE covers Qwen2.5-0.5B/1.5B-Instruct and gemma-2-2b-it; XSTest and HarmBench MISSING for the zoo; saturation flags: abliterated rows expect floor saturation), and verbatim chat-template/thinking-mode facts (enable_thinking default True, literal ' thinking'/' response' stream markers, token 151668, /think /no_think, no greedy decoding; huihui v2 tokenizer has NO chat_template — must be injected; Llama and Gemma template quirks quoted). Everything is evidence-backed with UNVERIFIED marks where applicable.

## Research Findings

# Model zoo and safety-score sources — research findings (checked 2026-09-19; all repo facts from the HuggingFace API, raw config.json / tokenizer_config.json / README fetches, and primary pages)

## 1. Availability matrix (every row: role | repo_id | exists | gated | license | fp16 safetensors | GGUF-only? | n_layers | hidden_size | evidence)

### Qwen3 — CRITICAL NAMING CORRECTION: the hypothesised `Qwen3-1.8B` and `Qwen3-{size}-Instruct` repo ids DO NOT EXIST
| role | repo_id | exists | gated | license | fp16 st | gguf-only | layers | hidden | ev |
|---|---|---|---|---|---|---|---|---|---|
| base 0.6B | Qwen/Qwen3-0.6B-Base | yes | false | apache-2.0 | 1 file | no | 28 | 1024 | [11, 7] |
| post-trained 0.6B (instruct role) | Qwen/Qwen3-0.6B | yes | false | apache-2.0 | 1 file | no | 28 | 1024 | [1, 7] |
| abliterated 0.6B | huihui-ai/Huihui-Qwen3-0.6B-abliterated-v2 | yes | false | apache-2.0 | 1 file | no | 28 | 1024 | [27]; alt mlabonne [34] |
| base 1.7B | Qwen/Qwen3-1.7B-Base | yes | false | apache-2.0 | 1 file | no | 28 | 2048 | [12, 7] |
| post-trained 1.7B (instruct role) | Qwen/Qwen3-1.7B | yes | false | apache-2.0 | 2 shards | no | 28 | 2048 | [2, 7] |
| abliterated 1.7B | huihui-ai/Huihui-Qwen3-1.7B-abliterated-v2 | yes | false | apache-2.0 | 1 file | no | 28 | 2048 | [28]; v1 gated=auto [33]; alt mlabonne [35] |
| base 4B | Qwen/Qwen3-4B-Base | yes | false | apache-2.0 | 3 shards | no | 36 | 2560 | [13, 7] |
| instruct 4B (2504) | Qwen/Qwen3-4B | yes | false | apache-2.0 | 3 shards | no | 36 | 2560 | [3, 8] |
| instruct 4B (2507 refresh) | Qwen/Qwen3-4B-Instruct-2507 | yes | false | apache-2.0 | 3 shards | no | 36 | 2560 | [10, 6] |
| abliterated 4B | huihui-ai/Huihui-Qwen3-4B-abliterated-v2 | yes | false | apache-2.0 | 2 shards | no | 36 | 2560 | [29, 31] |
| base 8B | Qwen/Qwen3-8B-Base | yes | false | apache-2.0 | 5 shards | no | 36 | 4096 | [14, 7] |
| post-trained 8B (instruct role; HELD-OUT pair) | Qwen/Qwen3-8B | yes | false | apache-2.0 | 5 shards | no | 36 | 4096 | [4, 7] |
| abliterated 8B (HELD-OUT pair) | huihui-ai/Huihui-Qwen3-8B-abliterated-v2 | yes | false | apache-2.0 | 4 shards | no | 36 | 4096 | [30] |

Why the correction is certain: (a) the official Qwen3 HF collection (84 items) lists only `Qwen3-{size}`, `Qwen3-{size}-Base`, quantized/MLX variants, and `-Instruct-2507`/`-Thinking-2507` for 4B/30B-A3B/235B-A22B only [5, 6]; (b) direct API calls to `Qwen/Qwen3-0.6B-Instruct` … `Qwen3-8B-Instruct` and `Qwen3-1.8B` return 401 `Invalid username or password`, byte-identical to a control call to a nonexistent repo (`Qwen/Qwen3-999B`) [1, 2, 3, 4, 41]; (c) the HF search API, which DOES surface gated repos such as meta-llama, does not return these ids [41]; (d) the Qwen3 blog/README family lists have no 1.8B and no per-size Instruct naming for 2504 [6, 7]. The official 'safety-finetuned' class of Qwen3 2504 dense models IS `Qwen/Qwen3-{size}` itself — its card states 'Training Stage: Pretraining & Post-training' with `base_model: Qwen/Qwen3-4B-Base` [8, 3]. All Qwen3 repos (including Qwen3-4B-Instruct-2507, ~4.0M downloads) are ungated Apache-2.0 [5, 10]. Config values fetched from raw config.json match the plan's priors exactly; -Base variants are identical architectures with 32K context [11, 12, 13, 14, 7].

### Qwen2.5 — fully ungated Apache-2.0; the least-risk family
| role | repo_id | exists | gated | license | fp16 st | layers | hidden | ev |
|---|---|---|---|---|---|---|---|---|
| base 0.5B | Qwen/Qwen2.5-0.5B | yes | false | apache-2.0 | 1 file | 24 | 896 | [15] |
| instruct 0.5B | Qwen/Qwen2.5-0.5B-Instruct | yes | false | apache-2.0 | 1 file | 24 | 896 | [17, 15] |
| abliterated 0.5B | Goekdeniz-Guelmez/Josiefied-Qwen2.5-0.5B-Instruct-abliterated-v1 | yes | false | apache-2.0 | 1 file | 24 | 896 | [37] |
| base 1.5B | Qwen/Qwen2.5-1.5B | yes | false | apache-2.0 | 1 file | 28 | 1536 | [16] |
| instruct 1.5B | Qwen/Qwen2.5-1.5B-Instruct | yes | false | apache-2.0 | 1 file | 28 | 1536 | [18, 16] |
| abliterated 1.5B | Goekdeniz-Guelmez/Josiefied-Qwen2.5-1.5B-Instruct-abliterated-v2 (or -v3) | yes | false | apache-2.0 | 1 file | 28 | 1536 | [36] |

Note: huihui-ai's own `Qwen2.5-*-Instruct-abliterated` and `Llama-3.2-1B-Instruct-abliterated` repos are NO LONGER PUBLIC (direct API 401, absent from HF search) [41]; the Goekdeniz-Guelmez 'Josiefied' series and mylesgoose are the fp16 replacements.

### Llama-3.2-1B — gated family (HF token + Llama 3.2 license acceptance required for the official checkpoints)
| role | repo_id | exists | gated | license | fp16 st | layers | hidden | ev |
|---|---|---|---|---|---|---|---|---|
| base | meta-llama/Llama-3.2-1B | yes | manual | llama3.2 | 1 file | 16 | 2048 | [19, 21] |
| instruct | meta-llama/Llama-3.2-1B-Instruct | yes | manual | llama3.2 | 1 file | 16 | 2048 | [20, 21] |
| abliterated | mylesgoose/Llama-3.2-1B-Instruct-abliterated | yes | false | llama3.2 | 1 file | 16 | 2048 | [38, 39] |
| base FALLBACK (ungated) | unsloth/Llama-3.2-1B | yes | false | llama3.2 | 1 file | 16 | 2048 | [22, 21] |

Architecture values were read from the ungated unsloth mirror config because the official config.json 401s without a token [21, 19, 20].

### Gemma-2-2b — gated family (HF token + Gemma license acceptance required for the official checkpoints)
| role | repo_id | exists | gated | license | fp16 st | layers | hidden | ev |
|---|---|---|---|---|---|---|---|---|
| base | google/gemma-2-2b | yes | manual | gemma | 3 shards | 26 | 2304 | [23, 25] |
| instruct | google/gemma-2-2b-it | yes | manual | gemma | 2 shards | 26 | 2304 | [24, 25] |
| abliterated (it-derived, ungated) | Miiyamoto255/SimplyAI-2B-Uncensored | yes | false | gemma | 2 shards | 26 | 2304 | [25] |
| abliterated (base-derived, ungated) | benniepie/gemma (gemma-2-2b-OBLITERATED) | yes | false | (no license tag) | 2 shards | 26 | 2304 | [40] |

Gemma-2-2b-it's architecture (26 layers / 2304 hidden / 8 attn / 4 kv heads, head_dim 256, 8K ctx, bf16) comes from the SimplyAI mirror config whose `_name_or_path` is `google/gemma-2-2b-it` [25]; the official config is gated [24]. WARNING (flagged, not silently dropped): known Gemma-2-2b-it abliterated mirrors exist GGUF-only (e.g., a `bartowski/gemma-2-2b-it-abliterated-GGUF` search hit) — GGUF repos are UNUSABLE for residual-stream activation hooking; prefer the fp16 repos above and re-check file lists at load time [see search results this pass; exact file inventory of that GGUF repo UNVERIFIED].

## 2. Corrected zoo — machine-readable rows for the experiment planner (model | size | variant | repo_id | blocked? | note)

```
qwen3|0.6B|base|Qwen/Qwen3-0.6B-Base|no|ungated fp16 1 file [11]
qwen3|0.6B|instruct|Qwen/Qwen3-0.6B|no|official post-trained model; thinking default ON [1, 8]; '-Instruct' id does not exist [5]
qwen3|0.6B|abliterated|huihui-ai/Huihui-Qwen3-0.6B-abliterated-v2|no|ungated fp16 [27]
qwen3|1.7B|base|Qwen/Qwen3-1.7B-Base|no|ungated [12]
qwen3|1.7B|instruct|Qwen/Qwen3-1.7B|no|hypothesis '1.8B' CORRECTED to 1.7B [6, 7]
qwen3|1.7B|abliterated|huihui-ai/Huihui-Qwen3-1.7B-abliterated-v2|no|ungated v2 [28]; v1 gated=auto [33]
qwen3|4B|base|Qwen/Qwen3-4B-Base|no|ungated [13]
qwen3|4B|instruct|Qwen/Qwen3-4B|no|2504 post-trained; matches huihui v2 base [3, 31]; optional newer: Qwen3-4B-Instruct-2507 (non-thinking only) [10]
qwen3|4B|abliterated|huihui-ai/Huihui-Qwen3-4B-abliterated-v2|no|ungated fp16 [29]
qwen3|8B|base|Qwen/Qwen3-8B-Base|no|held-out pair OK [14]
qwen3|8B|instruct|Qwen/Qwen3-8B|no|held-out pair OK; no '-Instruct' id [4, 5]
qwen3|8B|abliterated|huihui-ai/Huihui-Qwen3-8B-abliterated-v2|no|held-out pair OK [30]
qwen2.5|0.5B|base|Qwen/Qwen2.5-0.5B|no|ungated [15]
qwen2.5|0.5B|instruct|Qwen/Qwen2.5-0.5B-Instruct|no|ungated [17]
qwen2.5|0.5B|abliterated|Goekdeniz-Guelmez/Josiefied-Qwen2.5-0.5B-Instruct-abliterated-v1|no|ungated fp16; huihui variant gone [37, 41]
qwen2.5|1.5B|base|Qwen/Qwen2.5-1.5B|no|ungated [16]
qwen2.5|1.5B|instruct|Qwen/Qwen2.5-1.5B-Instruct|no|ungated [18]
qwen2.5|1.5B|abliterated|Goekdeniz-Guelmez/Josiefied-Qwen2.5-1.5B-Instruct-abliterated-v2|no|ungated fp16 [36]
llama-3.2|1B|base|meta-llama/Llama-3.2-1B|YES-gated|needs HF token + Llama 3.2 license; ungated fallback: unsloth/Llama-3.2-1B [22]
llama-3.2|1B|instruct|meta-llama/Llama-3.2-1B-Instruct|YES-gated|needs token + license; size-substitute option: Llama-3.2-3B-Instruct has published N-GLARE scores [42]
llama-3.2|1B|abliterated|mylesgoose/Llama-3.2-1B-Instruct-abliterated|no|ungated fp16, llama3.2 license [38]
gemma-2|2b|base|google/gemma-2-2b|YES-gated|needs token + Gemma license; no clean ungated fp16 base mirror found this pass
gemma-2|2b|instruct|google/gemma-2-2b-it|YES-gated|needs token + Gemma license; GGUF mirrors exist but are unusable for hooking
gemma-2|2b|abliterated|Miiyamoto255/SimplyAI-2B-Uncensored|no|ungated fp16, gemma license, it-derived [25]; alt benniepie/gemma base-derived [40]
```

DROPPED rows: `Qwen3-1.8B` / `Qwen3-1.8B-Instruct` (never existed) [6, 7]; all `Qwen/Qwen3-{size}-Instruct` ids (nonexistent) [5]; huihui-ai `Qwen2.5-0.5B/1.5B-Instruct-abliterated` and `Llama-3.2-1B-Instruct-abliterated` (no longer public) [41]. Every other role is resolved with an evidence-backed row; the only BLOCKED rows are the official Llama-3.2-1B and Gemma-2-2b checkpoints (gating), each with concrete fallbacks.

## 3. External behavioral safety scores (sparse coverage is a legitimate finding — the run computes its own reference rates on a fixed ~120-prompt subset plus XSTest-EN)

| model | benchmark | metric | value | direction | source |
|---|---|---|---|---|---|
| Qwen2.5-0.5B-Instruct | N-GLARE (ACL 2026; arXiv 2511.14195) | JSS latent-separability rank (abbr. INS-0.5B) | ranked among ~40 models; exact JSS values are in scatter figures only → UNVERIFIED as text | higher JSS = more aligned/safer | [42] |
| Qwen2.5-1.5B-Instruct | N-GLARE | JSS rank (QWE-1.5B) | same situation | higher = safer | [42] |
| gemma-2-2b-it | N-GLARE | JSS rank (GEM-2B) | same situation | higher = safer | [42] |
| Llama-3.2-3B-Instruct | N-GLARE | JSS rank (LLA-3B) | nearest Llama-3.2 member (no 1B in the set) | higher = safer | [42] |
| Llama-3.2-1B(-Instruct) | XSTest (NAACL 2024) | overrefusal rate | MISSING — paper tested Llama2-70b-chat, Mistral-7B-Instruct-v0.1, GPT-4 only | lower = safer | [43] |
| Qwen3 family; Qwen2.5-0.5B/1.5B; Gemma-2-2b base | XSTest | overrefusal rate | MISSING (not in the paper's model set) | lower = safer | [43] |
| all zoo models | HarmBench leaderboard (2026-09-19) | ASR | MISSING — no entries for Qwen3/Qwen2.5-small/Llama-3.2-1B/Gemma-2-2b in the page text | lower = safer | [44] |
| all zoo models | StrongREJECT / AIR-Bench 2024 / HELM Safety | safety rate / ASR | MISSING — published tables cover larger models; not re-verified in machine-readable detail this pass (UNVERIFIED) | — | [42, 43] |
| Qwen3-4B aligned/base/safety-removed | N-GLARE Fig. 1 | JSS separability | qualitative: 'better-aligned variants exhibit more pronounced geometric separation' | higher = safer | [42] |
| gemma-2-2b-it | Gemma-2 model card | safety evaluation | card contains 'Ethics and Safety / Evaluation Results' headings but no numeric rows extractable from page HTML this pass → UNVERIFIED | — | [24] |
| huihui/abliterated variants | huihui & mlabonne cards | refusal-rate tests | MISSING — cards describe method only, no refusal numbers published | — | [31, 33, 34, 38] |

SATURATION FLAGS: (a) abliterated/uncensored variants are design-intent floor-saturated (refusal ≈ 0); no numeric published confirmation exists, so treat as expected floor rows and verify with the run's own reference set [31, 33, 38]. (b) N-GLARE Table 4 reports JSS changes PRECEDE surface metrics (JSS vs Refusal-Rate lag in 74% of trajectories, median shift −4.4), i.e., latent safety signals lead behavior — directly relevant to the experiment's 'onset' feature and dose-response analysis [42]. No near-0%/near-100% numeric scores exist for these exact models to flag numerically.

MOST IMPORTANT EXTERNAL ANCHOR: N-GLARE [42] is already a non-generative, latent-representation safety evaluator that ranks ~40 models by Jensen-Shannon Separability at <1% of red-teaming cost, and its motivating figure explicitly uses the Qwen3-4B base / aligned / safety-removed triple [42]. Any new few-prompt latent metric must differentiate from JSS to be novel: JSS needs full generation trajectories contrasting jailbreak-vs-benign prompts; a candidate differentiator is 0–few BENIGN prompts, no jailbreak prompts needed, outputting a calibrated risk score for unseen models.

## 4. Chat-template and thinking-mode conventions (quoted from primary sources)

Qwen3 2504 post-trained (Qwen3-0.6B/1.7B/4B/8B):
- Template location: `tokenizer_config.json` → `chat_template` (jinja; 4168 chars — the 0.6B and 4B files are identical in length and thinking-handling) [9]. Message framing: `<|im_start|>{role}
…<|im_end|>`; the generation prompt is literally `'<|im_start|>assistant
'` [9].
- The thinking trace is LITERAL TEXT INSIDE THE TOKEN STREAM — there are NO special thinking tokens. The template conditionally emits the plain-text markers `' thinking

 response

'` (verbatim from the jinja's `add_generation_prompt` branch, guarded by `enable_thinking is defined and enable_thinking is false`) [9]. The ` response` substring is token id 151668 per the Qwen3-4B README ("rindex finding 151668 ( response)"), and the README describes generated output as "think content wrapped in a ` thinking... response` block" [8].
- Thinking default: `enable_thinking=True # Switches between thinking and non-thinking modes. Default is True.` — passed via `tokenizer.apply_chat_template(..., chat_template_kwargs={"enable_thinking": ...})` [8].
- Disable: hard switch `enable_thinking=False` or soft switch `/no_think` in a user/system message when thinking is on; `/think` re-enables; the most recent instruction wins [8, 6].
- Sampling: thinking mode — "DO NOT use greedy decoding" (recommended T=0.6, TopP=0.95, TopK=20, MinP=0); non-thinking suggested T=0.7, TopP=0.8, TopK=20 [8].
- Qwen3-4B-Instruct-2507 (the 2507 refresh) is non-thinking only: "specifying `enable_thinking=False` is no longer required" [6].

huihui-ai Qwen3 abliterated v2:
- Method: abliteration per Sumandora's remove-refusals-with-transformers ("This is an uncensored version of Qwen/Qwen3-4B created with abliteration"); "Ablation was performed using a new and faster method"; "Changed the 0 layer to eliminate the problem of garbled codes" [31]. No per-layer/alpha disclosure (method depth UNVERIFIED).
- Base = the post-trained `Qwen/Qwen3-4B` (2504) [31, 29]; thinking mode retained (ollama page documents `/set think` and `/set nothink`) [31].
- PITFALL: v2's `tokenizer_config.json` has NO `chat_template` field [32] — the harness must inject the Qwen3 template (copy from the Qwen3 source repo's tokenizer_config) or apply_chat_template will fail/fall back; also verify chat-template kwargs work on their tokenizer at load time.

Llama-3.2-1B-Instruct:
- Template tokens (from the mirror tokenizer_config, same template family as the official gated repo): `<|begin_of_text|>` (bos), `<|start_header_id|>`, `<|end_header_id|>`, `<|eot_id|>`; `model_max_length` 131072 [39].

Gemma-2-2b-it:
- Template (verbatim facts from the it-derived mirror's `chat_template` field, quoted in source 26): the prompt starts with `bos_token`; each turn is `<start_of_turn>{user|model}
{content}<end_of_turn>
`; a system message raises the exception 'System role not supported'; conversation roles must alternate user/assistant; `add_generation_prompt` emits `<start_of_turn>model
` [26]. Pitfalls: no system role is allowed; strict role alternation; every turn (including the last) ends with `<end_of_turn>`.

## 5. Blockers and what unblocks them
- `meta-llama/Llama-3.2-1B` and `-Instruct`: gated=manual; unblock = HF account + accept the Llama 3.2 Community License + `HF_TOKEN` [19, 20]. Ungated alternative for base: `unsloth/Llama-3.2-1B` [22]; abliterated instruct already ungated: `mylesgoose/…` [38].
- `google/gemma-2-2b` and `-it`: gated=manual; unblock = HF account + accept the Gemma license + `HF_TOKEN` [23, 24]. Ungated abliterated alternatives exist [25, 40]; no clean ungated fp16 official mirror found this pass.
- `huihui-ai/Qwen3-1.7B-abliterated` (v1): gated='auto' → requires click-through + sharing contact info, but v2 is ungated so this is NON-blocking [33, 28].
- No `Qwen3-{size}-Instruct` ids → not a gating problem, a naming correction [5].

## Confidence and what would change it
HIGH confidence on everything in Sections 1, 2, 4 and 5: every repo row rests on a direct API/config/card fetch with HTTP status recorded this session; architecture values came from fetched config.json files and the official blog. The Qwen3 '-Instruct does not exist' conclusion is inferred (401 on API = identical to our nonexistent-repo control; absent from collection and from search that does surface gated repos) — if HF later reintroduces `Qwen3-{size}-Instruct` ids (e.g., a future 2507-style refresh for more sizes), re-resolve. MEDIUM confidence on Section 3: N-GLARE per-model JSS numbers live in figures (values UNVERIFIED as text), per-model refusal/ASR numbers for these small models are sparse-to-absent in all checked leaderboards (marked MISSING/UNVERIFIED), and the harmbench check was page-text only. Saturation flags for abliterated rows are design-intent priors, not measured scores. Everything unverifiable is flagged; nothing was fabricated.

## Sources

[1] [HF API: Qwen/Qwen3-0.6B](https://huggingface.co/api/models/Qwen/Qwen3-0.6B) — Exists, gated=false, Apache-2.0, single model.safetensors (fp16), no GGUF; tags base_model:Qwen/Qwen3-0.6B-Base; ~22.5M downloads; tokenizer_config has full chat_template jinja.

[2] [HF API: Qwen/Qwen3-1.7B](https://huggingface.co/api/models/Qwen/Qwen3-1.7B) — Exists, gated=false, Apache-2.0, 2 safetensors shards fp16; config 28 layers / 2048 hidden / 16 heads / 8 kv.

[3] [HF API: Qwen/Qwen3-4B](https://huggingface.co/api/models/Qwen/Qwen3-4B) — Exists, gated=false, Apache-2.0, 3 safetensors shards fp16; config 36 / 2560 / 32 / 8; README: Training Stage 'Pretraining & Post-training', base_model Qwen3-4B-Base.

[4] [HF API: Qwen/Qwen3-8B](https://huggingface.co/api/models/Qwen/Qwen3-8B) — Exists, gated=false, Apache-2.0, 5 safetensors shards fp16; config 36 / 4096 / 32 / 8.

[5] [HF API: official Qwen3 collection (84 items)](https://huggingface.co/api/collections/Qwen/qwen3-67dd247413f0e2e4f653967f) — Official repo inventory. No Qwen3-{size}-Instruct repos exist for the 2504 dense family; all dense/base/2507 items are gated=false, including Qwen3-4B-Instruct-2507 (gated=false, ~4.0M downloads), Qwen3-4B-Thinking-2507, and the Qwen3-{size}-Base repos.

[6] [Qwen3 GitHub README (QwenLM/Qwen3)](https://github.com/QwenLM/Qwen3) (Qwen Team; 2025) — Family = 0.6B/1.7B/4B/8B/14B/32B dense + 30B-A3B/235B-A22B MoE, Apache 2.0; 2507 refresh only for 235B-A22B/30B-A3B/4B (Instruct-2507 = non-thinking, Thinking-2507 = thinking); Instruct-2507 needs no enable_thinking=False; /think and /no_think soft switches; links Qwen/Qwen3-4B-Instruct-2507.

> available in 0.6B, 1.7B, 4B, 8B, 14B, 32B and 30B-A3B, 235B-A22B

Locator: Qwen3 (aka Qwen3-2504) section, dense/MoE model list

[7] [Qwen3 blog: Think Deeper, Act Faster](https://qwenlm.github.io/blog/qwen3/) (Qwen Team; 2025) — Architecture table: Qwen3-0.6B 28L, Q/KV 16/8, tie embeddings, 32K ctx; 1.7B 28L 16/8 32K; 4B 36L 32/8 32K; 8B 36L 32/8 128K (no tie); 14B 40L, 32B 64L; MoE 30B-A3B 48L 32/4 128/8 experts 128K, 235B-A22B 94L 64/4 128/8 128K; dense family under Apache 2.0; hybrid thinking/non-thinking modes; -Base = pre-trained counterparts.

> Qwen3 models introduce a hybrid approach to problem-solving.

Locator: Key Features — Hybrid Thinking Modes

[8] [Qwen3-4B model card README (raw)](https://huggingface.co/Qwen/Qwen3-4B/raw/main/README.md) — Training Stage: Pretraining & Post-training; base_model Qwen/Qwen3-4B-Base; 36 layers, 32 Q / 8 KV heads (GQA); enable_thinking=True default via tokenizer.apply_chat_template chat_template_kwargs; thinking output wrapped in ' thinking... response' block; ' response' token id 151668; /think /no_think soft switches; DO NOT use greedy decoding in thinking mode (T=0.6/TopP 0.95/TopK 20/MinP 0); non-thinking T=0.7/TopP 0.8/TopK 20.

> enable_thinking=True # Switches between thinking and non-thinking modes. Default is True.

Locator: code example

> In this mode, the model will generate think content wrapped in a

Locator: ## Switching Between Thinking and Non-Thinking Mode (full sentence: '...wrapped in a ` thinking... response` block, followed by the final response.')

> **DO NOT use greedy decoding**, as it can lead to performance degradation and endless repetitions.

Locator: thinking-mode sampling note

[9] [Qwen3-0.6B tokenizer_config.json (raw)](https://huggingface.co/Qwen/Qwen3-0.6B/resolve/main/tokenizer_config.json) — Full Qwen3 chat_template jinja (4168 chars; byte-identical length and thinking-handling in Qwen3-4B's file too): message framing <|im_start|>{role}\n...<|im_end|>; generation prompt is '<|im_start|>assistant\n'; the template conditionally emits the literal plain-text markers ' thinking\n\n response\n\n' when enable_thinking is false; there are NO special thinking tokens — the thinking trace is plain text in the token stream.

> enable_thinking is defined and enable_thinking is false

Locator: chat_template jinja, add_generation_prompt branch

[10] [HF API: Qwen/Qwen3-4B-Instruct-2507](https://huggingface.co/api/models/Qwen/Qwen3-4B-Instruct-2507) — Exists, gated=false, Apache-2.0, 3 safetensors shards fp16; official updated 4B instruct (non-thinking only per Qwen3 GitHub README).

[11] [HF API: Qwen/Qwen3-0.6B-Base](https://huggingface.co/api/models/Qwen/Qwen3-0.6B-Base) — Exists, gated=false, Apache-2.0, 1 safetensors; raw config.json fetched: 28 layers / 1024 hidden / 16 heads / 8 kv, bf16, 32K.

[12] [HF API: Qwen/Qwen3-1.7B-Base](https://huggingface.co/api/models/Qwen/Qwen3-1.7B-Base) — Exists, gated=false, Apache-2.0, 1 safetensors; raw config.json fetched: 28 / 2048 / 16 / 8, bf16, 32K.

[13] [HF API: Qwen/Qwen3-4B-Base](https://huggingface.co/api/models/Qwen/Qwen3-4B-Base) — Exists, gated=false, Apache-2.0, 3 safetensors; raw config.json fetched: 36 / 2560 / 32 / 8, bf16, 32K.

[14] [HF API: Qwen/Qwen3-8B-Base](https://huggingface.co/api/models/Qwen/Qwen3-8B-Base) — Exists, gated=false, Apache-2.0, 5 safetensors; raw config.json fetched: 36 / 4096 / 32 / 8, bf16, 32K.

[15] [HF API: Qwen/Qwen2.5-0.5B](https://huggingface.co/api/models/Qwen/Qwen2.5-0.5B) — Exists, gated=false, Apache-2.0, 1 safetensors; config: 24 / 896 / 14 heads / 2 kv, model_type qwen2.

[16] [HF API: Qwen/Qwen2.5-1.5B](https://huggingface.co/api/models/Qwen/Qwen2.5-1.5B) — Exists, gated=false, Apache-2.0, 1 safetensors; config: 28 / 1536 / 12 / 2, qwen2.

[17] [HF API: Qwen/Qwen2.5-0.5B-Instruct](https://huggingface.co/api/models/Qwen/Qwen2.5-0.5B-Instruct) — Exists, gated=false, Apache-2.0, 1 safetensors.

[18] [HF API: Qwen/Qwen2.5-1.5B-Instruct](https://huggingface.co/api/models/Qwen/Qwen2.5-1.5B-Instruct) — Exists, gated=false, Apache-2.0, 1 safetensors.

[19] [HF API: meta-llama/Llama-3.2-1B](https://huggingface.co/api/models/meta-llama/Llama-3.2-1B) — Exists, gated=manual (license acceptance required), license:llama3.2, 1 safetensors; API metadata public, but raw files/config.json return 401 without auth.

[20] [HF API: meta-llama/Llama-3.2-1B-Instruct](https://huggingface.co/api/models/meta-llama/Llama-3.2-1B-Instruct) — Exists, gated=manual, license:llama3.2, 1 safetensors; raw files 401 without auth.

[21] [unsloth/Llama-3.2-1B config.json (raw)](https://huggingface.co/unsloth/Llama-3.2-1B/resolve/main/config.json) — Ungated mirror of Llama-3.2-1B; config fetched: 16 layers / 2048 hidden / 32 heads / 8 kv, bf16, model_type llama (used because the official config.json is gated).

[22] [HF API: unsloth/Llama-3.2-1B](https://huggingface.co/api/models/unsloth/Llama-3.2-1B) — Ungated (gated=false), license:llama3.2, 1 safetensors — concrete non-gated fallback for the Llama-3.2-1B base role.

[23] [HF API: google/gemma-2-2b](https://huggingface.co/api/models/google/gemma-2-2b) — Exists, gated=manual, license:gemma, 3 safetensors; files 401 without auth.

[24] [HF API: google/gemma-2-2b-it](https://huggingface.co/api/models/google/gemma-2-2b-it) — Exists, gated=manual, license:gemma, 2 safetensors; files 401 without auth; model card has an 'Ethics and Safety / Evaluation Results' section but no numeric rows extractable from the page HTML this pass.

[25] [Miiyamoto255/SimplyAI-2B-Uncensored config.json (raw)](https://huggingface.co/Miiyamoto255/SimplyAI-2B-Uncensored/resolve/main/config.json) — Ungated community uncensored variant whose _name_or_path is google/gemma-2-2b-it; confirms gemma-2-2b-it architecture: 26 layers / 2304 hidden / 8 heads / 4 kv, head_dim 256, max_position_embeddings 8192, bf16 (official config is gated).

[26] [Miiyamoto255/SimplyAI-2B-Uncensored tokenizer_config.json (raw)](https://huggingface.co/Miiyamoto255/SimplyAI-2B-Uncensored/resolve/main/tokenizer_config.json) — Gemma-2 chat template verbatim from chat_template field: bos_token; '<start_of_turn>' + role + '\n' + content + '<end_of_turn>\n'; system role raises 'System role not supported'; roles must alternate; add_generation_prompt emits '<start_of_turn>model\n'.

> {{ bos_token }}{% if messages[0]['role'] == 'system' %}{{ raise_exception('System role not supported') }}{% endif %}

Locator: chat_template field (start)

[27] [HF API: huihui-ai/Huihui-Qwen3-0.6B-abliterated-v2](https://huggingface.co/api/models/huihui-ai/Huihui-Qwen3-0.6B-abliterated-v2) — Exists, gated=false, Apache-2.0, 1 safetensors; base_model tags point to Qwen/Qwen3-0.6B.

[28] [HF API: huihui-ai/Huihui-Qwen3-1.7B-abliterated-v2](https://huggingface.co/api/models/huihui-ai/Huihui-Qwen3-1.7B-abliterated-v2) — Exists, gated=false, Apache-2.0, 1 safetensors; base_model tags point to Qwen/Qwen3-1.7B.

[29] [HF API: huihui-ai/Huihui-Qwen3-4B-abliterated-v2](https://huggingface.co/api/models/huihui-ai/Huihui-Qwen3-4B-abliterated-v2) — Exists, gated=false, Apache-2.0, 2 safetensors shards; its config.json: 36 / 2560 / 32 / 8, bf16 — same as Qwen3-4B.

[30] [HF API: huihui-ai/Huihui-Qwen3-8B-abliterated-v2](https://huggingface.co/api/models/huihui-ai/Huihui-Qwen3-8B-abliterated-v2) — Exists, gated=false, Apache-2.0, 4 safetensors shards; config 36 / 4096 — same as Qwen3-8B. Held-out pair abliterated row resolved.

[31] [huihui-ai/Huihui-Qwen3-4B-abliterated-v2 README (raw)](https://huggingface.co/huihui-ai/Huihui-Qwen3-4B-abliterated-v2/raw/main/README.md) — 'An uncensored version of Qwen/Qwen3-4B created with abliteration (see remove-refusals-with-transformers...)'; 'Ablation was performed using a new and faster method'; 'Changed the 0 layer to eliminate the problem of garbled codes'; ollama tag huihui_ai/qwen3-abliterated:4b-v2 with '/set think and /set nothink' — Qwen3 thinking mode retained. No refusal-rate benchmark numbers on the card.

> This is an uncensored version of [Qwen/Qwen3-4B](https://huggingface.co/Qwen/Qwen3-4B) created with abliteration (see [remove-refusals-with-transformers](https://github.com/Sumandora/remove-refusals-with-transformers) to know more about it).

Locator: model card body

> Ablation was performed using a new and faster method, which yields better results.

Locator: model card body

> Changed the 0 layer to eliminate the problem of garbled codes

Locator: model card body

[32] [huihui-ai/Huihui-Qwen3-4B-abliterated-v2 tokenizer_config.json (raw)](https://huggingface.co/huihui-ai/Huihui-Qwen3-4B-abliterated-v2/resolve/main/tokenizer_config.json) — NO chat_template field in tokenizer_config.json (keys enumerated) — unlike the stock Qwen3 repos; the Qwen3 chat template must be injected by the harness or copied from the source Qwen repo's tokenizer_config.

[33] [huihui-ai/Qwen3-1.7B-abliterated (v1) — gated variant](https://huggingface.co/huihui-ai/Qwen3-1.7B-abliterated) — The gated huihui variant: HF API gated='auto', Apache-2.0, 1 safetensors; page banner text 'You need to agree to share your contact information to access this model'. The ungated v2 (index 28) supersedes it.

> You need to agree to share your contact information to access this model

Locator: gating banner (search-indexed page text)

[34] [HF API: mlabonne/Qwen3-0.6B-abliterated](https://huggingface.co/api/models/mlabonne/Qwen3-0.6B-abliterated) — Exists, gated=false, Apache-2.0, 1 safetensors; abliterated from Qwen/Qwen3-0.6B (per card: 'uncensored version of Qwen/Qwen3-0.6B').

[35] [HF API: mlabonne/Qwen3-1.7B-abliterated](https://huggingface.co/api/models/mlabonne/Qwen3-1.7B-abliterated) — Exists, gated=false, Apache-2.0, 3 safetensors; abliterated from Qwen/Qwen3-1.7B.

[36] [HF API: Goekdeniz-Guelmez/Josiefied-Qwen2.5-1.5B-Instruct-abliterated-v2](https://huggingface.co/api/models/Goekdeniz-Guelmez/Josiefied-Qwen2.5-1.5B-Instruct-abliterated-v2) — Exists, gated=false, Apache-2.0, 1 safetensors; uncensored Qwen2.5-1.5B-Instruct variant (v1->v2->v3 chain visible in tags). huihui-ai's own Qwen2.5-1.5B-Instruct-abliterated is no longer public (index 41).

[37] [HF API: Goekdeniz-Guelmez/Josiefied-Qwen2.5-0.5B-Instruct-abliterated-v1](https://huggingface.co/api/models/Goekdeniz-Guelmez/Josiefied-Qwen2.5-0.5B-Instruct-abliterated-v1) — Exists, gated=false, Apache-2.0, 1 safetensors; base_model tag Qwen/Qwen2.5-0.5B-Instruct.

[38] [HF API: mylesgoose/Llama-3.2-1B-Instruct-abliterated](https://huggingface.co/api/models/mylesgoose/Llama-3.2-1B-Instruct-abliterated) — Exists, gated=false, license:llama3.2, 1 safetensors — ungated fp16 abliterated Llama-3.2-1B-Instruct. The huihui-ai/Llama-3.2-1B-Instruct-abliterated repo is no longer public (only GGUF mirrors remain).

[39] [mylesgoose/Llama-3.2-1B-Instruct-abliterated tokenizer_config.json (raw)](https://huggingface.co/mylesgoose/Llama-3.2-1B-Instruct-abliterated/resolve/main/tokenizer_config.json) — Standard Llama-3.2 chat template tokens present in the jinja: <|start_header_id|>, <|end_header_id|>, <|eot_id|> (plus <|begin_of_text|> as the bos token); model_max_length 131072. Same template family as meta-llama/Llama-3.2-1B-Instruct.

[40] [HF API: benniepie/gemma (gemma-2-2b-OBLITERATED)](https://huggingface.co/api/models/benniepie/gemma) — Exists, gated=false, 2 safetensors; base_model google/gemma-2-2b — abliterated from the BASE checkpoint (not IT), method 'advanced' via OBLITERATUS.

[41] [HF search API: abliterated Qwen2.5 / Llama-3.2 queries](https://huggingface.co/api/models?search=Qwen2.5-1.5B-Instruct-abliterated&limit=10) — Ground truth that huihui-ai/Qwen2.5-1.5B-Instruct-abliterated, huihui-ai/Qwen2.5-0.5B-Instruct-abliterated and huihui-ai/Llama-3.2-1B-Instruct-abliterated do NOT appear in HF search results and return 401 on direct API (same error as a nonexistent-repo control) — removed from public access; search surfaces Goekdeniz-Guelmez and mylesgoose fp16 alternatives instead. Also: search API DOES include gated repos (meta-llama appears), so absence is meaningful.

[42] [N-GLARE: A Non-Generative Latent Representation-Efficient LLM Safety Evaluator (Lin, Yang, Qiu et al.)](https://arxiv.org/html/2511.14195) (Zheyu Lin, Jirui Yang, Yukui Qiu; 2025) — Non-generative latent safety evaluator: whitened-PCA benign manifold + Angular-Probabilistic Trajectories + JSS (Jensen-Shannon Separability); ~40 models, 20 red-teaming strategies; <1% token/runtime cost; model set (Table 5) includes Qwen/Qwen2.5-0.5B-Instruct (INS-0.5B), Qwen2.5-1.5B-Instruct (QWE-1.5B), gemma-2-2b-it (GEM-2B), Llama-3.2-3B-Instruct (LLA-3B); Figure 1 uses Qwen3-4B aligned/base/safety-removed variants; Table 4 shows JSS changes precede surface metrics (JSS vs RR lag in 74% of trajectories); per-model JSS numbers are in scatter figures (not machine-readable text). ACL 2026 Long paper 2026.acl-long.1334.

> when comparing multiple variants of the same base model (e.g., RL-aligned, base, and safety-removed versions of Qwen3-4B), we observe that better-aligned variants exhibit more pronounced geometric separation between different trajectories in latent space.

Locator: Figure 1 caption

> Experiments on over 40 models and 20 red teaming strategies demonstrate that the JSS metric exhibits high consistency with Red Teaming safety rankings at less than 1% token and runtime cost.

Locator: Abstract

[43] [XSTest: A Test Suite for Identifying Exaggerated Safety Behaviours in Large Language Models (Rottger et al., NAACL 2024)](https://aclanthology.org/2024.naacl-long.301.pdf) (Paul Rottger, Hannah Rose Kirchner; 2024) — Original XSTest evaluated Llama2-70b-chat, Mistral-7B-Instruct-v0.1 and GPT-4 (Section 4.1); none of the current zoo models (Qwen3, Qwen2.5-0.5B/1.5B, Llama-3.2-1B, Gemma-2-2b) appear, so per-model XSTest overrefusal rates for the zoo are MISSING from this source.

> We test the state-of-the-art LLMs

Locator: Section 4.1 Model Setup (full sentence lists Llama2, Mistral-7B and GPT-4)

[44] [HarmBench leaderboard page (fetched 2026-09-19)](https://www.harmbench.org/leaderboard) — Leaderboard HTML contains no entries for Qwen3, Qwen2.5-0.5B/1.5B, Llama-3.2-1B or Gemma-2-2b (grep over the page text for these ids returned nothing) — published ASR coverage for these zoo models is MISSING here.

## Verification

Numbered citations resolve to unique listed sources. Passage checks test text occurrence, not claim truth or entailment. Author/year metadata and locators are not independently verified. Details: `research_verification.json`.

- Source [6]: text found — available in 0.6B, 1.7B, 4B, 8B, 14B, 32B and 30B-A3B, 235B-A22B
- Source [7]: text found — Qwen3 models introduce a hybrid approach to problem-solving.
- Source [8]: text found — enable_thinking=True # Switches between thinking and non-thinking modes. Default is True.
- Source [8]: text found — In this mode, the model will generate think content wrapped in a
- Source [8]: text found — **DO NOT use greedy decoding**, as it can lead to performance degradation and endless repetitions.
- Source [9]: text found — enable_thinking is defined and enable_thinking is false
- Source [26]: text found — {{ bos_token }}{% if messages[0]['role'] == 'system' %}{{ raise_exception('System role not supported
- Source [31]: text found — This is an uncensored version of [Qwen/Qwen3-4B](https://huggingface.co/Qwen/Qwen3-4B) created with 
- Source [31]: text found — Ablation was performed using a new and faster method, which yields better results.
- Source [31]: text found — Changed the 0 layer to eliminate the problem of garbled codes
- Source [33]: text found — You need to agree to share your contact information to access this model
- Source [42]: text found — when comparing multiple variants of the same base model (e.g., RL-aligned, base, and safety-removed 
- Source [42]: text found — Experiments on over 40 models and 20 red teaming strategies demonstrate that the JSS metric exhibits
- Source [43]: text found — We test the state-of-the-art LLMs

## Follow-up Questions

- Gated rows (meta-llama/Llama-3.2-1B, google/gemma-2-2b(-it)): is the run allowed to use an HF token + license acceptance for the official checkpoints, or must it stay fully anonymous and use the ungated fallbacks (unsloth base mirror; mylesgoose/Miiyamoto255 abliterated), dropping the official instruct row of those two families?
- Should the Qwen3 'instruct' class be standardized as Qwen/Qwen3-{size} (2504 post-trained, thinking default ON) with Qwen/Qwen3-4B-Instruct-2507 as the optional non-thinking 4B refresh, and should the new latent metric be evaluated head-to-head against N-GLARE's JSS on the shared model subset as a required baseline?
- N-GLARE's per-model JSS numbers are only in scatter figures (no machine-readable table): do we need to extract them (figure/PDF mining) or is the plan's own fixed ~120-prompt reference refusal-rate set plus XSTest-EN sufficient as the primary behavioral target?

---
*Generated by AI Inventor Pipeline*
