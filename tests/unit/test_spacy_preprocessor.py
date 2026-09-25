from pathlib import Path
from types import SimpleNamespace

import pytest

from serbian_sentiment.errors import ResourceError
from serbian_sentiment.preprocessing.spacy_adapter import SpacyPreprocessor


class FakeNLP:
    pipe_names = ("tagger", "trainable_lemmatizer")

    def add_pipe(self, name: str) -> None:
        self.pipe_names = (*self.pipe_names, name)

    def __call__(self, _text: str) -> list[SimpleNamespace]:
        sentence = SimpleNamespace(start=0)
        return [
            SimpleNamespace(
                i=0,
                text="Ово",
                lemma_="овај",
                pos_="PRON",
                idx=0,
                is_space=False,
                sent=sentence,
            ),
            SimpleNamespace(
                i=1,
                text=" ",
                lemma_=" ",
                pos_="SPACE",
                idx=3,
                is_space=True,
                sent=sentence,
            ),
            SimpleNamespace(
                i=2,
                text="ради",
                lemma_="радити",
                pos_="VERB",
                idx=4,
                is_space=False,
                sent=sentence,
            ),
        ]


def test_spacy_preprocessor_emits_pos_lemma_and_offsets() -> None:
    tokens = SpacyPreprocessor(nlp=FakeNLP()).process("Ово ради")

    assert [(token.text, token.lemma, token.upos) for token in tokens] == [
        ("Ово", "овај", "PRON"),
        ("ради", "радити", "VERB"),
    ]
    assert [(token.start, token.end, token.sentence_index) for token in tokens] == [
        (0, 3, 0),
        (4, 8, 0),
    ]


def test_spacy_preprocessor_rejects_missing_local_model(tmp_path: Path) -> None:
    with pytest.raises(ResourceError, match="spaCy preprocessing model directory not found"):
        SpacyPreprocessor(model_path=tmp_path / "missing")


def test_spacy_preprocessor_requires_pos_and_lemma_components() -> None:
    incomplete = FakeNLP()
    incomplete.pipe_names = ("tagger",)
    with pytest.raises(ResourceError, match="trainable_lemmatizer"):
        SpacyPreprocessor(nlp=incomplete)


def test_spacy_preprocessor_adds_sentence_boundaries_when_missing() -> None:
    nlp = FakeNLP()

    SpacyPreprocessor(nlp=nlp)

    assert "sentencizer" in nlp.pipe_names


def test_spacy_preprocessor_uses_tagger_label_when_pos_is_blank() -> None:
    sentence = SimpleNamespace(start=0)

    class BlankPosNLP(FakeNLP):
        def __call__(self, _text: str) -> list[SimpleNamespace]:
            return [
                SimpleNamespace(
                    text="тест",
                    lemma_="тест",
                    pos_="",
                    tag_="NOUN",
                    idx=0,
                    is_space=False,
                    sent=sentence,
                )
            ]

    tokens = SpacyPreprocessor(nlp=BlankPosNLP()).process("тест")

    assert tokens[0].upos == "NOUN"
