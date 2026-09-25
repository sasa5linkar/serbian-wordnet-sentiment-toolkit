from pathlib import Path

from serbian_sentiment.preprocessing.simple import SimplePreprocessor
from serbian_sentiment.wsd.distilled import DistilledSenseDisambiguator
from serbian_sentiment.wsd.overlap import load_sense_repository

FIXTURES = Path(__file__).parents[1] / "fixtures"


class FakeRanker:
    def rank(self, text: str, definitions: list[str]) -> list[int]:
        assert text
        return list(reversed(range(len(definitions))))


def test_distilled_adapter_uses_ranker_order(tmp_path: Path) -> None:
    senses = tmp_path / "ambiguous.csv"
    senses.write_text(
        "ID,Lemme,Definicija,Vrsta\n"
        "sense-1,резултат,последица рада,n\n"
        "sense-2,резултат,спортски исход,n\n",
        encoding="utf-8",
    )
    repository = load_sense_repository(senses)
    tokens = SimplePreprocessor().process("Резултат је познат.")
    decisions = DistilledSenseDisambiguator(repository, FakeRanker()).disambiguate(
        "Резултат је познат.", tokens
    )
    target = next(item for item in decisions if item.token.lemma == "rezultat")
    assert target.selected_sense_id == "sense-2"
    assert target.backend == "distilled-transformer"
    assert target.candidates == ("sense-2", "sense-1")
