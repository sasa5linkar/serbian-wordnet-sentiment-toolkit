import json
from pathlib import Path

from serbian_sentiment.api import Analyzer
from serbian_sentiment.cli import main
from serbian_sentiment.config import AnalyzerConfig
from serbian_sentiment.lexicons.loader import load_lexicon
from serbian_sentiment.preprocessing.simple import SimplePreprocessor
from serbian_sentiment.wsd.overlap import OverlapSenseDisambiguator, load_sense_repository

FIXTURES = Path(__file__).parents[1] / "fixtures"


def make_analyzer() -> Analyzer:
    config = AnalyzerConfig(lexicon_file=FIXTURES / "lexicon.csv")
    return Analyzer(
        config=config,
        preprocessor=SimplePreprocessor(),
        disambiguator=OverlapSenseDisambiguator(load_sense_repository(FIXTURES / "senses.csv")),
        lexicon=load_lexicon(FIXTURES / "lexicon.csv"),
    )


def test_pipeline_analyzes_arbitrary_text() -> None:
    result = make_analyzer().analyze("Ово је одличан резултат.")
    assert result.label == "positive"
    assert result.coverage > 0
    assert any(unit.selected_sense_id == "ENG30-0001-a" for unit in result.units)


def test_cli_analyze_json(capsys) -> None:
    code = main(
        [
            "analyze",
            "--text",
            "Ово је одличан резултат.",
            "--lexicon-file",
            str(FIXTURES / "lexicon.csv"),
            "--sense-repo",
            str(FIXTURES / "senses.csv"),
            "--format",
            "json",
        ]
    )
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["label"] == "positive"
    assert payload["lexicon"] == "lexicon"


def test_cli_lexicon_validation(capsys) -> None:
    code = main(["lexicons", "validate", "--file", str(FIXTURES / "lexicon.csv")])
    assert code == 0
    assert "2" in capsys.readouterr().out


def test_cli_selects_named_lexicon_from_resource_directory(tmp_path: Path, capsys) -> None:
    resource_dir = tmp_path / "lexicons"
    resource_dir.mkdir()
    (resource_dir / "A7.csv").write_bytes((FIXTURES / "lexicon.csv").read_bytes())
    code = main(
        [
            "analyze",
            "--text",
            "Ово је одличан резултат.",
            "--lexicon",
            "A7",
            "--resource-dir",
            str(resource_dir),
            "--sense-repo",
            str(FIXTURES / "senses.csv"),
        ]
    )
    assert code == 0
    assert json.loads(capsys.readouterr().out)["lexicon"] == "A7"
