from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import TextIO

from ..models import AnalysisResult


def write_results(
    results: tuple[AnalysisResult, ...],
    *,
    output_format: str,
    output: str | Path | None = None,
) -> None:
    handle: TextIO
    close = False
    if output is None:
        handle = sys.stdout
    else:
        handle = Path(output).open("w", encoding="utf-8-sig", newline="")
        close = True
    try:
        if output_format == "json":
            payload = (
                results[0].to_dict() if len(results) == 1 else [item.to_dict() for item in results]
            )
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        elif output_format == "jsonl":
            for result in results:
                handle.write(json.dumps(result.to_dict(), ensure_ascii=False) + "\n")
        elif output_format in {"csv", "tsv"}:
            delimiter = "\t" if output_format == "tsv" else ","
            fields = [
                "document_id",
                "text",
                "lexicon",
                "backend",
                "score",
                "label",
                "covered_units",
                "total_units",
                "coverage",
            ]
            writer = csv.DictWriter(handle, fieldnames=fields, delimiter=delimiter)
            writer.writeheader()
            for result in results:
                row = result.to_dict()
                writer.writerow({field: row[field] for field in fields})
        else:
            raise ValueError(f"unsupported output format: {output_format}")
    finally:
        if close:
            handle.close()
