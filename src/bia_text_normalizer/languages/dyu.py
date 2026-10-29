"""Integer-only Dyula normalization using an explicit Jula vocabulary.

Cardinal decomposition is adapted from MALIBA-AI/bambara-text-normalization,
src/bambara_normalizer/numbers.py at 896140160616285d0a03d22e96622a581fb12c00.
Its MIT copyright and license notice is retained in
../_licenses/bambara-text-normalization.txt.

Vocabulary follows the Jula numerals reference at
https://lingweb.eva.mpg.de/channumerals/Jula.htm, selecting seegi for eight.
Zero (fu) and million (miliyɔn) are attested in the Dioula dictionaries linked
from the README. This initial profile does not rewrite existing Dyula words.
"""

from .._text import clean_letter_labels, expand_numbers, normalize_text

_UNITS = ("fu", "kelen", "fila", "saba", "naani", "looru", "wɔɔrɔ", "wolonfila", "seegi", "kɔnɔntɔn")
_TENS = (
    "",
    "tan",
    "mugan",
    "bisaba",
    "binaani",
    "bilooru",
    "biwɔɔrɔ",
    "biwolonfila",
    "biseegi",
    "bikɔnɔntɔn",
)


def number_to_dyula(n: int) -> str:
    """Verbalize an integer from 0 through 999,999,999 in the initial profile.

    Negatives and billions raise ValueError. Non-integers, including booleans,
    raise TypeError. Larger numbers are never silently read digit by digit.
    """
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("Expected an integer")
    if not 0 <= n < 1_000_000_000:
        raise ValueError("Dyula verbalization currently supports integers from 0 through 999,999,999")

    if n < 10:
        return _UNITS[n]
    if n < 100:
        tens, unit = divmod(n, 10)
        result = _TENS[tens]
        if unit:
            result += " ni " + _UNITS[unit]
        return result
    if n < 1_000:
        hundreds, remainder = divmod(n, 100)
        result = "kɛmɛ" if hundreds == 1 else "kɛmɛ " + _UNITS[hundreds]
    elif n < 1_000_000:
        thousands, remainder = divmod(n, 1_000)
        result = "waga " + number_to_dyula(thousands)
    else:
        millions, remainder = divmod(n, 1_000_000)
        result = "miliyɔn " + number_to_dyula(millions)
    if remainder:
        result += " ni " + number_to_dyula(remainder)
    return result


def numbers_to_words(text: str) -> str:
    """Expand supported integers, preserving unsupported numeric expressions."""
    return expand_numbers(text, number_to_dyula)


def normalize(text: str) -> str:
    """Expand Dyula integers, preserving surrounding spelling and punctuation."""
    return normalize_text(text, number_to_dyula)


def normalize_transcription_text(text: str) -> str:
    """Prepare labels while retaining case, tone marks, and word apostrophes."""
    return clean_letter_labels(normalize(text))
