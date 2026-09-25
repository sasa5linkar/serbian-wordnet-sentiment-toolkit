from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .errors import ConfigurationError

DEFAULT_THRESHOLD = 0.01


@dataclass(frozen=True)
class AnalyzerConfig:
    lexicon: str | None = None
    lexicon_file: Path | None = None
    threshold: float = DEFAULT_THRESHOLD
    fail_fast: bool = True

    def __post_init__(self) -> None:
        if self.threshold < 0:
            raise ConfigurationError("threshold must be non-negative")
        if bool(self.lexicon) == bool(self.lexicon_file):
            raise ConfigurationError("select exactly one lexicon source")
