# Architecture

The pipeline is input → preprocessing → WSD → lexicon lookup → scoring →
output. Preprocessor and SenseDisambiguator are protocols. Analyzer reuses
loaded resources. Lexicon loading and scoring do not depend on model libraries,
so lightweight CI needs no Torch or model download.

SimplePreprocessor tokenizes and normalizes Cyrillic/Latin lemmas.
OverlapSenseDisambiguator ranks definitions transparently.
DistilledSenseDisambiguator accepts a ranker; the production ranker uses local
Transformer embeddings. AnalysisResult retains evidence, score, label,
coverage, warnings, backend, and lexicon.
