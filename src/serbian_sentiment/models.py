from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class DocumentInput:
    id: str
    text: str
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class TokenRecord:
    index: int
    text: str
    lemma: str
    upos: str
    start: int
    end: int
    sentence_index: int = 0


@dataclass(frozen=True)
class SenseDecision:
    token: TokenRecord
    selected_sense_id: str | None
    candidates: tuple[str, ...]
    backend: str
    explanation: str = ""


@dataclass(frozen=True)
class SentimentRecord:
    id: str
    pos: float
    neg: float
    lemmas: tuple[str, ...] = ()
    definition: str = ""
    wordnet_pos: str = ""


@dataclass(frozen=True)
class UnitResult:
    token: TokenRecord
    selected_sense_id: str | None
    candidate_sense_ids: tuple[str, ...]
    backend: str
    pos: float | None
    neg: float | None
    net: float | None
    covered: bool
    explanation: str = ""


@dataclass(frozen=True)
class ScoreSummary:
    score: float | None
    label: str
    covered_units: int
    total_units: int
    coverage: float
    units: tuple[UnitResult, ...]


@dataclass(frozen=True)
class AnalysisResult:
    document_id: str
    text: str
    lexicon: str
    backend: str
    score: float | None
    label: str
    covered_units: int
    total_units: int
    coverage: float
    units: tuple[UnitResult, ...]
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
