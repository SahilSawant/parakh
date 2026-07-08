# M1 — Hindi↔English embedding spike (concluded)

> **⚠️ Threshold superseded.** This spike recommended ~0.85 from clean EN↔HI
> translation pairs. The full **precision harness** (`docs/M1-precision.md`) later
> showed 0.85 over-merges the multi-story case (precision 0.29); the operating
> threshold is **0.88**. This doc's cross-lingual *viability* conclusion still
> holds; its threshold number does not.


**Question (work order §7, M1 gate):** does the multilingual embedding model place
the *same story's* English and Hindi headlines close enough to cluster together,
while keeping *different* stories apart? If not, we fall back to translating Hindi
titles to English before embedding.

**Verdict: PASS — cross-lingual clustering is viable with multilingual-e5, no
translation fallback needed.** But the threshold must be raised from the work
order's assumed 0.82.

## Method

`python -m app.spike.bilingual_eval --model <id>` over 12 curated EN/HI headline
pairs (`app/spike/eval_pairs.json`), each pair describing the same real-world event
across distinct topics (data rules, RBI rate, ISRO, monsoon, electoral bonds,
cricket, fuel prices, MSP, heatwave, education policy, rupee, air quality).

- **positive** = cosine(EN_i, HI_i) — same story, cross-language
- **negative** = cosine(EN_i, HI_j), i≠j — different stories
- **retrieval@1** = for each English headline, is its true Hindi translation the
  nearest of all 12 Hindi headlines?

Run on Apple Silicon (MPS), sentence-transformers 5.1.2 / torch 2.8.

## Results

| model | pairs | pos min | pos mean | neg max | neg mean | separation | retrieval@1 | rec. threshold |
|---|---|---|---|---|---|---|---|---|
| multilingual-e5-**small** | 12 | 0.860 | 0.909 | 0.819 | 0.757 | +0.041 | **100%** | 0.839 |
| multilingual-e5-**large** | 12 | 0.878 | 0.913 | 0.834 | 0.755 | +0.044 | **100%** | 0.856 |

## Findings

1. **Retrieval@1 = 100%** on both models — every English headline's nearest
   neighbour among the Hindi set is its true translation. Cross-lingual clustering
   works; the translate-then-embed fallback is **not** required for MVP.
2. **e5 compresses cosine similarities into a high band** (~0.75–0.91). The gap
   between same-story and different-story pairs is real but **thin (~0.04)**.
3. **0.82 is too low.** Different-story pairs reach **0.834** (e5-large), so a 0.82
   threshold would produce false merges. Config default is now **0.85**
   (`cluster_sim_threshold`), sitting above the observed negative max with a small
   margin below the positive min (0.878).
4. e5-large buys only a marginally wider separation than e5-small here. e5-large
   remains the default (schema is `VECTOR(1024)`, matching e5-large), but e5-small
   (384-dim) is a viable cost/latency fallback if we re-dimension.

## Caveats / follow-ups

- n=12, clean headlines. Real feeds are noisier (partial titles, mixed scripts,
  wire boilerplate). **Re-run against a labelled sample of live clusters** during
  M1's precision-gate work (≥85% precision on 100 hand-labelled stories).
- Thin margin means clustering is sensitive to threshold. Hold the **nightly
  merge/split repair pass** (design §4) as the safety net, and consider a two-stage
  gate (SimHash/lexical pre-filter → vector confirm).
- Validate `BAAI/bge-m3` as an alternative before locking in e5-large.
- These numbers are the **cross-lingual retrieval** proxy, not the end-to-end
  clustering precision. The ≥85% precision gate is still open.

## Reproduce

```bash
cd worker && pip install -e ".[ml]"
python -m app.spike.bilingual_eval --model intfloat/multilingual-e5-large
python -m app.spike.bilingual_eval --model intfloat/multilingual-e5-small
```
