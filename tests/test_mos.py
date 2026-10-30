import pytest

from bia_text_normalizer._text import normalize_transcription_spacing
from bia_text_normalizer.languages.mos import (
    normalize,
    normalize_transcription_text,
    number_to_moore,
    numbers_to_words,
)


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        (1, "yembo"),
        (10, "piiga"),
        (15, "piig la a nu"),
        (23, "pisi la a tã"),
        (100, "koabga"),
        (156, "koabga la pis-nu la a yoobe"),
        (200, "kobs-yi"),
        (1_000, "tusri"),
        (2_500, "tusa yi la kobs-nu"),
        (10_000, "tus-piiga"),
        (15_000, "tus-piig la nu"),
        (23_000, "tus-pisi la tãabo"),
        (99_999, "tus-pis-wae la wae la kobs-wae la pis-wae la a wae"),
        (1_000_000, "milyõ ye"),
        (2_000_003, "milyõ yiibu tãabo"),
    ],
)
def test_supplied_number_forms(number, expected):
    assert number_to_moore(number) == expected


@pytest.mark.parametrize("number", [0, -1, 100_000, 123_000, 999_999, 1_100_000])
def test_unsupported_values_raise_instead_of_dropping_or_crashing(number):
    with pytest.raises(ValueError):
        number_to_moore(number)


@pytest.mark.parametrize("number", [True, 1.5, "3"])
def test_non_integer_inputs_are_rejected(number):
    with pytest.raises(TypeError):
        number_to_moore(number)


@pytest.mark.parametrize(
    "text",
    [
        "0",
        "100000",
        "123000",
        "1100000",
        "007",
        "12.5",
        "1,000",
        "1/2",
        "12:30",
        "2026-10-28",
        "-3",
        "+3",
        "−3",
        "abc3",
        "3abc",
    ],
)
def test_unsupported_numeric_forms_pass_through(text):
    assert numbers_to_words(text) == text


def test_preserving_unknown_number_does_not_prevent_other_conversions():
    assert normalize("3, 0, 123000, 20.") == "tãabo, 0, 123000, pisi."


def test_nfkc_precedes_number_expansion_and_preserves_moore_spelling():
    assert normalize("  ﬁ １２ : A\u0303 Ɛ Ɩ Ʋ Œ  ") == "fi piig la a yi: Ã Ɛ Ɩ Ʋ Œ"


def test_unicode_fraction_is_not_expanded_into_two_cardinals():
    assert normalize("½") == "1⁄2"


def test_label_cleanup_is_explicit_and_keeps_case():
    assert normalize("“Mam” (Ɛ) + 3!") == "“Mam” (Ɛ) + tãabo!"
    assert normalize_transcription_text("“Mam” (Ɛ) + 3!") == "Mam Ɛ tãabo"


@pytest.mark.parametrize("text", ["0", "123000", "007", "3.14", "-3"])
def test_label_cleanup_cannot_silently_delete_unsupported_numbers(text):
    with pytest.raises(ValueError, match="unsupported numbers"):
        normalize_transcription_text(text)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1 000", "tusri"),
        ("2 500 FCFA", "tusa yi la kobs-nu FCFA"),
        ("1\u00a0000\u202f003", "milyõ ye tãabo"),
        ("1 000 000", "milyõ ye"),
    ],
)
def test_space_grouped_thousands_are_one_number(text, expected):
    assert normalize(text) == expected


@pytest.mark.parametrize("text", ["1 000,5", "1 000.5", "007 000", "-1 000"])
def test_unsupported_space_grouped_forms_pass_through(text):
    assert numbers_to_words(text) == text


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("12 34", "piig la a yi pis-tã la a naase"),
        ("10 2000", "piiga tusa yi"),
        ("1 00", "yembo 00"),
        # Separate numbers that look like a thousands group are read as one.
        ("20 300", "tus-pisi la kobs-tã"),
    ],
)
def test_irregular_groups_are_separate_numbers(text, expected):
    assert numbers_to_words(text) == expected


def test_labels_keep_word_internal_hyphens():
    assert normalize_transcription_text("20, 30, 200, 10000") == "pisi pis-tã kobs-yi tus-piiga"
    assert normalize_transcription_text("Kãab-noodo - la -saglse-.") == "Kãab-noodo la saglse"


def test_spacing_and_empty_text():
    assert normalize_transcription_spacing("  Kãab-noodo   la\nsaglse   .  ") == "Kãab-noodo la saglse."
    assert normalize("") == ""
    assert normalize_transcription_text("") == ""
