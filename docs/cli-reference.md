# CLI reference

- `sr-sentiment analyze`: direct text or TXT/CSV/TSV.
- `sr-sentiment explain`: detailed JSON for one text.
- `sr-sentiment lexicons list`: list CSVs in a resource directory.
- `sr-sentiment lexicons validate`: validate schema and scores.
- `sr-sentiment resources check-local`: verify the local resource layout.
- `sr-sentiment --version`: package version.

Analyze accepts exactly one of `--lexicon-file` and `--lexicon`. Named selection
also uses `--resource-dir`. Backends are `auto`, `overlap`, and `distilled`.
Preprocessors are `auto`, `simple`, and `spacy`. `--resource-root` defaults to
`.local-resources`; local defaults are ELEXIS `SrWSD-v2`, A7, the Tesla spaCy
pipeline, and the distilled WSD model. Explicit path options override any
default. Formats are JSON, JSONL, CSV, and TSV.

`--threshold` is symmetric around zero and defaults to `0.01`, the calibrated
operational value for A7/S7 with WSD. A custom lexicon, domain, or aggregation
method should be calibrated separately and passed an explicit threshold.

Exit codes: 0 success, 2 configuration, 3 resource, 4 input, 5 processing.

For `analyze` and `explain`, `--text-prefix` overrides the saved distilled-model prefix. Omit it to read `training_config.json`; use an empty string to disable the prefix.
