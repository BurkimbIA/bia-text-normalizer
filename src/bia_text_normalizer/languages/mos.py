"""Mooré integer verbalization and optional transcription label cleanup.

Word forms follow the supplied BurkimbIA rules. Zero and thousand multipliers
from 100 to 999 have no confirmed spoken form in these rules.
"""

import re

from .._text import (
    expand_numbers,
    normalize_text,
    require_expanded_numbers,
    strip_boundary_joiners,
)

_FINAL_LABEL_DISALLOWED_RE = re.compile(r"[^A-Za-zÃÕĨŨẼãõĩũẽƐɛƖɩƲʋŒœ\s-]")

_UNITS = ["", "yembo", "yiibu", "tãabo", "naase", "nu", "yoobe", "yopoe", "nii", "wae"]
_TENS = ["", "piiga", "pisi", "pis-tã", "pis-naase", "pis-nu", "pis-yoobe", "pis-yopoe", "pis-nii", "pis-wae"]
_HUNDREDS_PREFIX = "kobs-"

# Shortened vowel forms used when a unit word follows a connector.
_SHORT = {"yembo": "ye", "yiibu": "yi", "tãabo": "tã"}


def _short(unit_word: str) -> str:
    return _SHORT.get(unit_word, unit_word)


def _thousands_word(n: int) -> str:
    """Return the supplied thousands form for multipliers from 2 through 99."""
    if n >= 100:
        raise ValueError("Mooré thousand multipliers from 100 to 999 need confirmed word forms")
    if n < 10:
        return "tusa " + _short(_UNITS[n])
    if n == 10:
        return "tus-piiga"
    if n <= 19:
        return "tus-piig la " + _UNITS[n - 10]
    tens_part = _TENS[n // 10]
    unit = n % 10
    if unit:
        return "tus-" + tens_part + " la " + _UNITS[unit]
    return "tus-" + tens_part


def number_to_moore(n: int) -> str:
    """Verbalize a supported positive integer using the supplied Mooré rules.

    Raise ValueError for zero, negatives, and unsupported thousand multipliers.
    Raise TypeError for non-integers, including booleans.
    """
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("Expected an integer")
    if n <= 0:
        raise ValueError("Mooré verbalization currently supports positive integers only")

    if n < 10:
        return _UNITS[n]
    if n == 10:
        return _TENS[1]
    if n <= 19:
        return "piig la a " + _short(_UNITS[n - 10])
    if n < 100:
        tens_part = _TENS[n // 10]
        remainder = n % 10
        if remainder:
            return tens_part + " la a " + _short(_UNITS[remainder])
        return tens_part
    if n < 1_000:
        hundreds_count = n // 100
        remainder = n % 100
        result = "koabga" if hundreds_count == 1 else _HUNDREDS_PREFIX + _short(_UNITS[hundreds_count])
        if remainder:
            result += " la " + number_to_moore(remainder)
        return result
    if n < 1_000_000:
        thousands_count = n // 1_000
        remainder = n % 1_000
        result = "tusri" if thousands_count == 1 else _thousands_word(thousands_count)
        if remainder:
            result += " la " + number_to_moore(remainder)
        return result

    millions_count = n // 1_000_000
    remainder = n % 1_000_000
    result = "milyõ ye" if millions_count == 1 else "milyõ " + number_to_moore(millions_count)
    if remainder:
        result += " " + number_to_moore(remainder)
    return result


def numbers_to_words(text: str) -> str:
    """Expand supported integer expressions; preserve unsupported numeric forms.

    Leading-zero sequences are left unchanged because they may be identifiers.
    """

    return expand_numbers(text, number_to_moore)


def normalize(text: str) -> str:
    """Apply NFKC, expand supported integers, and normalize whitespace."""
    return normalize_text(text, number_to_moore)


def normalize_transcription_text(text: str) -> str:
    """Normalize labels with the supplied alphabet, preserving letter case.

    This removes punctuation and letters outside the label alphabet, keeping
    hyphens inside words such as pis-tã. Refuse residual numbers so cleanup
    cannot silently erase unsupported numeric forms.
    """
    text = normalize(text)
    require_expanded_numbers(text)
    text = _FINAL_LABEL_DISALLOWED_RE.sub(" ", text)
    return strip_boundary_joiners(text)
