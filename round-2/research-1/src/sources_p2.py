#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sources 21-40. All URLs accessed 2026-09-19; passages verbatim with locators."""
PART2 = [
 {"index":21,"url":"https://arxiv.org/abs/2609.09793","title":"How Fragile Is Safety Alignment at Frontier Scale? A Single-Direction Attack on a 320B MoE (arXiv:2609.09793)",
  "summary":"Directional ablation transferred to GLM-5.3-Flash (320B MoE, block-FP8): works but needs writer-set surgery beyond module matching; random-orthogonal direction control; category-concentrated residue at every rank 1-12; 'few hundred contrastive prompts'. Fetched 2026-09-19.",
  "authors":["Yi Shi","Tanyu Chen","Kai Shen"],"year":2026,
  "supporting_passages":[
   {"quote":"It needs no gradient-based training and no optimization, only a few hundred contrastive prompts, which makes it the canonical white-box attack on open-weight alignment.","locator":"arXiv abstract"},
   {"quote":"The effect does not follow from removing just any direction: ablating a random direction orthogonal to it leaves refusal unchanged.","locator":"arXiv HTML, abstract"},
   {"quote":"A category-concentrated residue survives every edit we tried: subspaces fitted on violence, sexual content and hate leave measurable refusal at every rank from 1 to 12.","locator":"arXiv HTML, abstract"}]},
 {"index":22,"url":"https://arxiv.org/abs/2606.08044","title":"Audit gap / dissociated models + Latent Vulnerability Score (LVS; arXiv:2606.08044)",
  "summary":"Defines the audit gap and LVS (safety degradation per unit of bounded latent perturbation); dissociated models built from Gemma 2 2B, Llama 3.2 3B, Qwen 2.5 3B; random-perturbation controls <=12%; 'a safety audit must intervene'. Fetched 2026-09-19. (Plan had flagged this id as the LVS paper: verified as the audit-gap paper.)",
  "authors":None,"year":2026,
  "supporting_passages":[
   {"quote":"We call the gap between what static audits certify and what an intervention can reach the audit gap, and we show it is realizable: one can build a model that matches its safety-aligned base on every static audit yet gives way to a small, known perturbation of its internal state.","locator":"arXiv abstract"},
   {"quote":"At the targeted mid layer the dissociated models score 2.5 to 3.1 times higher LVS than their bases. A bounded latent attack elicits harmful compliance on 54 to 86% of prompts, against 3 to 48% for the bases, while matched random perturbations stay at or below 12%.","locator":"arXiv abstract"},
   {"quote":"Behavioral testing, even with static latent probing, cannot certify representation-level robustness: a safety audit must intervene on the model, not only observe it.","locator":"arXiv abstract"}]},
 {"index":23,"url":"https://arxiv.org/abs/2406.11717","title":"Refusal in LLMs is mediated by a single direction (Arditi et al., COLM 2025)",
  "summary":"Canonical refusal-direction work: difference-in-means direction across 13 chat models; per-layer cosine profile (Fig 5); directional ablation x' <- x - rhat rhat^T x across all layers/positions; selection over |I| x L candidates; 128 harmful training instructions. Fetched 2026-09-19.",
  "authors":["Andy Arditi","Oscar Obeso","Aaquib Syed","Daniel Paleka","Nina Panickssery","Wes Gurnee"],"year":2024,
  "supporting_passages":[
   {"quote":"Directional ablation \"zeroes out\" the component along rhat for every residual stream activation x ... x' <- x - rhat rhat^T x. (4) We perform this operation at every activation x_i^(l) and x~_i^(l), across all layers l and all token positions.","locator":"arXiv:2406.11717, Section 2.4 'Model interventions' (equations 3-4)"},
   {"quote":"0 5 10 15 20 Layer; 0.0 0.1 0.2 0.3 0.4 0.5 Cosine similarity with refusal direction; harmful; harmful + random_suffix; harmful + adv_suffix; harmless. Figure 5: Cosine similarity between last token residual stream activations and refusal direction.","locator":"arXiv:2406.11717, Section 5.1, Fig. 5 caption (per-layer curves)"},
   {"quote":"To construct D_train_harmful, we randomly sample a total of 128 harmful instructions from ADVBENCH ... MALICIOUSINSTRUCT ... and TDC2023. To construct D_val_harmful, we sample 32 instructions from the HARMBENCH validation set","locator":"arXiv:2406.11717, Appendix A.1"}]},
 {"index":24,"url":"https://arxiv.org/abs/2609.04721","title":"Locating and Steering Refusal Beyond Attention (arXiv:2609.04721)",
  "summary":"Refusal direction shared across architectures (attention-to-SSM transport); harm decodable at per-architecture 'write sites' (probe AUROC 0.99); orthogonalized-random-direction controls (cosine ~0) used systematically. Fetched 2026-09-19.",
  "authors":None,"year":2026,
  "supporting_passages":[
   {"quote":"Removing the aligned direction makes a model answer attacks it would otherwise refuse, while a random direction of the same size does far less.","locator":"arXiv HTML, para '7693:...'"},
   {"quote":"As a control, we repeat both with a random source direction mapped through W and orthogonalized to the target's refusal axis, so the map cannot leak refusal signal into it","locator":"arXiv HTML, para '28102:...'"},
   {"quote":"Each layer computes a fresh output that is then added into the residual stream, and harm is cleanly readable at this output, the write site, before the addition.","locator":"arXiv HTML, para '7693:...'"},
   {"quote":"Harm peaks in decodability at each architecture's write site: a linear probe separates harmful from benign prompts with AUROC 0.99","locator":"arXiv HTML, para '12486:...'"}]},
 {"index":25,"url":"https://arxiv.org/abs/2501.17727","title":"Automated Interpretability Metrics Do Not Distinguish Trained and Random Transformers (Heap et al.)",
  "summary":"Randomized-initialization baseline (handbook S9): SAEs on randomly initialized Pythia transformers get auto-interp scores and reconstruction metrics similar to trained ones across multiple randomization schemes. arXiv 2025-01-29. Fetched 2026-09-19.",
  "authors":["Thomas Heap","Thomas Adamson","Tim Lawson"],"year":2025,
  "supporting_passages":[
   {"quote":"in many settings, SAEs trained on randomly initialized transformers produce auto-interpretability scores and reconstruction metrics that are similar to those from trained models","locator":"arXiv abstract"},
   {"quote":"These results show that high aggregate auto-interpretability scores do not, by themselves, guarantee that learned, computationally relevant features have been recovered.","locator":"arXiv abstract"}]},
 {"index":26,"url":"https://arxiv.org/abs/2507.08802","title":"The Non-Linear Representation Dilemma: Is Causal Abstraction Enough for Mechanistic Interpretability? (Sutter et al.)",
  "summary":"NeurIPS 2025 Spotlight (per mech-interp handbook S5): with unrestricted alignment maps, any network can map to any algorithm; empirically perfect interchange-intervention accuracy on randomly initialized models. Fetched 2026-09-19.",
  "authors":["Thomas Sutter","Nicola Gnecco"],"year":2025,
  "supporting_passages":[
   {"quote":"we prove that under reasonable assumptions, any neural network can be mapped to any algorithm, rendering this unrestricted notion of causal abstraction trivial and uninformative.","locator":"arXiv abstract"}]},
 {"index":27,"url":"https://aclanthology.org/D19-1275/","title":"Designing and Interpreting Probes with Control Tasks (Hewitt and Liang, EMNLP-IJCNLP 2019)",
  "summary":"Control-task/selectivity norm for probing: a probe reflecting the representation should score high on the task and low on the control. Fetched 2026-09-19.",
  "authors":["John Hewitt","Percy Liang"],"year":2019,
  "supporting_passages":[
   {"quote":"a good probe, (one that reflects the representation), should be selective, achieving high linguistic task accuracy and low control task accuracy.","locator":"Anthology abstract"}]},
 {"index":28,"url":"https://arxiv.org/abs/2404.15255","title":"How to use and interpret activation patching (Heimersheim and Turner)",
  "summary":"Canonical activation-patching practice guide; patching-baseline norms for intervention studies. Fetched 2026-09-19.",
  "authors":["Stefan Heimersheim","Jan Brauner"],"year":2024,
  "supporting_passages":[
   {"quote":"In most situations, use activation patching instead of ablations.","locator":"arXiv:2404.15255 (HTML)"}]},
 {"index":29,"url":"https://arxiv.org/abs/2406.04313","title":"Improving Alignment and Robustness with Circuit Breakers (Zou et al.)",
  "summary":"Circuit breakers: intervention-based defense and representational-corruption training; canonical reference for intervention sweeps on refusal behavior. Id verified 2026-09-19 via OpenAlex (DOI 10.48550/arxiv.2406.04313).",
  "authors":["Andy Zou","Long Phan","Justin Wang","Derek Duvenaud","David Duvenaud","Jacob Steinhardt","Dan Hendrycks"],"year":2024,
  "supporting_passages":[]},
 {"index":30,"url":"https://aclanthology.org/2026.acl-long.1334/","title":"N-GLARE (ACL 2026 Long, anthology page)",
  "summary":"N-GLARE official published venue: ACL 2026 Long paper 2026.acl-long.1334; authors Zheyu Lin et al.; PDF at aclanthology.org/2026.acl-long.1334.pdf. Fetched 2026-09-19.",
  "authors":["Zheyu Lin","Jirui Yang","Yukui Qiu","Yubing Bao","Hengqi Guo","Yao Guan"],"year":2026,
  "supporting_passages":[
   {"quote":"N-GLARE: An Non-Generative Latent Representation-Efficient LLM Safety Evaluator","locator":"Anthology page title"}]},
 {"index":31,"url":"https://arxiv.org/abs/2511.14195","title":"N-GLARE arXiv v2 (APT/JSS method)",
  "summary":"N-GLARE method: APT (Angular-Probabilistic Trajectory) + JSS (Jensen-Shannon Separability) of turning angles vs a benign manifold; >40 models, 20 red-team strategies; <1% token cost; Qwen3-4B base/RL/safety-removed variants show geometric separation (Fig 1); zoo rows present but figure-only. Fetched 2026-09-19.",
  "authors":None,"year":2025,
  "supporting_passages":[
   {"quote":"Experiments on over 40 models and 20 red teaming strategies demonstrate that the JSS metric exhibits high consistency with the safety rankings derived from Red Teaming.","locator":"arXiv abstract"},
   {"quote":"when comparing multiple variants of the same base model (e.g., RL-aligned, base, and safety-removed versions of Qwen3-4B), we observe that better-aligned variants exhibit more pronounced geometric separation between different trajectories in latent space.","locator":"ACL PDF, p.2 'Figure 1 supports the core intuition'"}]},
 {"index":32,"url":"https://arxiv.org/abs/2402.13494","title":"GradSafe (Bui et al., ACL 2024)",
  "summary":"Zero-shot jailbreak-prompt detection from gradients of safety-critical parameters (arXiv id verified 2026-09-19; characterization carried from iter-1 dep as binding).",
  "authors":None,"year":2024,
  "supporting_passages":[]},
 {"index":33,"url":"https://arxiv.org/abs/2605.21545","title":"RefusalBench (arXiv:2605.21545)",
  "summary":"Matched-triple biological-research refusal benchmark: 141 prompts/47 bundles; strict refusal rates 0.1%-94.6% across 19 frontier models; refusal-rate ranking is not discrimination. Fetched 2026-09-19.",
  "authors":None,"year":2026,
  "supporting_passages":[
   {"quote":"Across 19 frontier models in the May 2026 snapshot, strict refusal rates span 0.1% to 94.6% on identical prompts.","locator":"arXiv abstract"}]},
 {"index":34,"url":"https://arxiv.org/abs/2407.17436","title":"AIR-Bench 2024 (safety benchmark from regulations and policies)",
  "summary":"AIR-Bench 2024 = first AI safety benchmark built on regulatory risk categories (identity verified 2026-09-19; zoo rows not extracted - secondary anchor).",
  "authors":None,"year":2024,
  "supporting_passages":[
   {"quote":"we introduce AIR-Bench 2024, the first AI safety benchmark aligned [with regulatory risk categories]","locator":"arXiv abstract (fragment)"}]},
 {"index":35,"url":"https://arxiv.org/abs/2406.14598","title":"SORRY-Bench (arXiv:2406.14598)",
  "summary":"Systematic safety-refusal benchmark with fine-grained taxonomy; 450 unsafe prompts across 45 categories; a refusal-rate target reference. Fetched 2026-09-19 (identity verified; partial abstract).",
  "authors":None,"year":2024,
  "supporting_passages":[
   {"quote":"existing methods often use coarse-grained taxonomies of unsafe topics, and are over-representing some fine-grained topics","locator":"arXiv abstract (fragment)"}]},
 {"index":36,"url":"https://arxiv.org/abs/2311.08370","title":"SimpleSafetyTests (arXiv:2311.08370)",
  "summary":"100 critical-safety prompts suited for binary refusal screening; identity verified 2026-09-19 (secondary anchor).",
  "authors":None,"year":2023,
  "supporting_passages":[]},
 {"index":37,"url":"https://arxiv.org/abs/2606.15980","title":"Do Activation Monitors Survive Model Updates? (arXiv:2606.15980)",
  "summary":"First systematic test of activation-monitor staleness under quantization/fine-tuning/LoRA/merge updates; evaluated on Gemma-2-2B-it and Qwen2.5-7B-Instruct; monitors drift and can be predicted/repaired. Fetched 2026-09-19.",
  "authors":None,"year":2026,
  "supporting_passages":[
   {"quote":"We present the first systematic test of whether this implicit contract holds: whether activation monitors trained on a base model remain reliable after these routine model updates.","locator":"arXiv abstract"}]},
 {"index":38,"url":"https://arxiv.org/abs/2607.17427","title":"Abliteration Is Not a Scalpel: Off-Target Effects of Refusal Removal (arXiv:2607.17427)",
  "summary":"Off-target effects: 21,600 no-refusal decision tasks, base vs abliterated arms of two MoE families; between-arm deltas are pure side effects (iter-1 dep carries +7.4pp/+12.2pp optimism deltas and ~6 TruthfulQA points as binding). Fetched 2026-09-19.",
  "authors":None,"year":2026,
  "supporting_passages":[
   {"quote":"The task elicits no refusals at all, so any between-arm delta is pure side effect. Holding provenance constant (official BF16 checkpoints, a single abliteration author, an identical serving stack, one byte-identical frozen prompt), we compare base and abliterated arms of two Mixture-of-Experts families","locator":"arXiv abstract"}]},
 {"index":39,"url":"https://arxiv.org/abs/2608.18093","title":"Abliteration Mitigation via Refusal Aliases / AMRA (arXiv:2608.18093)",
  "summary":"Defense that obscures the refusal signal with rank-k updates to residual-stream writer matrices plus random-alias activations; +2.16 post-abliteration refusal score on Llama-3-8B with <0.5pp MMLU loss. Shows fingerprint extraction can be actively hindered. Fetched 2026-09-19.",
  "authors":None,"year":2026,
  "supporting_passages":[
   {"quote":"we introduce a weight-editing method that obscures the refusal signal by applying rank-k updates to residual stream writer matrices while replacing refusal-inducing activations with random aliases and correcting downstream reader matrices to preserve the model's original behavior","locator":"arXiv abstract"},
   {"quote":"On Llama-3-8B, AMRA improves post-abliteration refusal scores by 2.16 points over the undefended baseline with less than 0.5 percentage points of MMLU degradation","locator":"arXiv abstract"}]},
 {"index":40,"url":"https://arxiv.org/abs/2608.17202","title":"Fool's Gold: Defensive Deception Against Safety-Removal Attacks (arXiv:2608.17202)",
  "summary":"Decoy hardening: trained decoys that only express in the attacked (safety-removed) state; 0.51-0.90 decoy rates on attacked-state responses across 7 models (9B-122B); perturbs post-abliteration behavior while keeping clean-state behavior near-original. Fetched 2026-09-19.",
  "authors":None,"year":2026,
  "supporting_passages":[
   {"quote":"On the six models passing our pre-registered efficacy gate, 0.51-0.90 of attacked-state responses to held-out prompts are decoys","locator":"arXiv abstract"}]},
]