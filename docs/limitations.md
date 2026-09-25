# Limitations

Results depend on preprocessing, candidate coverage, WSD, lexicon coverage,
domain, and threshold. The lightweight preprocessor is not a morphological
lemmatizer, so inflected forms may be uncovered. Definition overlap is a
transparent baseline, not a replacement for an evaluated WSD model.

The default threshold `0.01` was calibrated for the thesis A7/S7 + WSD
configuration. It is an operational default, not a universal constant; custom
lexicons, domains, and aggregation methods require separate calibration on
development data.

Lexical aggregates are not probabilities and do not fully model negation,
irony, discourse, or sentiment targets. Inspect coverage and evidence.
