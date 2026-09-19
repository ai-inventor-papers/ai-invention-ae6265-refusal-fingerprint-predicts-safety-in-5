# Qwen3 Safety Triad: Activation Evidence Review

## Summary

This research artifact verifies the factual/numeric claims underlying the planned study ('compare Qwen3 base vs official Instruct vs community abliterated models mechanistically; find internal patterns on safety prompts; build a 0- to few-prompt activation-based safety metric for arbitrary Hugging Face models'). Verified facts: (1) Qwen3 released April 29, 2025 with eight Apache-2.0 open-weight models (dense 0.6B/1.7B/4B/8B/14B/32B and MoE 30B-A3B/235B-A22B), 32K-128K context, ~36T pretraining tokens, four-stage post-training; HF metadata confirms Qwen/Qwen3-8B is a fine-tune of Qwen/Qwen3-8B-Base and the abliterated ecosystem exists at scale (e.g., huihui-ai/Huihui-Qwen3-8B-abliterated-v2). (2) Mechanistic prior art: refusal is mediated by a single residual-stream direction across 13 chat models incl. Qwen (arXiv:2406.11717); safety layers sit in contiguous middle layers (arXiv:2408.17003); safety-critical regions are ~3% of parameters (arXiv:2402.05162); harm is readable at each layer's output 'write site' and the safety direction transfers across architectures (arXiv:2609.04721); CAV/SCAV probes quantify per-layer safety concepts (arXiv:2404.12038). (3) The proposed 'new metric' is NOT novel in general form: GradSafe (ACL 2024) detects jailbreak prompts from gradients zero-shot; Google AMS (Apr 2026, Apache-2.0) scans any HF model in 10-40s by sigma-separation of three safety concepts (instruct-tuned 3.8-8.4 sigma, abliterated 3.3, uncensored 1.1-1.3, base ~0.7); RAS/SafeVec (arXiv:2606.25750, Jun 2026) extracts layer-wise refusal directions from a reference model and scores any target model with a calibrated 0-100 Refusal Alignment Score across Llama/Gemma/Qwen. (4) Cautionary evidence: abliteration has off-target effects (arXiv:2607.17427: +7.4pp/+12.2pp optimism on Qwen3-30B-A3B/Gemma-4 decisions; ~6 TruthfulQA points lost intrinsically) and refusal-rate-based scores can misrank models (RefusalBench arXiv:2605.21545: refusal rates 0.1%-94.6%, ranking != discrimination). Gap analysis: a systematic layer-by-layer activation comparison of the exact Qwen3-8B base/Instruct/abliterated triad and a direct calibration of activation-geometry scores against full benchmark refusal rates (SafetyBench 11,435 items / HarmBench / SORRY-Bench 440 items / WildGuard 92K) were not found in this search; per the mech-interp handbook, not-found is not equal to open, and a fresh saturation search is required at write-up time. All 23 sources were fetched and checked; the only tool failure was HTTP 401 on the HF API for Qwen3-8B-Instruct (handled by fallback evidence).

## Research Findings

**Verification results for the Qwen3 safety mechanistic-interpretability research plan**

**1. Tool availability (diagnostic step).** All web-tools skill operations (search, fetch, grep through the ability server) executed successfully. The single failure was HTTP 401 on the Hugging Face API endpoint for `Qwen/Qwen3-8B-Instruct`; this was handled by fallback: verifying the official `Qwen/Qwen3-8B` record and the Qwen team's blog directly [3, 1]. The Instruct-named chat checkpoint's existence is corroborated by the HF API evidence produced by the parallel research artifact in this run, but was not independently re-verified here.

