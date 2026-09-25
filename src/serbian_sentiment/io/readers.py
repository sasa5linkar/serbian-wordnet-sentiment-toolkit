from __future__ import annotations

import csv
from collections.abc import Iterable
from pathlib import Path

from ..errors import InputValidationError
from ..models import DocumentInput


def read_documents(
    path: str | Path,
    *,
    text_column: str = "text",
    id_column: str | None = None,
    one_per_line: bool = False,
) -> tuple[DocumentInput, ...]:
    source = Path(path)
    if not source.is_file():
        raise InputValidationError(f"input file not found: {source}")
    suffix = source.suffix.casefold()
    if suffix == ".txt":
        text = source.read_text(encoding="utf-8-sig")
        values = text.splitlines() if one_per_line else [text]
        return _validated(
            DocumentInput(str(index), value) for index, value in enumerate(values, start=1)
        )
    if suffix not in {".csv", ".tsv"}:
        raise InputValidationError("input must be TXT, CSV, or TSV")
    delimiter = "\t" if suffix == ".tsv" else ","
    with source.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        if text_column not in (reader.fieldnames or ()):
            raise InputValidationError(f"text column not found: {text_column}")
        rows = [
            DocumentInput(
                id=(row.get(id_column) or str(index)) if id_column else str(index),
                text=row.get(text_column) or "",
            )
            for index, row in enumerate(reader, start=1)
        ]
    return _validated(rows)


def _validated(documents: Iterable[DocumentInput]) -> tuple[DocumentInput, ...]:
    result = tuple(documents)
    ids: set[str] = set()
    for document in result:
        if not document.text.strip():
            raise InputValidationError(f"empty text for document {document.id}")
        if document.id in ids:
            raise InputValidationError(f"duplicate document ID: {document.id}")
        ids.add(document.id)
    return result
