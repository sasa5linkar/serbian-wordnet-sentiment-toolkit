# Sentiment lexicon format

CSV encoding is UTF-8 or UTF-8 with BOM. Required columns:

- ID: unique synset identifier.
- POS: positive score from 0 to 1.
- NEG: negative score from 0 to 1.

Optional columns are Lemme, Definicija, and Vrsta. Lemmes may be comma
separated. Identical duplicates are tolerated; conflicting duplicates fail.

    sr-sentiment lexicons validate --file path\table.csv

Named selection resolves NAME to resource-dir\NAME.csv.
