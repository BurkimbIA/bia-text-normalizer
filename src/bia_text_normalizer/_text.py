"""Shared text handling for language-specific number verbalizers."""

import re
import unicodedata
from collections.abc import Callable

# Spaces used as thousands separators, e.g. "1 000 000" in French-style text.
_GROUP_SEPARATORS = "   "
_NUMERIC_SEPARATORS = ".,:/⁄–—-"
# Match numeric expressions as a whole so fractions, decimals, dates, and signed
# numbers pass through rather than having their components read as cardinals.
# Space-grouped thousands form one expression, so "1 000,5" also passes through.
_NUMBER_RE = re.compile(
    rf"(?<!\w)[+\-−]?(?:\d{{1,3}}(?:[{_GROUP_SEPARATORS}]\d{{3}})+|\d+)(?:[{_NUMERIC_SEPARATORS}]\d+)*"
    rf"(?!\w|[{_NUMERIC_SEPARATORS}]\d)"
)
_REMOVE_GROUP_SEPARATORS = str.maketrans("", "", _GROUP_SEPARATORS)
# Unify apostrophe variants so labels spell a word one way.
_LABEL_APOSTROPHES = str.maketrans({"’": "'", "ʼ": "'"})
# Apostrophes and hyphens are kept only inside words, as in go'o and pis-tã.
_BOUNDARY_JOINERS = re.compile(r"(?<!\w)['-]|['-](?!\w)")


def expand_numbers(text: str, verbalize: Callable[[int], str]) -> str:
    """Expand supported integers, preserving identifiers and unsupported forms."""

    def replace(match: re.Match[str]) -> str:
        token = match.group()
        digits = token.translate(_REMOVE_GROUP_SEPARATORS)
        if not digits.isdecimal() or (len(digits) > 1 and int(digits[0]) == 0):
            return token
        try:
            return verbalize(int(digits))
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


def strip_boundary_joiners(text: str) -> str:
    """Drop apostrophes and hyphens that do not join two word characters."""
    return normalize_transcription_spacing(_BOUNDARY_JOINERS.sub(" ", text))


def clean_letter_labels(text: str) -> str:
    """Keep Unicode letters, marks, and word-internal apostrophes and hyphens."""
    require_expanded_numbers(text)
    text = text.translate(_LABEL_APOSTROPHES)
    text = "".join(
        character if unicodedata.category(character)[0] in {"L", "M"} or character in "'-" else " "
        for character in text
    )
    return strip_boundary_joiners(text)
