from __future__ import annotations

from collections.abc import Sequence

from .config import AnalyzerConfig
from .lexicons.loader import Lexicon
from .models import AnalysisResult, DocumentInput
from .protocols import Preprocessor, SenseDisambiguator
from .sentiment.scoring import score_decisions


class Analyzer:
    def __init__(
        self,
        *,
        config: AnalyzerConfig,
        preprocessor: Preprocessor,
        disambiguator: SenseDisambiguator,
        lexicon: Lexicon,
    ) -> None:
        self.config = config
        self.preprocessor = preprocessor
        self.disambiguator = disambiguator
        self.lexicon = lexicon

    def analyze(self, text: str, *, document_id: str = "text-1") -> AnalysisResult:
        tokens = self.preprocessor.process(text)
        decisions = self.disambiguator.disambiguate(text, tokens)
        summary = score_decisions(decisions, self.lexicon, threshold=self.config.threshold)
        warnings: tuple[str, ...] = ()
        if summary.coverage == 0:
            warnings = ("No WSD-selected synset was covered by the selected lexicon.",)
        return AnalysisResult(
            document_id=document_id,
            text=text,
            lexicon=self.lexicon.name,
            backend=self.disambiguator.name,
            score=summary.score,
            label=summary.label,
            covered_units=summary.covered_units,
            total_units=summary.total_units,
            coverage=summary.coverage,
            units=summary.units,
            warnings=warnings,
        )

    def analyze_many(self, documents: Sequence[DocumentInput]) -> tuple[AnalysisResult, ...]:
        results: list[AnalysisResult] = []
        for document in documents:
            results.append(self.analyze(document.text, document_id=document.id))
        return tuple(results)
