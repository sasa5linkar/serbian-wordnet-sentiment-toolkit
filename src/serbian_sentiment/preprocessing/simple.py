from __future__ import annotations

import re

from ..models import TokenRecord
from ..text import normalize_lemma

WORD_RE = re.compile(r"[^\W\d_]+(?:-[^\W\d_]+)*", re.UNICODE)


class SimplePreprocessor:
    """Dependency-free Serbian tokenizer with lowercase surface lemmas.

    This adapter is useful for demonstrations and already-lemmatized text. It
    does not claim morphological lemmatization; production users should supply
    a richer adapter when processing inflected Serbian.
    """

    def process(self, text: str) -> tuple[TokenRecord, ...]:
        tokens: list[TokenRecord] = []
        sentence_index = 0
        for index, match in enumerate(WORD_RE.finditer(text), start=1):
            prefix = text[: match.start()]
            sentence_index = sum(prefix.count(mark) for mark in ".!?")
            form = match.group(0)
            tokens.append(
                TokenRecord(
                    index=index,
                    text=form,
                    lemma=normalize_lemma(form),
                    upos="",
                    start=match.start(),
                    end=match.end(),
                    sentence_index=sentence_index,
                )
            )
        return tuple(tokens)
