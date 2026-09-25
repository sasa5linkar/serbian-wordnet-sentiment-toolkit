# Python API

Construct Analyzer with AnalyzerConfig, a Preprocessor, a SenseDisambiguator,
and a validated Lexicon. analyze returns AnalysisResult; analyze_many preserves
input order. Public dataclasses support to_dict.

Adapters are explicit dependencies, so users can replace preprocessing or WSD
without monkey-patching the core.

The Python configuration uses the calibrated A7/S7 + WSD threshold by default,
and accepts an explicit value for another evaluated setup:

~~~python
from serbian_sentiment.config import AnalyzerConfig

default_config = AnalyzerConfig(lexicon="A7")  # threshold=0.01
custom_config = AnalyzerConfig(lexicon="A7", threshold=0.05)
~~~
