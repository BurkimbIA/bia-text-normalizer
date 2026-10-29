import csv
from pathlib import Path

import pytest

from bia_text_normalizer import normalize, normalize_transcription_text
from bia_text_normalizer.languages.fuh import number_to_fulfulde, numbers_to_words


def _source_examples():
    # Unedited snapshot of Chiffres fulfulde - Feuille 1.csv. Only incidental
    # capitalization and the leading space in Hemre are normalized for output.
    path = Path(__file__).parent / "data" / "fuh_numbers.csv"
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [
            (int(row["Nombre (Chiffre)"]), row["Fulfulde"].strip().lower()) for row in csv.DictReader(handle)
        ]


@pytest.mark.parametrize(("number", "expected"), _source_examples())
def test_csv_number_forms(number, expected):
    assert number_to_fulfulde(number) == expected


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        (24, "noogay e nay"),
        (42, "cappanɗe nayi e didi"),
        (110, "hemre e sappo"),
        (122, "hemre e noogay e ɗiɗi"),
        (2_500, "ujunaaji didi e keme joy"),
        (10_001, "ujunaaji sapo e go'o"),
        (123_456, "ujunaaji hemre e noogay e tati e keme nayi e cappanɗe joy e jeego"),
        (
            999_999,
            "ujunaaji keme jeenayi e cappanɗe jeenayi e jeenayi e keme jeenayi e cappanɗe jeenayi e jeenayi",
        ),
    ],
)
def test_compositional_patterns(number, expected):
    assert number_to_fulfulde(number) == expected


@pytest.mark.parametrize("number", [0, -1, 1_000_000])
def test_values_without_source_rules_are_rejected(number):
    with pytest.raises(ValueError):
        number_to_fulfulde(number)


@pytest.mark.parametrize("number", [True, 1.5, "3"])
def test_non_integer_inputs_are_rejected(number):
    with pytest.raises(TypeError):
        number_to_fulfulde(number)


@pytest.mark.parametrize(
    "text",
    ["0", "1000000", "007", "12.5", "1,000", "1/2", "12:30", "2026-10-29", "-3", "+3", "−3", "abc3", "3abc"],
)
def test_unsupported_numeric_forms_pass_through(text):
    assert numbers_to_words(text) == text


def test_public_api_expands_numbers_and_preserves_surrounding_text():
    assert normalize("  Ɓe: 22, 1789 .  ", lang="fuh") == (
        "Ɓe: noogay e ɗiɗi, ujunere e keme je'di e cappanɗe jeetati e jeenayi."
    )
    assert normalize("3, 0, 1000000.", lang="fuh") == "tati, 0, 1000000."


def test_unicode_normalization_does_not_split_fractions():
    assert normalize("２２ ½", lang="fuh") == "noogay e ɗiɗi 1⁄2"


def test_label_cleanup_preserves_word_apostrophes_and_fulfulde_letters():
    assert normalize_transcription_text("“Ɓe” 1, 7, 22!", lang="fuh") == "Ɓe go'o je'di noogay e ɗiɗi"
    assert normalize_transcription_text("'Go'o' ‘Je’di’ Ɗɗ Ƴƴ Ŋŋ Ññ!", lang="fuh") == "Go'o Je’di Ɗɗ Ƴƴ Ŋŋ Ññ"


@pytest.mark.parametrize("text", ["0", "1000000", "007", "3.14", "-3"])
def test_label_cleanup_cannot_delete_unsupported_numbers(text):
    with pytest.raises(ValueError, match="unsupported numbers"):
        normalize_transcription_text(text, lang="fuh")


def test_empty_text():
    assert normalize("", lang="fuh") == ""
    assert normalize_transcription_text("", lang="fuh") == ""
