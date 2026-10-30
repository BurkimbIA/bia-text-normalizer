"""Fulfulde cardinal rules derived from Chiffres fulfulde - Feuille 1.csv.

The 52 source examples cover 1 through 10,000. Their compositional patterns are
extended to positive integers below one million. Generated words are lowercase.
Two is always ɗiɗi and ten is always sappo; the source's didi and its sapo in
10,000 were corrected to these spellings.
"""

from .._text import (
    clean_letter_labels,
    expand_numbers,
    normalize_text,
)

_UNITS = ("", "go'o", "ɗiɗi", "tati", "nay", "joy", "jeego", "je'di", "jeetati", "jeenay")
# The source uses nayi and jeenayi as multipliers, and jeenayi as a remainder.
_MULTIPLIERS = {4: "nayi", 9: "jeenayi"}
_REMAINDERS = {9: "jeenayi"}


def _multiplier(n: int) -> str:
    if n in _MULTIPLIERS:
        return _MULTIPLIERS[n]
    return number_to_fulfulde(n)


def number_to_fulfulde(n: int) -> str:
    """Verbalize a cardinal from 1 through 999,999 using the CSV's patterns.

    Zero, negatives, and millions need additional source forms and raise
    ValueError. Non-integers, including booleans, raise TypeError.
    """
    if not isinstance(n, int) or isinstance(n, bool):
        raise TypeError("Expected an integer")
    if not 1 <= n < 1_000_000:
        raise ValueError("Fulfulde verbalization currently supports integers from 1 through 999,999")

    if n < 10:
        return _UNITS[n]
    if n < 100:
        tens, unit = divmod(n, 10)
        if tens == 1:
            result = "sappo"
        elif tens == 2:
            result = "noogay"
        else:
            result = "cappanɗe " + _multiplier(tens)
        if unit:
            result += " e " + _REMAINDERS.get(unit, _UNITS[unit])
        return result
    if n < 1_000:
        hundreds, remainder = divmod(n, 100)
        result = "hemre" if hundreds == 1 else "keme " + _multiplier(hundreds)
    else:
        thousands, remainder = divmod(n, 1_000)
        result = "ujunere" if thousands == 1 else "ujunaaji " + _multiplier(thousands)
    if remainder:
        result += " e " + number_to_fulfulde(remainder)
    return result


def numbers_to_words(text: str) -> str:
    """Expand supported integers, leaving unsupported numeric forms unchanged."""
    return expand_numbers(text, number_to_fulfulde)


def normalize(text: str) -> str:
    """Expand Fulfulde integers, preserving surrounding case and punctuation."""
    return normalize_text(text, number_to_fulfulde)


def normalize_transcription_text(text: str) -> str:
    """Prepare labels, retaining Unicode letters, marks, and word apostrophes.

    Apostrophes in forms such as go'o and je'di are part of the word. Other
    punctuation is removed. No unconfirmed Fulfulde alphabet filter is imposed.
    """
    return clean_letter_labels(normalize(text))
