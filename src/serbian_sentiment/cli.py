from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .api import Analyzer
from .config import DEFAULT_THRESHOLD, AnalyzerConfig
from .errors import (
    ConfigurationError,
    InputValidationError,
    LexiconValidationError,
    ProcessingError,
    ResourceError,
)
from .io.readers import read_documents
from .io.writers import write_results
from .lexicons.loader import load_lexicon
from .models import DocumentInput
from .preprocessing.simple import SimplePreprocessor
from .preprocessing.spacy_adapter import SpacyPreprocessor
from .protocols import Preprocessor, SenseDisambiguator
from .resources import LocalResources
from .wsd.distilled import DistilledSenseDisambiguator, TransformerEmbeddingRanker
from .wsd.overlap import OverlapSenseDisambiguator, load_sense_repository

_THRESHOLD_HELP = (
    f"symmetric decision threshold (default: {DEFAULT_THRESHOLD:g}, calibrated for A7/S7 + WSD)"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sr-sentiment",
        description="Explainable Serbian WordNet sentiment analysis with WSD.",
        allow_abbrev=False,
    )
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)

    analyze = commands.add_parser("analyze", help="Analyze direct text or a TXT/CSV/TSV file.")
    source = analyze.add_mutually_exclusive_group(required=True)
    source.add_argument("--text")
    source.add_argument("--input", type=Path)
    analyze.add_argument("--text-column", default="text")
    analyze.add_argument("--id-column")
    analyze.add_argument("--one-per-line", action="store_true")
    lexicon_source = analyze.add_mutually_exclusive_group()
    lexicon_source.add_argument("--lexicon-file", type=Path)
    lexicon_source.add_argument("--lexicon")
    analyze.add_argument("--resource-root", type=Path, default=Path(".local-resources"))
    analyze.add_argument("--resource-dir", type=Path)
    analyze.add_argument("--sense-repo", type=Path)
    analyze.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=_THRESHOLD_HELP,
    )
    analyze.add_argument("--backend", choices=("auto", "overlap", "distilled"), default="auto")
    analyze.add_argument("--model", type=Path)
    analyze.add_argument(
        "--text-prefix",
        default=None,
        help="override the prefix saved in training_config.json (empty string disables it)",
    )
    analyze.add_argument("--preprocessor", choices=("auto", "simple", "spacy"), default="auto")
    analyze.add_argument("--preprocessor-model", type=Path)
    analyze.add_argument("--format", choices=("json", "jsonl", "csv", "tsv"), default="json")
    analyze.add_argument("--output", type=Path)
    analyze.set_defaults(func=_cmd_analyze)

    explain = commands.add_parser("explain", help="Analyze one text with token-level details.")
    explain.add_argument("--text", required=True)
    explain_lexicon = explain.add_mutually_exclusive_group()
    explain_lexicon.add_argument("--lexicon-file", type=Path)
    explain_lexicon.add_argument("--lexicon")
    explain.add_argument("--resource-root", type=Path, default=Path(".local-resources"))
    explain.add_argument("--resource-dir", type=Path)
    explain.add_argument("--sense-repo", type=Path)
    explain.add_argument(
        "--threshold",
        type=float,
        default=DEFAULT_THRESHOLD,
        help=_THRESHOLD_HELP,
    )
    explain.add_argument("--backend", choices=("auto", "overlap", "distilled"), default="auto")
    explain.add_argument("--model", type=Path)
    explain.add_argument(
        "--text-prefix",
        default=None,
        help="override the prefix saved in training_config.json (empty string disables it)",
    )
    explain.add_argument("--preprocessor", choices=("auto", "simple", "spacy"), default="auto")
    explain.add_argument("--preprocessor-model", type=Path)
    explain.set_defaults(func=_cmd_analyze, format="json", output=None, input=None)

    lexicons = commands.add_parser("lexicons", help="Inspect sentiment lexicons.")
    lexicon_commands = lexicons.add_subparsers(dest="lexicon_command", required=True)
    validate = lexicon_commands.add_parser("validate", help="Validate a lexicon CSV.")
    validate.add_argument("--file", type=Path, required=True)
    validate.set_defaults(func=_cmd_validate_lexicon)
    listing = lexicon_commands.add_parser("list", help="List CSV lexicons in a directory.")
    listing.add_argument("--resource-dir", type=Path, default=Path("resources/lexicons"))
    listing.set_defaults(func=_cmd_list_lexicons)

    resources = commands.add_parser("resources", help="Check configured resources.")
    resource_commands = resources.add_subparsers(dest="resource_command", required=True)
    check = resource_commands.add_parser("check")
    check.add_argument("--lexicon-file", type=Path)
    check.add_argument("--sense-repo", type=Path)
    check.set_defaults(func=_cmd_check_resources)
    check_local = resource_commands.add_parser(
        "check-local", help="Verify the complete local resource layout."
    )
    check_local.add_argument("--resource-root", type=Path, default=Path(".local-resources"))
    check_local.set_defaults(func=_cmd_check_local_resources)
    return parser


