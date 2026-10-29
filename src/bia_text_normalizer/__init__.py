"""Text normalization for speech applications."""

import argparse

from .languages import dyu, fuh, mos

__all__ = ["normalize", "normalize_transcription_text"]

_LANGUAGES = {"mos": mos, "dyu": dyu, "fuh": fuh}


def _language(lang: str):
    if lang not in _LANGUAGES:
        raise NotImplementedError(
            f"Text normalization is not implemented for {lang!r}; available languages: {', '.join(_LANGUAGES)}"
        )
    return _LANGUAGES[lang]


def normalize(text: str, lang: str = "mos") -> str:
    """Expand supported integers while preserving spelling, case, and punctuation."""
    return _language(lang).normalize(text)


def normalize_transcription_text(text: str, lang: str = "mos") -> str:
    """Expand integers and apply the language's explicit, lossy label cleanup."""
    return _language(lang).normalize_transcription_text(text)


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize text for speech applications.")
    parser.add_argument("text", help="Text to normalize")
    parser.add_argument("--lang", choices=list(_LANGUAGES), default="mos")
    parser.add_argument(
        "--labels", action="store_true", help="Apply the selected language's transcription label cleanup"
    )
    args = parser.parse_args()
    normalizer = normalize_transcription_text if args.labels else normalize
    try:
        result = normalizer(args.text, lang=args.lang)
    except ValueError as exc:
        parser.error(str(exc))
    print(result)
