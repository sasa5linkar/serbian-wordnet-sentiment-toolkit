from __future__ import annotations

from pathlib import Path
from typing import Any

from ..errors import ResourceError
from ..models import TokenRecord


class SpacyPreprocessor:
    """Serbian POS and lemma preprocessing backed by a local spaCy pipeline."""

    REQUIRED_COMPONENTS = ("tagger", "trainable_lemmatizer")

    def __init__(
        self,
        model_path: str | Path | None = None,
        *,
        nlp: Any | None = None,
    ) -> None:
        if nlp is None:
            if model_path is None:
                raise ResourceError("a local spaCy preprocessing model path is required")
            path = Path(model_path)
            if not path.is_dir():
                raise ResourceError(f"spaCy preprocessing model directory not found: {path}")
            try:
                import spacy
            except ImportError as exc:
                raise ResourceError(
                    "install the full extra to use spaCy preprocessing: pip install -e .[full]"
                ) from exc
            try:
                nlp = spacy.load(path)
            except Exception as exc:
                raise ResourceError(
                    f"could not load spaCy preprocessing model at {path}: {exc}"
                ) from exc
        missing = [name for name in self.REQUIRED_COMPONENTS if name not in nlp.pipe_names]
        if missing:
            raise ResourceError(
                "spaCy preprocessing model is missing required component(s): "
                + ", ".join(missing)
            )
        if not {"parser", "senter", "sentencizer"}.intersection(nlp.pipe_names):
            nlp.add_pipe("sentencizer")
        self._nlp = nlp

    def process(self, text: str) -> tuple[TokenRecord, ...]:
        doc = self._nlp(text)
        sentence_numbers: dict[int, int] = {}
        records: list[TokenRecord] = []
        for token in doc:
            if token.is_space:
                continue
            sentence_start = int(token.sent.start)
            if sentence_start not in sentence_numbers:
                sentence_numbers[sentence_start] = len(sentence_numbers)
            records.append(
                TokenRecord(
                    index=len(records) + 1,
                    text=str(token.text),
                    lemma=str(token.lemma_),
                    upos=str(token.pos_ or token.tag_),
                    start=int(token.idx),
                    end=int(token.idx) + len(str(token.text)),
                    sentence_index=sentence_numbers[sentence_start],
                )
            )
        return tuple(records)
