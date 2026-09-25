from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any, Protocol

from ..errors import ResourceError
from ..models import SenseDecision, TokenRecord
from ..text import normalize_lemma
from .overlap import SenseRepository


class DefinitionRanker(Protocol):
    def rank(self, text: str, definitions: list[str]) -> list[int]:
        """Return candidate indexes from best to worst."""


def _read_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ResourceError(f"invalid model configuration: {path.name}") from exc
    if not isinstance(value, dict):
        raise ResourceError(f"model configuration must be an object: {path.name}")
    return value


def _encoding_settings(path: Path, text_prefix: str | None) -> tuple[str, int]:
    training = _read_config(path / "training_config.json")
    prefix = training.get("text_prefix", "") if text_prefix is None else text_prefix
    if not isinstance(prefix, str):
        raise ResourceError("training_config.json text_prefix must be a string")
    sentence = _read_config(path / "sentence_bert_config.json")
    max_length = sentence.get("max_seq_length", 512)
    if isinstance(max_length, bool) or not isinstance(max_length, int) or max_length < 1:
        raise ResourceError("sentence_bert_config.json max_seq_length must be a positive integer")
    # This adapter implements Transformer -> mean Pooling -> optional Normalize.
    modules_path = path / "modules.json"
    if modules_path.exists():
        try:
            modules = json.loads(modules_path.read_text(encoding="utf-8"))
            kinds = [module["type"].rsplit(".", 1)[-1] for module in modules]
            if kinds not in (["Transformer", "Pooling"], ["Transformer", "Pooling", "Normalize"]):
                raise ValueError("unsupported modules")
            if modules[0].get("path", ""):
                raise ValueError("transformer must be stored at the model root")
            pooling = _read_config(path / modules[1]["path"] / "config.json")
            if not pooling.get("pooling_mode_mean_tokens") or any(
                value
                for key, value in pooling.items()
                if key.startswith("pooling_mode_") and key != "pooling_mode_mean_tokens"
            ):
                raise ValueError("unsupported pooling")
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
            raise ResourceError("model requires an unsupported SentenceTransformer layout") from exc
    return prefix, max_length


class TransformerEmbeddingRanker:
    """Local transformer mean-pooling ranker with no network fallback."""

    def __init__(self, model_path: str | Path, *, text_prefix: str | None = None) -> None:
        path = Path(model_path)
        if not path.is_dir():
            raise ResourceError(f"distilled WSD model directory not found: {path}")
        prefix, max_length = _encoding_settings(path, text_prefix)
        try:
            import torch
            from transformers import AutoModel, AutoTokenizer
        except ImportError as exc:
            raise ResourceError(
                "install the wsd extra to use the distilled backend: pip install -e .[wsd]"
            ) from exc
        self.torch = torch
        self.text_prefix = prefix
        self.max_length = max_length
        self.tokenizer = AutoTokenizer.from_pretrained(path, local_files_only=True)
        self.model = AutoModel.from_pretrained(path, local_files_only=True)
        self.model.eval()

    def _encode(self, texts: list[str]) -> Any:
        inputs = [
            text if text.startswith(self.text_prefix) else self.text_prefix + text for text in texts
        ]
        with self.torch.no_grad():
            batch = self.tokenizer(
                inputs,
                padding=True,
                truncation=True,
                max_length=self.max_length,
                return_tensors="pt",
            )
            output = self.model(**batch).last_hidden_state
            mask = batch["attention_mask"].unsqueeze(-1).to(output.dtype)
            pooled = (output * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1e-9)
            return self.torch.nn.functional.normalize(pooled, p=2, dim=1)

    def rank(self, text: str, definitions: list[str]) -> list[int]:
        if not definitions:
            return []
        embeddings = self._encode([text, *definitions])
        scores = (embeddings[0:1] @ embeddings[1:].T).squeeze(0).tolist()
        return [
            index
            for index, _score in sorted(enumerate(scores), key=lambda item: item[1], reverse=True)
        ]


class DistilledSenseDisambiguator:
    name = "distilled-transformer"

    def __init__(self, repository: SenseRepository, ranker: DefinitionRanker) -> None:
        self.repository = repository
        self.ranker = ranker

    def disambiguate(
        self,
        text: str,
        tokens: Sequence[TokenRecord],
    ) -> tuple[SenseDecision, ...]:
        decisions: list[SenseDecision] = []
        for token in tokens:
            candidates = self.repository.by_lemma.get(normalize_lemma(token.lemma), ())
            order = self.ranker.rank(text, [item.definition for item in candidates])
            ranked = tuple(candidates[index] for index in order)
            selected = ranked[0].id if ranked else None
            decisions.append(
                SenseDecision(
                    token=token,
                    selected_sense_id=selected,
                    candidates=tuple(item.id for item in ranked),
                    backend=self.name,
                    explanation=(
                        f"Selected by distilled transformer from {len(ranked)} candidate(s)."
                        if ranked
                        else "No candidate sense was found for the normalized lemma."
                    ),
                )
            )
        return tuple(decisions)
