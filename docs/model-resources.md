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

The WSD rankers are public on the Tanor account:

| Experiment preset | Public model | Weight file | License |
|---|---|---:|---|
| `mling` | [Tanor/serbian-wsd-distilled-e5-large](https://huggingface.co/Tanor/serbian-wsd-distilled-e5-large) | 2239.61 MB | MIT |
| `simple` | [Tanor/serbian-wsd-distilled-minilm](https://huggingface.co/Tanor/serbian-wsd-distilled-minilm) | 90.86 MB | Apache-2.0 |
| `tesla` | [Tanor/serbian-wsd-distilled-teslaxlm](https://huggingface.co/Tanor/serbian-wsd-distilled-teslaxlm) | 2239.61 MB | CC BY-SA 4.0 |

For the default `mling` resource layout, explicitly download E5 Large with the Hugging Face CLI:

~~~bash
hf download Tanor/serbian-wsd-distilled-e5-large --revision 749f694999b256039011acfb8f0a4b1b4f388c8c --local-dir .local-resources/wsd/wsd-distilled-mling
~~~

The Hub name is `serbian-wsd-distilled-e5-large`; the local directory retains the experiment preset `mling`. This revision was checked on 2026-09-28. The download contains the tokenizer and saved configuration as well as the weights. The toolkit continues to load local files only.

The adapter reads `text_prefix` from `training_config.json`; `--text-prefix` explicitly overrides it. E5 requires `query: ` on both contexts and definitions, which the adapter applies automatically. It reads `max_seq_length` when present in `sentence_bert_config.json` and otherwise uses 512 tokens. The released E5 checkpoint uses 512 tokens.

For model-specific SentenceTransformer examples and the pinned revisions of MiniLM and TeslaXLM, see the [WSD model guide](https://github.com/sasa5linkar/serbian-wsd-distillation/blob/main/docs/huggingface_models.md) and their model cards. The published loading checks are separate from a full replication of the dissertation results.

The existing [Tanor preprocessing model](https://huggingface.co/Tanor/sr_pln_tesla_dbmu), ELEXIS inventory, and sentiment lexicons remain separate resources. Obtain them before running the full pipeline and retain their original licenses. The lightweight overlap example requires none of these downloads.

## Optional model selector

Use [examples/load_hf_wsd.py](../examples/load_hf_wsd.py) to choose `mling`, `simple`, or `tesla`, download it explicitly, or run a small standalone SentenceTransformer ranking example. [Commands and recommendations](../README.md#optional-hugging-face-example) keep this optional environment separate from the toolkit installation. The default E5 download directory matches the full pipeline layout above.
