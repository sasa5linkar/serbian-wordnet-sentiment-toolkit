import sys
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def test_full_extra_declares_click_for_spacy_runtime() -> None:
    pyproject = Path(__file__).parents[2] / "pyproject.toml"
    config = tomllib.loads(pyproject.read_text(encoding="utf-8"))

    full_dependencies = config["project"]["optional-dependencies"]["full"]

    assert any(dependency.lower().startswith("click") for dependency in full_dependencies)
