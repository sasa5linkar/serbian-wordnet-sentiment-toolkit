import json
from pathlib import Path

import pytest

from serbian_sentiment.cli import build_parser
from serbian_sentiment.errors import ResourceError
from serbian_sentiment.wsd.distilled import _encoding_settings


def test_saved_prefix_and_max_length_with_explicit_overrides(tmp_path: Path) -> None:
    (tmp_path / "training_config.json").write_text(json.dumps({"text_prefix": "query: "}))
    (tmp_path / "sentence_bert_config.json").write_text(json.dumps({"max_seq_length": 256}))
    assert _encoding_settings(tmp_path, None) == ("query: ", 256)
    assert _encoding_settings(tmp_path, "") == ("", 256)
    assert _encoding_settings(tmp_path, "custom: ") == ("custom: ", 256)


def test_plain_transformer_defaults(tmp_path: Path) -> None:
    assert _encoding_settings(tmp_path, None) == ("", 512)


@pytest.mark.parametrize("value", [None, 8, [], {}])
def test_invalid_prefix_is_not_silently_used(tmp_path: Path, value: object) -> None:
    (tmp_path / "training_config.json").write_text(json.dumps({"text_prefix": value}))
    with pytest.raises(ResourceError, match="text_prefix"):
        _encoding_settings(tmp_path, None)


def test_invalid_json_has_actionable_error(tmp_path: Path) -> None:
    (tmp_path / "training_config.json").write_text("{")
    with pytest.raises(ResourceError, match="invalid model configuration"):
        _encoding_settings(tmp_path, None)


def test_unsupported_pooling_is_rejected(tmp_path: Path) -> None:
    (tmp_path / "modules.json").write_text(
        json.dumps(
            [
                {"type": "sentence_transformers.models.Transformer", "path": ""},
                {"type": "sentence_transformers.models.Pooling", "path": "1_Pooling"},
            ]
        )
    )
    pool = tmp_path / "1_Pooling"
    pool.mkdir()
    (pool / "config.json").write_text(
        json.dumps({"pooling_mode_mean_tokens": False, "pooling_mode_cls_token": True})
    )
    with pytest.raises(ResourceError, match="unsupported"):
        _encoding_settings(tmp_path, None)
    (pool / "config.json").write_text(
        json.dumps({"pooling_mode_mean_tokens": True, "pooling_mode_cls_token": False})
    )
    assert _encoding_settings(tmp_path, None) == ("", 512)


@pytest.mark.parametrize("command", ["analyze", "explain"])
def test_cli_prefix_override(command: str) -> None:
    parser = build_parser()
    assert parser.parse_args([command, "--text", "Текст"]).text_prefix is None
    assert parser.parse_args([command, "--text", "Текст", "--text-prefix", ""]).text_prefix == ""
