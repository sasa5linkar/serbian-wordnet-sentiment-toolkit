"""Numerical pooling/prefix checks with a tiny local random encoder; no downloads."""

import json
from pathlib import Path

import pytest


def test_local_encoder_matches_reference_and_prefix_override(tmp_path: Path) -> None:
    torch = pytest.importorskip("torch")
    transformers = pytest.importorskip("transformers")
    from serbian_sentiment.wsd.distilled import TransformerEmbeddingRanker

    vocab = [
        "[PAD]",
        "[UNK]",
        "[CLS]",
        "[SEP]",
        "[MASK]",
        "query",
        ":",
        "он",
        "је",
        "љубазан",
        "добар",
        ".",
    ]
    (tmp_path / "vocab.txt").write_text("\n".join(vocab), encoding="utf-8")
    tokenizer = transformers.BertTokenizerFast(vocab_file=str(tmp_path / "vocab.txt"))
    tokenizer.save_pretrained(tmp_path)
    torch.manual_seed(17)
    config = transformers.BertConfig(
        vocab_size=len(vocab),
        hidden_size=16,
        num_hidden_layers=1,
        num_attention_heads=2,
        intermediate_size=24,
        max_position_embeddings=32,
    )
    model = transformers.BertModel(config)
    model.save_pretrained(tmp_path)
    (tmp_path / "training_config.json").write_text(json.dumps({"text_prefix": "query: "}))
    (tmp_path / "sentence_bert_config.json").write_text(json.dumps({"max_seq_length": 12}))
    ranker = TransformerEmbeddingRanker(tmp_path)
    texts = ["Он је љубазан.", "query: добар.", "Он је љубазан. " * 20]
    actual = ranker._encode(texts)
    batch = tokenizer(
        ["query: Он је љубазан.", "query: добар.", "query: " + texts[2]],
        padding=True,
        truncation=True,
        max_length=12,
        return_tensors="pt",
    )
    model.eval()
    with torch.no_grad():
        hidden = model(**batch).last_hidden_state
        mask = batch["attention_mask"].unsqueeze(-1).to(hidden.dtype)
        expected = torch.nn.functional.normalize((hidden * mask).sum(1) / mask.sum(1), dim=1)
    torch.testing.assert_close(actual, expected)
    assert ranker.rank(texts[0], []) == []
    assert ranker.rank(texts[0], ["добар."]) == [0]
    assert (
        ranker.rank(texts[0], texts[1:])
        == torch.argsort(actual[0] @ actual[1:].T, descending=True).tolist()
    )
    no_prefix = TransformerEmbeddingRanker(tmp_path, text_prefix="")
    assert not torch.allclose(actual[0], no_prefix._encode([texts[0]])[0])
