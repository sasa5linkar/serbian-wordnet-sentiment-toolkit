from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from .models import SenseDecision, TokenRecord


class Preprocessor(Protocol):
    def process(self, text: str) -> Sequence[TokenRecord]:
        """Return normalized token records for text."""


class SenseDisambiguator(Protocol):
    name: str

    def disambiguate(self, text: str, tokens: Sequence[TokenRecord]) -> Sequence[SenseDecision]:
        """Select a sense for each eligible token."""
