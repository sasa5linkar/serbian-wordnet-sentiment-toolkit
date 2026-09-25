import json
from pathlib import Path

from openpyxl import Workbook

from serbian_sentiment import cli
from serbian_sentiment.preprocessing.simple import SimplePreprocessor

FIXTURES = Path(__file__).parents[1] / "fixtures"


def test_cli_resolves_local_a7_and_elexis_defaults(tmp_path: Path, capsys) -> None:
    root = tmp_path / ".local-resources"
    (root / "lexicons").mkdir(parents=True)
    (root / "elexis").mkdir()
    (root / "lexicons" / "A7.csv").write_bytes((FIXTURES / "lexicon.csv").read_bytes())
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "SrWSD-v2"
    sheet.append(("pos", "upos", "lemma", "senseID", "definition", "literals"))
    sheet.append(
        ("A", "ADJ", "одличан", "ENG30-0001-a", "који има веома добре особине", "одличан")
    )
    workbook.save(root / "elexis" / "Elexis-WSD-Repo.xlsx")

    code = cli.main(
        [
            "analyze",
            "--text",
            "Ово је одличан резултат.",
            "--resource-root",
            str(root),
            "--backend",
            "overlap",
            "--preprocessor",
            "simple",
        ]
    )

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["lexicon"] == "A7"
    assert payload["label"] == "positive"


def test_cli_builds_spacy_preprocessor_when_explicit(
    tmp_path: Path, monkeypatch
) -> None:
    model_path = tmp_path / "model"
    model_path.mkdir()
    selected: dict[str, Path] = {}

    def fake_spacy(path: Path) -> SimplePreprocessor:
        selected["path"] = path
        return SimplePreprocessor()

    monkeypatch.setattr(cli, "SpacyPreprocessor", fake_spacy)
    args = cli.build_parser().parse_args(
        [
            "analyze",
            "--text",
            "Ово ради.",
            "--lexicon-file",
            str(FIXTURES / "lexicon.csv"),
            "--sense-repo",
            str(FIXTURES / "senses.csv"),
            "--backend",
            "overlap",
            "--preprocessor",
            "spacy",
            "--preprocessor-model",
            str(model_path),
        ]
    )

    cli._make_analyzer(args)

    assert selected["path"] == model_path


def test_cli_checks_local_resource_layout(tmp_path: Path, capsys) -> None:
    root = tmp_path / ".local-resources"
    resources = cli.LocalResources.from_root(root)
    resources.preprocessing_model.mkdir(parents=True)
    resources.wsd_model.mkdir(parents=True)
    resources.sense_repository.parent.mkdir(parents=True)
    resources.sense_repository.touch()
    resources.lexicon_directory.mkdir(parents=True)
    for name in ("S0", "A1", "A2", "A3", "A4", "A5", "A6", "A7"):
        resources.lexicon(name).touch()

    code = cli.main(
        ["resources", "check-local", "--resource-root", str(root)]
    )

    assert code == 0
    assert all(json.loads(capsys.readouterr().out).values())