**2. The three model families exist as claimed.** Qwen3 was released April 29, 2025, with eight open-weight models: six dense (0.6B, 1.7B, 4B, 8B, 14B, 32B) and two MoE (30B-A3B: 30B total / 3B activated; 235B-A22B: 235B total / 22B activated), all under the Apache 2.0 license; context lengths are 32K for the three smallest dense models and 128K for 8B/14B/32B and both MoE models [1]. Pre-training used ~36 trillion tokens across 119 languages/dialects, and post-training is a four-stage pipeline (long-CoT cold start, reasoning-based RL, thinking-mode fusion, general RL over 20+ tasks) [1]. The Qwen3 Technical Report (arXiv:2505.09388, May 14, 2025) describes the series with parameter scales from 0.6 to 235 billion [2]. On Hugging Face, `Qwen/Qwen3-8B` is the chat model (12.99M downloads, 2,014 likes, Apache-2.0) and its metadata tags it explicitly as a fine-tune of `Qwen/Qwen3-8B-Base` [3]; `Qwen/Qwen3-8B-Base` (442K downloads, Apache-2.0) is the pretrained base model [4]. These correspond to the plan's 'base' and 'official safety-finetuned' variants [1, 3]. Community abliterated models exist at scale: `huihui-ai/Huihui-Qwen3-8B-abliterated-v2` describes itself as 'an uncensored version of Qwen/Qwen3-8B created with abliteration' and 'a crude, proof-of-concept implementation to remove refusals' (Apache-2.0) [5]. An HF search returns many further examples, e.g. `huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF` (788 likes, ~2.83M downloads) and `IamLucif3r/Qwen3-4B-Instruct-2507-Abliterated`, reflecting that the Qwen family has since shipped Qwen3.5/3.8 with the same abliteration pattern [6].

**3. Mechanistic-interpretability facts relevant to the planned analysis.** The foundational result shows refusal 'is mediated by a one-dimensional subspace, across 13 popular open-source chat models up to 72B parameters in size', including Qwen Chat 1.8B/7B/14B/72B; erasing this single direction from residual-stream activations stops refusal of harmful instructions while adding it elicits refusal on harmless ones [7]. Methodologically, the direction is extracted by difference-in-means and the single most effective vector is selected from |I| x L layer-position candidates on validation sets [7]. The representation-engineering framework (RepE) underlies this: high-level concepts are placed at the center of analysis and can be monitored/manipulated for safety-relevant phenomena such as harmlessness [23]. Complementary localization results: a small set of contiguous middle layers ('safety layers') distinguishes malicious from normal queries, and freezing their gradients preserves security during fine-tuning (ICLR 2025) [14]; safety-critical regions are sparse, about 3% at parameter level and 2.5% at rank level, so removing them destroys safety with little utility loss [15]. On 'patterns in internal computation on safety prompts': harmful content is cleanly readable at each layer's output, the 'write site', before it is added to the residual stream, and a harm probe trained on a transformer flags an SSM's harmful inputs, i.e., the safety representation transfers across architectures while the read site is architecture-specific (arXiv:2609.04721, Sep 2026) [19]. Concept-activation-vector safety probes (SCAV, NeurIPS 2024) quantify safety concepts across layers of seven open LLMs and achieve high attack success when inverted [13].

