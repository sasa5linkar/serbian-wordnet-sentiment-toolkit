# Local full-pipeline smoke test

The production-like local verification uses raw Serbian text and all four
resource layers:

1. `Tanor/sr_pln_tesla_dbmu` supplies tokens, POS tags, and lemmas.
2. ELEXIS `SrWSD-v2` supplies candidate senses.
3. `wsd-distilled-mling` ranks the candidates.
4. A7 supplies POS and NEG sentiment values.

Run:

    .\.venv\Scripts\sr-sentiment.exe explain --text "Он је љубазан." --backend distilled --preprocessor spacy

Verified on 2026-07-28:

- token: `љубазан`
- lemma/POS: `љубазан` / `ADJ`
- selected sense: `ENG30-01372049-a`
- A7 POS: `0.7469015886512871`
- A7 NEG: `0.008102135869609839`
- net score: `0.738799452782`
- label: `positive`
- backend: `distilled-transformer`
- decision threshold: `0.01` (the A7/S7 + WSD operational default)

The output also preserves uncovered tokens and reports coverage (`1/4`) rather
than silently treating missing senses as neutral. This file records expected
behavior, not the models themselves; all production resources remain local and
Git-ignored.
