import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).parents[2] / "scripts" / "verify_release.py"
SPEC = importlib.util.spec_from_file_location("verify_release", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

SYNTHETIC_LOCAL_PATH = 'MODEL = r"' + "C:" + '\\Users\\name\\model"\n'


def test_repository_audit_detects_absolute_windows_path(tmp_path: Path) -> None:
    (tmp_path / "bad.py").write_text(SYNTHETIC_LOCAL_PATH, encoding="utf-8")
    findings = MODULE.scan_repository(tmp_path)
    assert any("absolute Windows path" in item for item in findings)


def test_repository_audit_ignores_virtual_environment(tmp_path: Path) -> None:
    hidden = tmp_path / ".venv"
    hidden.mkdir()
    (hidden / "bad.py").write_text(SYNTHETIC_LOCAL_PATH, encoding="utf-8")
    assert MODULE.scan_repository(tmp_path) == []


def test_repository_audit_ignores_local_resource_store(tmp_path: Path) -> None:
    hidden = tmp_path / ".local-resources"
    hidden.mkdir()
    (hidden / "model.safetensors").write_bytes(b"local model")
    assert MODULE.scan_repository(tmp_path) == []