**4. Full benchmarks versus quick activation-based metrics (prior art for the proposed metric).** Behavioral benchmarks: SafetyBench comprises 11,435 multiple-choice questions across 7 safety categories in Chinese and English (ACL 2024) [8]; HarmBench standardizes red-teaming evaluation with a comparison of 18 attack methods over 33 target LLMs and defenses [9]; SORRY-Bench provides a fine-grained taxonomy of 44 topics with 440 class-balanced unsafe instructions and 20 linguistic augmentations (ICLR 2025) [11]; WildGuard is a one-stop moderation tool built on WildGuardMix (92K labeled examples) and WildGuardTest (5K items) covering 13 risk categories, which reduced measured jailbreak success from 79.8% to 2.4% when deployed as a gate [10]. Few- or zero-prompt activation-based scoring already exists in three forms: GradSafe (ACL 2024) detects jailbreak prompts zero-shot by scrutinizing gradients of safety-critical parameters and outperforms Llama Guard without further training [12]; Google's AMS (Activation-based Model Scanner, Apache-2.0, Apr 2026) scans any Hugging Face-compatible model in 10-40 seconds with no generation, measuring sigma-separation of three concepts (harmful_content, injection_resistance, refusal_capability) at ~35-40% depth; reported separations are 3.8-8.4 sigma for instruction-tuned models (including Qwen), 3.3 sigma for abliterated models (WARNING band 2.0-3.5), 1.1-1.3 sigma for 'uncensored' fine-tunes, and ~0.69-0.7 sigma for base models, with Tier-2 identity verification via direction cosine similarity > 0.7 [16, 17]. The same source cites a 2025 study of 8,000+ safety-modified model repos on Hugging Face with 74% vs 19% compliance rates for modified vs original models [16]. Closest to the proposed metric is RAS/SafeVec (arXiv:2606.25750, Jun 2026): extract layer-wise refusal directions from a safety-aligned reference model, select stable layer windows, score a target model by whether its hidden states align with these directions under unsafe and jailbreak prompts, and map the result to a calibrated 0-100 Refusal Alignment Score; it separates aligned from uncensored and abliterated variants across Llama, Gemma and Qwen families and tracks output-level attack success rate [21].

