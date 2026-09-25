# End-to-end workflow

1. Read direct text, TXT, CSV, or TSV into DocumentInput.
2. If available, apply the local Serbian spaCy model for tokenization, POS, and
   trainable lemmatization; otherwise use the explicit simple fallback.
3. Find candidate senses by normalized lemma.
4. Rank candidates by definition overlap or a local distilled model.
5. Look up the selected synset in the chosen sentiment CSV.
6. Calculate POS minus NEG for covered units.
7. Average covered values and classify with the threshold.
8. Emit output with selected synsets, provenance, and coverage.

No-candidate and no-lexicon-row cases remain visible as uncovered units.

`auto` resolves the default local resource layout and chooses distilled WSD
when the model directory exists. Explicit `spacy` or `distilled` selection
fails clearly when its resource is unavailable; it never downloads silently.
