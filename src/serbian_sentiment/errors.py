class SerbianSentimentError(Exception):
    """Base exception for the toolkit."""


class ConfigurationError(SerbianSentimentError):
    """Raised when analyzer configuration is inconsistent."""


class ResourceError(SerbianSentimentError):
    """Raised when a required model or lexical resource is unavailable."""


class InputValidationError(SerbianSentimentError):
    """Raised when input text or tabular data is invalid."""


class LexiconValidationError(SerbianSentimentError):
    """Raised when a sentiment lexicon does not match the public schema."""


class ProcessingError(SerbianSentimentError):
    """Raised when preprocessing or WSD cannot complete."""
