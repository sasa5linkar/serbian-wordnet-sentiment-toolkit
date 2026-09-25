"""Audit a release tree for machine-local paths and unsafe bundled artifacts."""

from __future__ import annotations

import re
import sys
from pathlib import Path

IGNORED_DIRECTORIES = {
    ".git",
    ".local-resources",
    ".local-smoke",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    ".worktrees",
    "__pycache__",
    "build",
    "dist",
}
TEXT_SUFFIXES = {".cff", ".csv", ".json", ".md", ".py", ".toml", ".tsv", ".txt", ".yaml", ".yml"}
FORBIDDEN_SUFFIXES = {".ckpt", ".key", ".onnx", ".pkl", ".pt", ".safetensors"}
WINDOWS_ABSOLUTE_PATH = re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]")


def scan_repository(root: Path) -> list[str]:
    """Return actionable release-audit findings below root."""
    findings: list[str] = []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if any(part in IGNORED_DIRECTORIES for part in relative.parts):
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            findings.append(f"bundled model/private artifact: {relative.as_posix()}")
            continue
        if path.suffix.lower() not in TEXT_SUFFIXES and path.name not in {"AGENTS.md", "NOTICE"}:
            continue
        try:
            file_content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append(f"non-UTF-8 text file: {relative.as_posix()}")
            continue
        if WINDOWS_ABSOLUTE_PATH.search(file_content):
            findings.append(f"absolute Windows path: {relative.as_posix()}")
    return findings


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    root = Path(args[0]).resolve() if args else Path.cwd().resolve()
    findings = scan_repository(root)
    if findings:
        print("Repository audit failed:")
        for finding in findings:
            print(f"- {finding}")
        return 1
    print("Repository audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
