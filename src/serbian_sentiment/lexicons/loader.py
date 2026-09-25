from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from ..errors import LexiconValidationError
from ..models import SentimentRecord

REQUIRED_COLUMNS = {"ID", "POS", "NEG"}


@dataclass(frozen=True)
class Lexicon:
    name: str
    records: dict[str, SentimentRecord]
    source: Path


def load_lexicon(path: str | Path) -> Lexicon:
    source = Path(path)
    if not source.is_file():
        raise LexiconValidationError(f"lexicon file not found: {source}")
    with source.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or ())
        missing = REQUIRED_COLUMNS - columns
        if missing:
            raise LexiconValidationError(
                "lexicon is missing required columns: " + ", ".join(sorted(missing))
            )
        records: dict[str, SentimentRecord] = {}
        for line, row in enumerate(reader, start=2):
            sense_id = (row.get("ID") or "").strip()
            if not sense_id:
                raise LexiconValidationError(f"line {line}: ID is empty")
            try:
                pos = float(row["POS"])
                neg = float(row["NEG"])
            except (TypeError, ValueError) as exc:
                raise LexiconValidationError(f"line {line}: POS and NEG must be numeric") from exc
            if not 0.0 <= pos <= 1.0 or not 0.0 <= neg <= 1.0:
                raise LexiconValidationError(f"line {line}: POS and NEG must be in [0, 1]")
            record = SentimentRecord(
                id=sense_id,
                pos=pos,
                neg=neg,
                lemmas=tuple(
                    item.strip().casefold()
                    for item in (row.get("Lemme") or "").split(",")
                    if item.strip()
                ),
                definition=(row.get("Definicija") or "").strip(),
                wordnet_pos=(row.get("Vrsta") or "").strip().casefold(),
            )
            previous = records.get(sense_id)
            if previous is not None and previous != record:
                raise LexiconValidationError(f"line {line}: conflicting duplicate ID {sense_id}")
            records[sense_id] = record
    return Lexicon(name=source.stem, records=records, source=source)
