# Installation

Python 3.10 or newer is required.

    python -m venv .venv
    .\.venv\Scripts\python -m pip install --upgrade pip
    .\.venv\Scripts\python -m pip install -e ".[dev]"

Optional local Transformer backend:

    .\.venv\Scripts\python -m pip install -e ".[wsd]"

Models and external resources are not downloaded automatically.

Complete local pipeline:

    .\.venv\Scripts\python -m pip install -e ".[dev,full]"
    .\.venv\Scripts\sr-sentiment.exe resources check-local
    .\.venv\Scripts\sr-sentiment.exe explain --text "Он је љубазан."

The `full` extra keeps POS/lemma preprocessing, ELEXIS XLSX loading, and
distilled WSD in the same virtual environment. Transformers is constrained to
the newest range compatible with `spacy-transformers` and the saved tokenizer.
