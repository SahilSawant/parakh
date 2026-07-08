"""
Pairwise clustering metrics — the M1 gate metric.

Over all unordered pairs of articles:
  - TP: same gold story AND same predicted cluster   (correct merge)
  - FP: different gold story BUT same predicted cluster (bad merge)
  - FN: same gold story BUT different predicted cluster (missed merge)
  - TN: different gold AND different predicted

  precision = TP / (TP + FP)   ← the "≥85% precision" gate: of the merges we make,
                                  how many are correct
  recall    = TP / (TP + FN)   ← of the merges we should make, how many we made
  F1        = harmonic mean

Precision is the gate because a false merge (two unrelated stories shown as one
coverage set) directly corrupts the bias distribution — the product's core claim.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PairwiseScore:
    precision: float
    recall: float
    f1: float
    tp: int
    fp: int
    fn: int
    tn: int
    n_items: int
    n_pred_clusters: int
    n_gold_clusters: int

    def gate_met(self, precision_gate: float = 0.85) -> bool:
        return self.precision >= precision_gate


def pairwise_score(gold: list, pred: list) -> PairwiseScore:
    """Compare a predicted clustering to gold labels. `gold`/`pred` are per-item
    labels of equal length; label identity (not value) defines a cluster."""
    if len(gold) != len(pred):
        raise ValueError("gold and pred must be the same length")

    n = len(gold)
    tp = fp = fn = tn = 0
    for i in range(n):
        for j in range(i + 1, n):
            same_gold = gold[i] == gold[j]
            same_pred = pred[i] == pred[j]
            if same_gold and same_pred:
                tp += 1
            elif not same_gold and same_pred:
                fp += 1
            elif same_gold and not same_pred:
                fn += 1
            else:
                tn += 1

    # No predicted pairs => no false merges => precision is perfect (vacuously).
    precision = tp / (tp + fp) if (tp + fp) else 1.0
    recall = tp / (tp + fn) if (tp + fn) else 1.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0

    return PairwiseScore(
        precision=round(precision, 4),
        recall=round(recall, 4),
        f1=round(f1, 4),
        tp=tp,
        fp=fp,
        fn=fn,
        tn=tn,
        n_items=n,
        n_pred_clusters=len(set(pred)),
        n_gold_clusters=len(set(gold)),
    )