def _make_analyzer(args: argparse.Namespace) -> Analyzer:
    local = LocalResources.from_root(args.resource_root)
    if args.lexicon_file is not None:
        lexicon_path = args.lexicon_file
        config = AnalyzerConfig(lexicon_file=lexicon_path, threshold=args.threshold)
    else:
        lexicon_name = args.lexicon or "A7"
        lexicon_directory = args.resource_dir or local.lexicon_directory
        lexicon_path = lexicon_directory / f"{lexicon_name}.csv"
        config = AnalyzerConfig(lexicon=lexicon_name, threshold=args.threshold)
    lexicon = load_lexicon(lexicon_path)
    if args.lexicon_file is None:
        lexicon = type(lexicon)(
            name=config.lexicon or lexicon.name,
            records=lexicon.records,
            source=lexicon.source,
        )
    sense_repository = args.sense_repo or local.sense_repository
    repository = load_sense_repository(sense_repository)
    model_path = args.model or local.wsd_model
    backend = args.backend
    if backend == "auto":
        backend = "distilled" if model_path.is_dir() else "overlap"
    disambiguator: SenseDisambiguator
    if backend == "distilled":
        disambiguator = DistilledSenseDisambiguator(
            repository, TransformerEmbeddingRanker(model_path, text_prefix=args.text_prefix)
        )
    else:
        disambiguator = OverlapSenseDisambiguator(repository)
    preprocessor = _make_preprocessor(args, local)
    return Analyzer(
        config=config,
        preprocessor=preprocessor,
        disambiguator=disambiguator,
        lexicon=lexicon,
    )


def _make_preprocessor(args: argparse.Namespace, local: LocalResources) -> Preprocessor:
    model_path = args.preprocessor_model or local.preprocessing_model
    if args.preprocessor == "spacy":
        return SpacyPreprocessor(model_path)
    if args.preprocessor == "auto" and model_path.is_dir():
        return SpacyPreprocessor(model_path)
    return SimplePreprocessor()


def _cmd_analyze(args: argparse.Namespace) -> int:
    analyzer = _make_analyzer(args)
    documents: tuple[DocumentInput, ...]
    if getattr(args, "text", None) is not None:
        documents = (DocumentInput("text-1", args.text),)
    else:
        documents = read_documents(
            args.input,
            text_column=args.text_column,
            id_column=args.id_column,
            one_per_line=args.one_per_line,
        )
    results = analyzer.analyze_many(documents)
    write_results(results, output_format=args.format, output=args.output)
    return 0


def _cmd_validate_lexicon(args: argparse.Namespace) -> int:
    lexicon = load_lexicon(args.file)
    print(json.dumps({"name": lexicon.name, "rows": len(lexicon.records)}, ensure_ascii=False))
    return 0


def _cmd_list_lexicons(args: argparse.Namespace) -> int:
    paths = sorted(args.resource_dir.glob("*.csv")) if args.resource_dir.is_dir() else []
    print(json.dumps([{"name": path.stem, "path": str(path)} for path in paths], indent=2))
    return 0


def _cmd_check_resources(args: argparse.Namespace) -> int:
    payload = {
        "lexicon": bool(args.lexicon_file and args.lexicon_file.is_file()),
        "sense_repository": bool(args.sense_repo and args.sense_repo.is_file()),
    }
    print(json.dumps(payload))
    return 0 if all(payload.values()) else 3


def _cmd_check_local_resources(args: argparse.Namespace) -> int:
    payload = LocalResources.from_root(args.resource_root).availability()
    print(json.dumps(payload, indent=2))
    return 0 if all(payload.values()) else 3


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8")
    try:
        args = build_parser().parse_args(argv)
        return int(args.func(args))
    except (ConfigurationError, LexiconValidationError) as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        return 2
    except ResourceError as exc:
        print(f"resource error: {exc}", file=sys.stderr)
        return 3
    except InputValidationError as exc:
        print(f"input error: {exc}", file=sys.stderr)
        return 4
    except ProcessingError as exc:
        print(f"processing error: {exc}", file=sys.stderr)
        return 5


if __name__ == "__main__":
    raise SystemExit(main())
