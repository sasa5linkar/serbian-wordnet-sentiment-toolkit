from pathlib import Path

from serbian_sentiment.resources import LocalResources


def test_local_resources_resolve_expected_layout(tmp_path: Path) -> None:
    resources = LocalResources.from_root(tmp_path)

    assert resources.preprocessing_model == tmp_path / "preprocessing" / "sr_pln_tesla_dbmu"
    assert resources.wsd_model == tmp_path / "wsd" / "wsd-distilled-mling"
    assert resources.sense_repository == tmp_path / "elexis" / "Elexis-WSD-Repo.xlsx"
    assert resources.lexicon("A7") == tmp_path / "lexicons" / "A7.csv"


def test_local_resources_report_availability(tmp_path: Path) -> None:
    resources = LocalResources.from_root(tmp_path)
    (tmp_path / "lexicons").mkdir(parents=True)
    resources.lexicon("A7").write_text("ID,POS,NEG\nx,0,0\n", encoding="utf-8")

    assert resources.availability()["lexicon_A7"] is True
    assert resources.availability()["preprocessing_model"] is False
