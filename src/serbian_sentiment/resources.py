from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class LocalResources:
    root: Path
    preprocessing_model: Path
    wsd_model: Path
    sense_repository: Path
    lexicon_directory: Path

    @classmethod
    def from_root(cls, root: str | Path) -> LocalResources:
        resolved = Path(root)
        return cls(
            root=resolved,
            preprocessing_model=resolved / "preprocessing" / "sr_pln_tesla_dbmu",
            wsd_model=resolved / "wsd" / "wsd-distilled-mling",
            sense_repository=resolved / "elexis" / "Elexis-WSD-Repo.xlsx",
            lexicon_directory=resolved / "lexicons",
        )

    def lexicon(self, name: str) -> Path:
        return self.lexicon_directory / f"{name}.csv"

    def availability(self) -> dict[str, bool]:
        return {
            "preprocessing_model": self.preprocessing_model.is_dir(),
            "wsd_model": self.wsd_model.is_dir(),
            "sense_repository": self.sense_repository.is_file(),
            **{
                f"lexicon_{name}": self.lexicon(name).is_file()
                for name in ("S0", "A1", "A2", "A3", "A4", "A5", "A6", "A7")
            },
        }