**5. Contradicting and cautionary evidence.** Abliteration is not a clean surgical removal: a preregistered 21,600-decision study on Gemma-4-26B-A4B-it and Qwen3-30B-A3B-Instruct-2507 found abliterated arms systematically more optimistic (+12.2 pp Gemma, +7.4 pp Qwen), writing longer justifications with fewer uncertainty words, while the confidence effect reversed sign between families; the provenance audit also caught two toolchain contamination channels (mismatched quantizer pair, stale community chat template) that silently altered prompts - a direct warning for any study of community-modified checkpoints [18]. Abliteration also costs capability: even a clean implementation loses about six TruthfulQA points and ~88% of that cost is intrinsic to removing the refusal direction, not implementation sloppiness [20]. Finally, refusal rate - the behavior that refusal-direction metrics proxy - can misrank models: RefusalBench (May 2026) found strict refusal rates spanning 0.1% to 94.6% across 19 frontier models on identical prompts, and the model with the best tier discrimination (Youden's J = 0.787) ranked only seventh by raw refusal rate; nine of 18 models showed a 'hedge-but-help' partial-compliance pattern invisible to binary refusal metrics [22]. Any refusal-alignment safety score inherits this caveat [21, 22]. Per the mechanistic-interpretability handbook (internal, not cited here), activation-level findings are statistical estimates rather than fixed properties, and decodability of an internal signal does not guarantee actionability in output behavior - relevant when claiming a metric evaluates 'safety' rather than 'refusal alignment' [7, 19, 21].

**6. Gap analysis and confidence.** High confidence (verified against primary pages fetched in this run): the Qwen3 model facts, refusal-direction mechanism, benchmark statistics, and the existence and parameters of AMS and RAS as prior art for the metric idea [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 16, 17, 21]. The generic 'new metric' idea (activation-based, 0- to few-prompt, for arbitrary HF models) is already realized at least twice (AMS 2026; RAS 2026) [16, 17, 21], so a paper must position against them. Surviving open space not found in this search: (a) a systematic layer-by-layer activation comparison of the exact Qwen3 (8B) base vs Instruct vs abliterated triad; the closest located items are a Qwen3-0.6B refusal-steering master's thesis and family-generic audits that do not use this triad [19, 21]; (b) directly calibrating an activation-geometry score (sigma or RAS-like) against full-benchmark refusal rates (SafetyBench/HarmBench/SORRY-Bench) across a diverse HF model panel - no such calibration was found [16, 17, 21]; (c) prompt-count ablations (0 vs 1 vs few prompts) and reference-free operation (RAS needs a reference aligned model; AMS does not, but its thresholds rest on 14 configurations) [17, 21]. Confidence that (b)/(c) are unoccupied: medium - searches are never exhaustive, and the field handbook's standing rule applies: not-found-in-search does not equal open. A fresh saturation search at write-up time is required, and any claims about a new metric should be scoped as 'refusal-alignment score calibrated against behavioral benchmarks' rather than 'safety score' [22].

## Sources

[1] [Qwen3: Think Deeper, Act Faster (Qwen blog)](https://qwenlm.github.io/blog/qwen3/) (Qwen Team; 2025) — Official Qwen3 release post; verified release date (April 29, 2025), eight open-weight models with sizes, Apache-2.0 license, context lengths (32K/128K), pretraining token count (~36T), 119 languages, and the four-stage post-training pipeline.

> approximately 36 trillion tokens covering 119 languages and dialects

Locator: Pre-training section

[2] [Qwen3 Technical Report](https://arxiv.org/abs/2505.09388) (An Yang, et al. (60 authors); 2025) — arXiv abstract page confirming the report identity (submitted May 14, 2025, 60 authors) and that Qwen3 spans dense and MoE architectures with parameter scales from 0.6 to 235 billion.

> with parameter scales ranging from 0.6 to 235 billion

Locator: Abstract

[3] [Hugging Face API record: Qwen/Qwen3-8B](https://huggingface.co/api/models/Qwen/Qwen3-8B) (Qwen; 2025) — HF API metadata: Qwen3-8B chat model, 12,988,756 downloads, 2,014 likes, Apache-2.0, tagged as a finetune of Qwen3-8B-Base.

> "base_model:Qwen/Qwen3-8B-Base","base_model:finetune:Qwen/Qwen3-8B-Base","license:apache-2.0"

Locator: tags field

> "downloads":12988756

Locator: downloads field

[4] [Hugging Face API record: Qwen/Qwen3-8B-Base](https://huggingface.co/api/models/Qwen/Qwen3-8B-Base) (Qwen; 2025) — HF API metadata confirming the pretrained base model exists, Apache-2.0, linked to arXiv:2505.09388, 442,094 downloads, 125 likes.

> "arxiv:2505.09388","license:apache-2.0"

Locator: tags field

[5] [huihui-ai/Huihui-Qwen3-8B-abliterated-v2 model card](https://huggingface.co/huihui-ai/Huihui-Qwen3-8B-abliterated-v2) (huihui-ai) — Community 'abliterated' (uncensored) Qwen3-8B model: confirms the third member of the planned triad, Apache-2.0, created via the abliteration technique (remove-refusals-with-transformers).

> This is a crude, proof-of-concept implementation to remove refusals from an LLM model without using TransformerLens.

Locator: Model card introduction

[6] [Hugging Face API search: Qwen3-Abliterated](https://huggingface.co/api/models?search=Qwen3-Abliterated&limit=12&full=false) (Hugging Face; 2026) — HF API search results showing the scale of the abliterated ecosystem for the Qwen family (e.g., huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF with 788 likes and ~2.83M downloads; 0bserverx Heretic variants; IamLucif3r/Qwen3-4B-Instruct-2507-Abliterated).

> "id":"huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF","author":"huihui-ai"

Locator: first search result

[7] [Refusal in Language Models Is Mediated by a Single Direction](https://arxiv.org/abs/2406.11717) (Andy Arditi, Oscar Obeso, Aaquib Syed, Daniel Paleka, Nina Panickssery, Wes Gurnee, Neel Nanda; 2024) — Foundational mech-interp paper (Arditi et al.): refusal mediated by a one-dimensional residual-stream subspace across 13 open-source chat models up to 72B (including Qwen Chat 1.8B-72B); difference-in-means extraction; erase/add directional interventions; also published at COLM 2025 (DOI 10.52202/079017-4322).

> refusal is mediated by a one-dimensional subspace, across 13 popular open-source chat models up to 72B parameters in size

Locator: Abstract

> erasing this direction from the model's residual stream activations prevents it from refusing harmful instructions, while adding this direction elicits refusal on even harmless instructions

Locator: Abstract

[8] [SafetyBench: Evaluating the Safety of Large Language Models](https://arxiv.org/abs/2309.07045) (Zhexin Zhang, Leqi Lei, Lindong Wu, Rui Sun, Yongkang Huang, Chong Long, Xiao Liu, Xuanyu Lei, Jie Tang, Minlie Huang; 2024) — ACL 2024 benchmark: 11,435 multiple-choice questions, 7 safety categories, Chinese and English, tested on 25 LLMs.

> which comprises 11,435 diverse multiple choice questions spanning across 7 distinct categories of safety concerns

Locator: Abstract

[9] [HarmBench: A Standardized Evaluation Framework for Automated Red Teaming and Robust Refusal](https://arxiv.org/abs/2402.04249) (Mantas Mazeika, Long Phan, Xuwang Yin, Andy Zou, Zifan Wang, Norman Mu, Elham Sakhaee, Nathaniel Li, Steven Basart, Bo Li, David Forsyth, Dan Hendrycks; 2024) — Standardized red-teaming evaluation framework (Mazeika et al.); verified large-scale comparison of 18 red teaming methods over 33 target LLMs and defenses.

> we conduct a large-scale comparison of 18 red teaming methods and 33 target LLMs and defenses

Locator: Abstract

[10] [WildGuard: Open One-Stop Moderation Tools for Safety Risks, Jailbreaks, and Refusals of LLMs](https://arxiv.org/abs/2406.18495) (Seungju Han, Kavel Rao, Allyson Ettinger, Liwei Jiang, Bill Yuchen Lin, Nathan Lambert, Yejin Choi, Nouha Dziri; 2024) — NeurIPS 2024 moderation/evaluation tool: WildGuardMix (92K labeled examples) and WildGuardTest (5K items), 13 risk categories; reduces measured jailbreak success from 79.8% to 2.4% as a gate.

> we construct WildGuardMix, a large-scale and carefully balanced multi-task safety moderation dataset with 92K labeled examples

Locator: Abstract

> reducing the success rate of jailbreak attacks from 79.8% to 2.4%

Locator: Abstract

[11] [SORRY-Bench: Systematically Evaluating Large Language Model Safety Refusal](https://arxiv.org/abs/2406.14598) (2025) — Safety-refusal benchmark: fine-grained taxonomy of 44 unsafe topics, 440 class-balanced unsafe instructions, 20 linguistic augmentations (ICLR 2025; authorship per proceedings: Tinghao Xie, Xiangyu Qi, et al.).

> a fine-grained taxonomy of 44 potentially unsafe topics, and 440 class-balanced unsafe instructions

Locator: Abstract

[12] [GradSafe: Detecting Jailbreak Prompts for LLMs via Safety-Critical Gradient Analysis](https://arxiv.org/abs/2402.13494) (Yueqi Xie, Minghong Fang, Renjie Pi, Neil Gong; 2024) — ACL 2024: jailbreak-prompt detection from gradients of safety-critical parameters; zero-shot and adaptation settings outperform Llama Guard on ToxicChat and XSTest despite no training data.

> detects jailbreak prompts by scrutinizing the gradients of safety-critical parameters in LLMs

Locator: Abstract

[13] [Uncovering Safety Risks of Large Language Models through Concept Activation Vector](https://arxiv.org/abs/2404.12038) (Zhihao Xu, Ruixuan Huang, Changyu Chen, Xiting Wang; 2024) — SCAV framework (NeurIPS 2024): CAV-based safety concept probes across layers of seven open-source LLMs; reports 99.14% average attack success rate against them under a keyword-matching criterion.

> in our evaluation of seven open-source LLMs, we observe an average attack success rate of 99.14%, based on the classic keyword-matching criterion

Locator: Abstract

[14] [Safety Layers in Aligned Large Language Models: The Key to LLM Security](https://arxiv.org/abs/2408.17003) (Shen Li, Liuyi Yao, Lan Zhang, Yaliang Li; 2025) — ICLR 2025 paper locating a small set of contiguous middle 'safety layers' critical for malicious-vs-normal discrimination and proposing SPPFT (fixing their gradients during fine-tuning).

> identifying a small set of contiguous layers in the middle of the model that are crucial for distinguishing malicious queries from normal ones

Locator: Abstract

[15] [Assessing the Brittleness of Safety Alignment via Pruning and Low-Rank Modifications](https://arxiv.org/abs/2402.05162) (Boyi Wei, Kaixuan Huang, Yangsibo Huang, Tinghao Xie, Xiangyu Qi, Mengzhou Xia, Prateek Mittal, Mengdi Wang, Peter Henderson; 2024) — Wei et al.: safety-critical regions are sparse (~3% of parameters, ~2.5% of rank); removing them compromises safety with little utility loss, evidencing brittleness of safety alignment.

> the isolated regions we find are sparse, comprising about $3\%$ at the parameter level and $2.5\%$ at the rank level

Locator: Abstract

[16] [Introducing AMS: Activation-based model scanner for open-weight LLM safety verification (Google Open Source Blog)](https://opensource.googleblog.com/2026/04/introducing-ams-activation-based-model-scanner-for-open-weight-llm-safety-verification.html) (Glen Messenger; 2026) — Google's AMS (Apache-2.0, Apr 2026): scans any HF-compatible model in 10-40 seconds without generation; sigma-separation of 3 safety concepts; separations by model type (instruct-tuned incl. Qwen 3.8-8.4 sigma, abliterated 3.3, uncensored 1.1-1.3, base ~0.69); cites a 2025 study of 8,000+ safety-modified HF repos (74% vs 19% compliance).

> The entire scan completes in a single forward pass per prompt pair, typically 10-40 seconds on GPU hardware.

Locator: How It Works section

> A 2025 study identified over 8,000 safety-modified model repositories on Hugging Face alone, with modified models complying with unsafe requests at rates of 74% compared to 19% for their original instruction-tuned counterparts.

Locator: Introduction

[17] [AMS - Activation-based Model Scanner (GitHub README)](https://github.com/GoogleCloudPlatform/activation-model-scanner) (Google Cloud Platform; 2026) — AMS implementation details: Tier-1 thresholds PASS >3.5 sigma / WARNING 2.0-3.5 / CRITICAL <2.0; Tier-2 identity verification via cosine similarity >0.7; three concepts (harmful_content, injection_resistance, refusal_capability); 10-40s scans on A100/L4; based on AASE methodology.

> Thresholds: PASS (>3.5σ), WARNING (2.0–3.5σ), CRITICAL (<2.0σ)

Locator: Tier 1 heading

[18] [Abliteration Is Not a Scalpel: Off-Target Effects of Refusal Removal on Decision Disposition Across Model Families](https://arxiv.org/abs/2607.17427) (Aleksander Fafuła; 2026) — Preregistered 21,600-decision study on Gemma-4-26B-A4B-it and Qwen3-30B-A3B-Instruct-2507: abliterated arms are systematically more optimistic, write longer justifications, use fewer uncertainty words; confidence effect reverses sign between families; provenance audit caught two toolchain contamination channels.

> abliterated models are systematically more optimistic (+12.2 pp Gemma, +7.4 pp Qwen

Locator: Abstract

[19] [Locating and Steering Refusal Beyond Attention](https://arxiv.org/abs/2609.04721) (Preethi Carmel Bosco, Gopalakrishnan Srinivasan; 2026) — Shows the harm/refusal representation reads cleanly at each layer's output ('write site') before the residual-stream addition and transfers across SSM/transformer/recurrent/hybrid architectures; detector-gated steering lowers jailbreak success.

> harm is cleanly readable at this output, the write site, before the addition

Locator: Abstract

> A harm probe trained on a transformer then flags an SSM's harmful inputs

Locator: Abstract

[20] [Abliteration Doesn't Just Remove Refusals. It Removes Truth. (TemperatureZero)](https://temperaturezero.com/2026/06/14/abliteration-removes-truth/) (Maxim Starkweather; 2026) — Secondary analysis of a LessWrong test on Qwen3.5-27B: even a clean abliteration loses ~6 TruthfulQA points; ~88% of the cost is intrinsic to removing the refusal direction, not implementation quality; describes FailSpy abliterator and huihui-ai's industrial-scale use.

> You lose six points of factual accuracy regardless.

Locator: Article body

> The remaining 88% of abliteration's cost on TruthfulQA is intrinsic to removing the refusal direction at all.

Locator: Article body

[21] [RAS: Measuring LLM Safety Through Refusal Alignment](https://arxiv.org/abs/2606.25750) (Chang-Chieh Huang, Yan-Lun Chen, Chia-Mu Yu, Wei-Bin Lee; 2026) — Closest published match to the proposed metric: SafeVec extracts layer-wise refusal directions from a safety-aligned reference model, selects stable layer windows, scores target hidden states under unsafe/jailbreak prompts, mapping to a calibrated 0-100 Refusal Alignment Score; validated across Llama, Gemma and Qwen, separating aligned from uncensored and abliterated variants.

> scores a target model by measuring whether its hidden states align with these refusal directions under unsafe and jailbreak prompts

Locator: Abstract

> maps representation-level refusal alignment to a calibrated 0-100 safety score

Locator: Abstract

[22] [RefusalBench: Why Refusal Rate Misranks Frontier LLMs on Biological Research Prompts](https://arxiv.org/abs/2605.21545) (Lukas Weidener, Marko Brkić, Mihailo Jovanović, Emre Ulgac, Aakaash Meduri; 2026) — Cautionary evidence: strict refusal rates span 0.1% to 94.6% across 19 frontier models on identical prompts; refusal-rate ranking misranks safety calibration (best tier discrimination ranked 7th by refusal rate); 9 of 18 models hedge-but-help.

> strict refusal rates span 0.1% to 94.6% on identical prompts

Locator: Abstract

> Strict refusal rate misranks safety calibration: Grok 4.20 achieves the highest tier discrimination (Youden's J = 0.787) while ranking only seventh by overall refusal rate

Locator: Abstract

[23] [Representation Engineering: A Top-Down Approach to AI Transparency](https://arxiv.org/abs/2310.01405) (Andy Zou, Long Phan, Sarah Chen, James Campbell, Phillip Guo, Richard Ren, Alexander Pan, Xuwang Yin, Mantas Mazeika, Ann-Kathrin Dombrowski, Shashwat Goel, Nathaniel Li, Michael J. Byun, Zifan Wang, Alex Mallen, Steven Basart, Sanmi Koyejo, Dawn Song, Matt Fredrikson, J. Zico Kolter, Dan Hendrycks; 2023) — RepE framework (Zou et al.): population-level representations as the analytic unit, with methods for monitoring and manipulating honesty, harmlessness, power-seeking in LLMs - the general basis for activation-based safety monitoring.

> RepE places population-level representations, rather than neurons or circuits, at the center of analysis

Locator: Abstract

## Verification

Numbered citations resolve to unique listed sources. Passage checks test text occurrence, not claim truth or entailment. Author/year metadata and locators are not independently verified. Details: `research_verification.json`.

- Source [1]: text found — approximately 36 trillion tokens covering 119 languages and dialects
- Source [2]: text found — with parameter scales ranging from 0.6 to 235 billion
- Source [3]: text found — "base_model:Qwen/Qwen3-8B-Base","base_model:finetune:Qwen/Qwen3-8B-Base","license:apache-2.0"
- Source [3]: text found — "downloads":12988756
- Source [4]: text found — "arxiv:2505.09388","license:apache-2.0"
- Source [5]: text found — This is a crude, proof-of-concept implementation to remove refusals from an LLM model without using 
- Source [6]: text found — "id":"huihui-ai/Huihui-Qwen3.8-27B-abliterated-GGUF","author":"huihui-ai"
- Source [7]: text found — refusal is mediated by a one-dimensional subspace, across 13 popular open-source chat models up to 7
- Source [7]: text found — erasing this direction from the model's residual stream activations prevents it from refusing harmfu
- Source [8]: text found — which comprises 11,435 diverse multiple choice questions spanning across 7 distinct categories of sa
- Source [9]: text found — we conduct a large-scale comparison of 18 red teaming methods and 33 target LLMs and defenses
- Source [10]: text found — we construct WildGuardMix, a large-scale and carefully balanced multi-task safety moderation dataset
- Source [10]: text found — reducing the success rate of jailbreak attacks from 79.8% to 2.4%
- Source [11]: text found — a fine-grained taxonomy of 44 potentially unsafe topics, and 440 class-balanced unsafe instructions
- Source [12]: text found — detects jailbreak prompts by scrutinizing the gradients of safety-critical parameters in LLMs
- Source [13]: text found — in our evaluation of seven open-source LLMs, we observe an average attack success rate of 99.14%, ba
- Source [14]: text found — identifying a small set of contiguous layers in the middle of the model that are crucial for disting
- Source [15]: text found — the isolated regions we find are sparse, comprising about $3\%$ at the parameter level and $2.5\%$ a
- Source [16]: text found — The entire scan completes in a single forward pass per prompt pair, typically 10-40 seconds on GPU h
- Source [16]: text found — A 2025 study identified over 8,000 safety-modified model repositories on Hugging Face alone, with mo
- Source [17]: text found — Thresholds: PASS (>3.5σ), WARNING (2.0–3.5σ), CRITICAL (<2.0σ)
- Source [18]: text found — abliterated models are systematically more optimistic (+12.2 pp Gemma, +7.4 pp Qwen
- Source [19]: text found — harm is cleanly readable at this output, the write site, before the addition
- Source [19]: text found — A harm probe trained on a transformer then flags an SSM's harmful inputs
- Source [20]: text found — You lose six points of factual accuracy regardless.
- Source [20]: text found — The remaining 88% of abliteration's cost on TruthfulQA is intrinsic to removing the refusal directio
- Source [21]: text found — scores a target model by measuring whether its hidden states align with these refusal directions und
- Source [21]: text found — maps representation-level refusal alignment to a calibrated 0-100 safety score
- Source [22]: text found — strict refusal rates span 0.1% to 94.6% on identical prompts
- Source [22]: text found — Strict refusal rate misranks safety calibration: Grok 4.20 achieves the highest tier discrimination 
- Source [23]: text found — RepE places population-level representations, rather than neurons or circuits, at the center of anal

## Follow-up Questions

- How many prompts do AMS and RAS/SafeVec actually require per model, and do their activation scores rank-order models consistently with full-benchmark refusal rates on SafetyBench/HarmBench/SORRY-Bench across a diverse Hugging Face panel?
- Does the refusal direction found in Qwen3-8B-Instruct survive the 2507 refresh and later Qwen3.5/Qwen3.8 checkpoints, and how does its layer profile differ between base, Instruct, and huihui-style abliterated weights?
- Can a reference-free few-prompt activation score be benchmark-calibrated into an absolute safety estimate despite RefusalBench's evidence that raw refusal rate misranks models - i.e., what is the correlation between refusal-alignment geometry and task-specific tier discrimination (Youden's J)?

---
*Generated by AI Inventor Pipeline*
