from pathlib import Path

import pytest

from serbian_sentiment.errors import ResourceError
from serbian_sentiment.wsd.overlap import load_sense_repository

openpyxl = pytest.importorskip("openpyxl")


def _write_workbook(
    path: Path,
    *,
    sheet: str = "SrWSD-v2",
    headers: tuple[str, ...] | None = None,
) -> None:
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = sheet
    worksheet.append(headers or ("pos", "upos", "lemma", "senseID", "definition", "literals"))
    worksheet.append(
        ("A", "ADJ", "одличан", "ENG30-0001-a", "који има веома добре особине", "одличан")
    )
    workbook.save(path)


def test_load_elexis_xlsx_maps_real_column_names(tmp_path: Path) -> None:
    path = tmp_path / "elexis.xlsx"
    _write_workbook(path)

    repository = load_sense_repository(path)

    assert len(repository.entries) == 1
    assert repository.entries[0].id == "ENG30-0001-a"
    assert repository.entries[0].definition == "који има веома добре особине"
    assert repository.entries[0].wordnet_pos == "a"
    assert repository.by_lemma["odličan"][0].id == "ENG30-0001-a"


def test_load_elexis_xlsx_requires_expected_sheet(tmp_path: Path) -> None:
    path = tmp_path / "elexis.xlsx"
    _write_workbook(path, sheet="other")

    with pytest.raises(ResourceError, match="SrWSD-v2"):
        load_sense_repository(path)


def test_load_elexis_xlsx_requires_columns(tmp_path: Path) -> None:
    path = tmp_path / "elexis.xlsx"
    _write_workbook(path, headers=("lemma", "definition"))

    with pytest.raises(ResourceError, match="senseID"):
        load_sense_repository(path)
