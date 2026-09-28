# Serbian Sentiment WSD Toolkit

Explainable sentiment analysis for Serbian text using word-sense disambiguation
(WSD) and Serbian WordNet sentiment tables. The toolkit accepts direct text,
TXT, CSV, or TSV; normalizes Serbian Cyrillic and Latin lemmas; selects WordNet
senses; looks up POS and NEG values in a chosen CSV; and returns a score, label,
token-level evidence, and coverage.

## Research context

This software was developed as part of the doctoral dissertation:

> Саша З. Петалинкар, „Машинско учење и велики језички модели у развоју
> семантичких мрежа и њиховој примени на аутоматско разумевање текста”,
> Универзитет у Београду, 2026. Докторска дисертација је у поступку
> објављивања.

English title: “Machine Learning and Large Language Models in the Development
of Semantic Networks and Their Application in Automatic Text Understanding.”
The dissertation has been submitted and awaits publication; no DOI or permanent thesis
URL is claimed yet.

## Features

- Direct-text and batch CLI plus typed Python API.
- Explicit CSV selection by file or by name such as A7.
- Transparent definition-overlap WSD in the lightweight core.
- Optional local distilled Transformer WSD with no network fallback.
- Optional local Serbian POS and lemma analysis with a complete spaCy pipeline.
- Native ELEXIS `SrWSD-v2` XLSX loading.
- JSON, JSONL, CSV, and TSV output.
- Selected synsets, POS/NEG contributions, and coverage.
- Zero coverage is unscored, not neutral.
- Offline examples and explicit local resource configuration.

## Quick start

~~~bash
uv sync --extra dev
~~~

Analyze one sentence:

~~~powershell
uv run sr-sentiment analyze --text "Ово је одличан резултат." --lexicon-file examples/lexicon.csv --sense-repo examples/senses.csv --backend overlap --preprocessor simple
~~~

Select a named table from a resource directory:

~~~powershell
sr-sentiment analyze --input corpus.csv --text-column text --id-column id --lexicon A7 --resource-dir resources\lexicons --sense-repo resources\senses.csv --output results.csv --format csv
~~~

Optional local distilled WSD:

~~~powershell
.\.venv\Scripts\python -m pip install -e ".[wsd]"
sr-sentiment analyze --text "Ово је одличан резултат." --lexicon A7 --resource-dir resources\lexicons --sense-repo resources\senses.csv --backend distilled --model models\wsd-distilled
~~~

Full local pipeline (POS/lemma → WSD → sentiment):

~~~powershell
.\.venv\Scripts\python -m pip install -e ".[dev,full]"
sr-sentiment explain --text "Он је љубазан."
~~~

With the documented `.local-resources` layout, `auto` selects the local
spaCy model, distilled WSD model, ELEXIS workbook, and A7 table. Large and
third-party resources are deliberately ignored by Git.

The default symmetric decision threshold is `0.01`. It is the operational
value calibrated for the thesis configuration A7/S7 with WSD; use
`--threshold` to override it for another lexicon, domain, or scoring method.

## Optional Hugging Face example

[examples/load_hf_wsd.py](examples/load_hf_wsd.py) offers all three published rankers:

