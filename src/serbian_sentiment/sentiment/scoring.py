from __future__ import annotations

from collections.abc import Sequence

from ..lexicons.loader import Lexicon
from ..models import ScoreSummary, SenseDecision, UnitResult


def classify(score: float, threshold: float) -> str:
    if score > threshold:
        return "positive"
    if score < -threshold:
        return "negative"
    return "neutral"


def score_decisions(
    decisions: Sequence[SenseDecision],
    lexicon: Lexicon,
    *,
    threshold: float,
) -> ScoreSummary:
    units: list[UnitResult] = []
    values: list[float] = []
    for decision in decisions:
        record = (
            lexicon.records.get(decision.selected_sense_id)
            if decision.selected_sense_id is not None
            else None
        )
        if record is None:
            units.append(
                UnitResult(
                    token=decision.token,
                    selected_sense_id=decision.selected_sense_id,
                    candidate_sense_ids=decision.candidates,
                    backend=decision.backend,
                    pos=None,
                    neg=None,
                    net=None,
                    covered=False,
                    explanation=decision.explanation,
                )
            )
            continue
        net = round(record.pos - record.neg, 12)
        values.append(net)
        units.append(
            UnitResult(
                token=decision.token,
                selected_sense_id=decision.selected_sense_id,
                candidate_sense_ids=decision.candidates,
                backend=decision.backend,
                pos=record.pos,
                neg=record.neg,
                net=net,
                covered=True,
                explanation=decision.explanation,
            )
        )
    total = len(decisions)
    covered = len(values)
    coverage = round(covered / total, 12) if total else 0.0
    if not values:
        return ScoreSummary(None, "unscored", 0, total, coverage, tuple(units))
    score = round(sum(values) / covered, 12)
    return ScoreSummary(score, classify(score, threshold), covered, total, coverage, tuple(units))
