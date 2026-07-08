# M1 — clustering precision harness

**Gate (work order §7):** ≥85% precision on a hand-labelled eval set. Precision is
**pairwise precision**: over all article pairs the system merges into one story,
the fraction that are truly the same story. It's the gate because a false merge
shows two unrelated stories as one coverage set — corrupting the bias distribution,
the product's core claim.

## Harness

`python -m app.eval.run_precision [--model <id>] [--gate 0.85]`

- `app/eval/metrics.py` — pairwise precision/recall/F1 (pure, unit-tested).
- `app/eval/gold_stories.jsonl` — the labelled set.
- `app/eval/run_precision.py` — embeds the gold set once with the **real** model,
  clusters with the **real** `incremental_cluster` at each threshold, scores vs
  gold, and sweeps thresholds to find the operating point.
- `--export-labeling OUT` — dumps ingested DB articles into a labelling template
  (blank `story` field) to build the real hand-labelled set.

### Gold set (honest scope)

71 articles across 21 stories: bilingual (EN + हिंदी), multi-outlet, 3 singletons,
and **two hard-adjacent pairs** designed to break naive clustering —
`isro-nvs` vs `isro-spadex` (two different ISRO space events) and
`budget-tax` vs `gst-council` (two different fiscal stories). These must stay
**separate**; merging them is a precision failure.

> ⚠️ This gold set is **authored** (by us), not hand-labelled from live feeds. It
> validates the harness and yields a realistic number, but formally closing the
> gate requires running over the real labelled 100 (use `--export-labeling`).

## Result — intfloat/multilingual-e5-large

| threshold | precision | recall | F1 | pred clusters |
|---:|---:|---:|---:|---:|
| ≤ 0.82 | 0.039 | 1.000 | 0.076 | 1 |
| 0.85 | **0.288** | 1.000 | 0.448 | 11 |
| 0.86 | 0.364 | 1.000 | 0.534 | 14 |
| 0.87 | 0.446 | 0.959 | 0.608 | 17 |
| **0.88** | **1.000** | **0.816** | **0.899** | 27 |
| 0.89 | 1.000 | 0.765 | 0.867 | 29 |
| 0.90 | 1.000 | 0.633 | 0.775 | 34 |

(gold: 21 true stories.)

## Findings — the harness overturned the spike

1. **The bilingual spike's 0.85 was wrong for production.** That spike measured
   only EN↔HI translation-pair *retrieval* (100% @1) and recommended ~0.85. But e5's
   absolute cosine sits uniformly high across *unrelated* Indian-news headlines
   (shared domain vocabulary), so at 0.85 the whole set over-merges to precision
   **0.288**. Only the full multi-story precision eval reveals this.
2. **Gate met at 0.88:** precision **1.000**, recall 0.816, F1 0.899 — and the two
   hard-adjacent pairs stay separate. `cluster_sim_threshold` is now **0.88**
   (was 0.85).
3. **Sharp cliff** between 0.87 (prec 0.446) and 0.88 (prec 1.000): clustering is
   very threshold-sensitive in e5's compressed band. Small drift → big precision
   swings. Mitigations below matter.
4. **Recall cost:** at 0.88 we miss ~18% of true same-story pairs (harder
   paraphrases / cross-lingual). The **nightly merge/split repair pass** is the
   recall safety net.

## Caveats & follow-ups (gate not yet formally closed)

- Precision 1.0 is on an **authored** set with clean distinctions; real feeds have
  messier near-duplicates. Expect lower precision on the real labelled 100. **Run
  `--export-labeling`, hand-label ~100 real stories, and re-tune.**
- The 0.87→0.88 cliff argues for a **two-stage gate** (SimHash/lexical pre-filter →
  vector confirm) and/or per-topic thresholds, not a single global cut.
- Validate `BAAI/bge-m3` as an alternative; its similarity distribution may be less
  compressed and more robust to the threshold cliff.
- Title-only here; production embeds title+snippet, which should help recall.

## Reproduce

```bash
cd worker && pip install -e ".[ml]"
python -m app.eval.run_precision --model intfloat/multilingual-e5-large
```