| Option | Model | When to choose it |
|---|---|---|
| `mling` (default) | [E5 Large](https://huggingface.co/Tanor/serbian-wsd-distilled-e5-large) | Starting choice: highest reported strict WSD accuracy of these three (72.6%). |
| `simple` | [MiniLM](https://huggingface.co/Tanor/serbian-wsd-distilled-minilm) | Smaller download: about 91 MB of weights; reported strict accuracy 68.5%. |
| `tesla` | [TeslaXLM](https://huggingface.co/Tanor/serbian-wsd-distilled-teslaxlm) | Comparison model; reported strict accuracy 51.3%, without improvement after distillation. |

These are the dissertation's reported results, not scores from this example. E5 and TeslaXLM each have about 2.24 GB of weights. The default only selects a model; it does not authorize a download.

List choices without installing model libraries:

~~~bash
python examples/load_hf_wsd.py --list
~~~

Run the small ranking example in a separate optional environment. This first call explicitly downloads MiniLM; replace `simple` with `mling` or `tesla` to choose another model:

~~~bash
uv run --no-project --with "sentence-transformers==5.5.0" --with "transformers==5.8.1" python examples/load_hf_wsd.py --model simple --download
~~~

Subsequent calls can omit `--download` to use the pinned cached copy. Use `--local-dir PATH` to read a complete existing checkpoint, or combine it with `--download` to download into that directory. Package installation by `uv` is separate from model download; `--no-project` keeps these example dependencies separate from the project's environment.

The example loads only local files after the explicit download, reads the saved `text_prefix` (including E5's `query: `), and lets SentenceTransformers load the saved pooling and tokenizer settings. It ranks two illustrative Serbian definitions and prints sense IDs with cosine scores. The sample is a usage demonstration, not an accuracy test or a full sentiment pipeline. A supplied local directory is used as-is; the pinned revision applies to Hub downloads and cached snapshots.

To obtain only the checkpoint for the existing application, without running the example:

~~~bash
uv run --no-project --with huggingface_hub python examples/load_hf_wsd.py --model mling --download --download-only --local-dir .local-resources/wsd/wsd-distilled-mling
~~~

The E5 directory above matches the toolkit's default resource layout. Use it with the existing `--backend distilled` option after obtaining the sense inventory and sentiment lexicon. The standalone example uses SentenceTransformers; it does not change the toolkit's optional dependency versions or its local adapter.

## Python API

~~~python
from pathlib import Path
from serbian_sentiment import Analyzer, AnalyzerConfig
from serbian_sentiment.lexicons import load_lexicon
from serbian_sentiment.preprocessing import SimplePreprocessor
from serbian_sentiment.wsd import OverlapSenseDisambiguator, load_sense_repository

lexicon = load_lexicon(Path("resources/lexicons/A7.csv"))
repository = load_sense_repository(Path("resources/senses.csv"))
analyzer = Analyzer(
    config=AnalyzerConfig(lexicon="A7"),
    preprocessor=SimplePreprocessor(),
    disambiguator=OverlapSenseDisambiguator(repository),
    lexicon=lexicon,
)
result = analyzer.analyze("Ово је одличан резултат.")
print(result.label, result.score, result.coverage)
~~~

## Interpretation and limitations

Every covered selected synset contributes POS minus NEG. The score is the mean
of covered units; a configurable symmetric threshold maps it to positive,
negative, or neutral. No covered units means unscored. Coverage must always be
considered with the label.

`auto` uses the local spaCy model when installed and otherwise falls back to
`SimplePreprocessor`. The simple preprocessor uses lowercase surface forms and
script normalization; it is not a full Serbian morphological analyzer. See
[limitations](docs/limitations.md).

## Resources, licensing, and documentation

No large model, thesis annotation, or third-party WordNet table is bundled
without verified redistribution rights. Code is Apache-2.0; original docs and
examples are CC BY 4.0. Third-party resources keep their own licenses.

Start with [installation](docs/installation.md), [workflow](docs/workflow.md),
[CLI reference](docs/cli-reference.md), [model resources](docs/model-resources.md),
[historical local smoke test](docs/local-smoke-test.md), and [lexicon format](docs/lexicon-format.md).

## WSD model configuration

The distilled adapter reads `text_prefix` from the model's `training_config.json`, including the trailing space in `query: ` for mling, and reads `max_seq_length` from `sentence_bert_config.json` when present (otherwise 512 tokens). It uses masked mean pooling and cosine similarity; unsupported SentenceTransformer layouts raise a resource error. Prefixes already present are not added twice. Override with CLI `--text-prefix` or the Python constructor's `text_prefix=` argument; an explicit empty string disables the saved prefix.

The WSD checkpoints are separate from the [24 sentiment classifiers](https://github.com/sasa5linkar/Serbian-WordNet-Sentiment-Lexicon-Analysis). [E5 Large (`mling`)](https://huggingface.co/Tanor/serbian-wsd-distilled-e5-large), [MiniLM (`simple`)](https://huggingface.co/Tanor/serbian-wsd-distilled-minilm), and [TeslaXLM (`tesla`)](https://huggingface.co/Tanor/serbian-wsd-distilled-teslaxlm) are now public. Follow [model resources](docs/model-resources.md#model-download-and-saved-settings) for an explicit, pinned E5 download into the default local directory. The lightweight example works without them.

This toolkit returns `unscored` at zero coverage. The separate [research evaluator](https://github.com/sasa5linkar/serbian-sentiment-wsd-evaluation) uses a neutral fallback; keep this distinction when comparing outputs.
