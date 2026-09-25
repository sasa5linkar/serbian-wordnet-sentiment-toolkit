# Models and resources

The repository ships only synthetic fixtures. Real runs use this ignored local
layout by default:

    .local-resources/
      preprocessing/sr_pln_tesla_dbmu/
      wsd/wsd-distilled-mling/
      elexis/Elexis-WSD-Repo.xlsx
      lexicons/S0.csv
      lexicons/A1.csv ... A7.csv
      manifest.json

The selected POS/lemma model is `Tanor/sr_pln_tesla_dbmu`; it contains a
transformer, tagger, trainable lemmatizer, and NER component. ELEXIS senses are
read from the `SrWSD-v2` sheet. The default sentiment table is A7.

The overlap backend needs no model. The distilled backend uses
`local_files_only` and never downloads silently. Users obtain resources under
their original licenses. Do not commit a resource until redistribution and
provenance are documented.

The local manifest records provenance, license notes, sizes, and checksums.
`.local-resources/` is excluded both by `.gitignore` and the release audit.

## Model download and saved settings

The WSD weights are not yet released. See the [WSD publication guide](https://github.com/sasa5linkar/serbian-wsd-distillation/blob/main/docs/huggingface_models.md) for release status and the pinned-revision download procedure. Once published, download mling into `.local-resources/wsd/wsd-distilled-mling/`. The adapter reads `training_config.json` and `sentence_bert_config.json`; `--text-prefix` explicitly overrides the saved prefix. The existing [Tanor preprocessing model](https://huggingface.co/Tanor/sr_pln_tesla_dbmu) is a separate dependency and retains its own license.
