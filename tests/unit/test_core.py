from pathlib import Path

import pytest

from serbian_sentiment.cli import build_parser
from serbian_sentiment.config import AnalyzerConfig
from serbian_sentiment.errors import ConfigurationError, LexiconValidationError
from serbian_sentiment.lexicons.loader import load_lexicon
from serbian_sentiment.models import SenseDecision, TokenRecord
from serbian_sentiment.sentiment.scoring import score_decisions

FIXTURES = Path(__file__).parents[1] / "fixtures"


def test_calibrated_a7_wsd_threshold_is_the_public_default() -> None:
    config = AnalyzerConfig(lexicon="A7")
    analyze_args = build_parser().parse_args(["analyze", "--text", "тест"])
    explain_args = build_parser().parse_args(["explain", "--text", "тест"])

    assert config.threshold == 0.01
    assert analyze_args.threshold == 0.01
    assert explain_args.threshold == 0.01


def test_public_threshold_can_be_overridden() -> None:
    config = AnalyzerConfig(lexicon="A7", threshold=0.42)
    analyze_args = build_parser().parse_args(
        ["analyze", "--text", "тест", "--threshold", "0.42"]
    )
    explain_args = build_parser().parse_args(
        ["explain", "--text", "тест", "--threshold", "0.42"]
    )

    assert config.threshold == 0.42
    assert analyze_args.threshold == 0.42
    assert explain_args.threshold == 0.42


def test_config_requires_exactly_one_lexicon_source() -> None:
    with pytest.raises(ConfigurationError):
        AnalyzerConfig()
    with pytest.raises(ConfigurationError):
        AnalyzerConfig(lexicon="A7", lexicon_file=FIXTURES / "lexicon.csv")
    with pytest.raises(ConfigurationError):
        AnalyzerConfig(lexicon_file=FIXTURES / "lexicon.csv", threshold=-0.1)


def test_load_lexicon_and_score_selected_synset() -> None:
    lexicon = load_lexicon(FIXTURES / "lexicon.csv")
    token = TokenRecord(index=1, text="одличан", lemma="одличан", upos="ADJ", start=0, end=7)
    decision = SenseDecision(
        token=token,
        selected_sense_id="ENG30-0001-a",
        candidates=("ENG30-0001-a",),
        backend="fixture",
    )
    result = score_decisions((decision,), lexicon, threshold=0.33)
    assert result.label == "positive"
    assert result.score == 0.75
    assert result.covered_units == 1
    assert result.coverage == 1.0


def test_zero_coverage_is_unscored() -> None:
    lexicon = load_lexicon(FIXTURES / "lexicon.csv")
    token = TokenRecord(index=1, text="непознат", lemma="непознат", upos="ADJ", start=0, end=8)
    decision = SenseDecision(
        token=token, selected_sense_id="missing", candidates=("missing",), backend="fixture"
    )
    result = score_decisions((decision,), lexicon, threshold=0.33)
    assert result.label == "unscored"
    assert result.score is None
    assert result.coverage == 0.0


def test_invalid_lexicon_columns_are_rejected(tmp_path: Path) -> None:
    path = tmp_path / "bad.csv"
    path.write_text("ID,POS\nx,0.2\n", encoding="utf-8")
    with pytest.raises(LexiconValidationError):
        load_lexicon(path)
