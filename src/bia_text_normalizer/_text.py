"""Shared text handling for language-specific number verbalizers."""

import re
import unicodedata
from collections.abc import Callable

# Match numeric expressions as a whole so fractions, decimals, dates, and signed
# numbers pass through rather than having their components read as cardinals.
_NUMBER_RE = re.compile(r"(?<!\w)[+\-−]?\d+(?:[.,:/⁄–—-]\d+)*(?!\w)")
_BOUNDARY_APOSTROPHES = re.compile(r"(?<!\w)['’]|['’](?!\w)")


def expand_numbers(text: str, verbalize: Callable[[int], str]) -> str:
    """Expand supported integers, preserving identifiers and unsupported forms."""

    def replace(match: re.Match[str]) -> str:
        token = match.group()
        if not token.isdecimal() or (len(token) > 1 and int(token[0]) == 0):
            return token
        try:
            return verbalize(int(token))
        except ValueError:
            return token

    return _NUMBER_RE.sub(replace, text)


def normalize_transcription_spacing(text: str) -> str:
    """Normalize whitespace without changing the words."""
    text = re.sub(r"\s+", " ", text).strip()
    return re.sub(r"\s+([.,!?;:])", r"\1", text)


def normalize_text(text: str, verbalize: Callable[[int], str]) -> str:
    """Apply NFKC, expand supported integers, and normalize whitespace."""
    text = unicodedata.normalize("NFKC", text)
    return normalize_transcription_spacing(expand_numbers(text, verbalize))


def require_expanded_numbers(text: str) -> None:
    """Refuse label cleanup when numeric content would otherwise be erased."""
    if any(character.isdecimal() for character in text):
        raise ValueError("Label cleanup cannot remove unsupported numbers; use normalize() to preserve them")


def clean_letter_labels(text: str) -> str:
    """Keep Unicode letters, marks, and word apostrophes in normalized labels."""
    require_expanded_numbers(text)
    text = "".join(
        character if unicodedata.category(character)[0] in {"L", "M"} or character in "'’" else " "
        for character in text
    )
    return normalize_transcription_spacing(_BOUNDARY_APOSTROPHES.sub(" ", text))
