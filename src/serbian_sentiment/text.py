from __future__ import annotations

_CYRILLIC_TO_LATIN = str.maketrans(
    {
        "а": "a",
        "б": "b",
        "в": "v",
        "г": "g",
        "д": "d",
        "ђ": "đ",
        "е": "e",
        "ж": "ž",
        "з": "z",
        "и": "i",
        "ј": "j",
        "к": "k",
        "л": "l",
        "м": "m",
        "н": "n",
        "о": "o",
        "п": "p",
        "р": "r",
        "с": "s",
        "т": "t",
        "ћ": "ć",
        "у": "u",
        "ф": "f",
        "х": "h",
        "ц": "c",
        "ч": "č",
        "џ": "dž",
        "ш": "š",
        "љ": "lj",
        "њ": "nj",
    }
)


def normalize_lemma(value: str) -> str:
    """Normalize Serbian Cyrillic or Latin lemma text to lowercase Latin."""

    return " ".join(value.strip().casefold().translate(_CYRILLIC_TO_LATIN).split())
