import pytest

from bia_text_normalizer import normalize, normalize_transcription_text
from bia_text_normalizer.languages.dyu import number_to_dyula, numbers_to_words


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        (0, "fu"),
        (1, "kelen"),
        (2, "fila"),
        (3, "saba"),
        (4, "naani"),
        (5, "looru"),
        (6, "wɔɔrɔ"),
        (7, "wolonfila"),
        (8, "seegi"),
        (9, "kɔnɔntɔn"),
        (10, "tan"),
        (11, "tan ni kelen"),
        (15, "tan ni looru"),
        (17, "tan ni wolonfila"),
        (20, "mugan"),
        (23, "mugan ni saba"),
        (30, "bisaba"),
        (50, "bilooru"),
        (70, "biwolonfila"),
        (80, "biseegi"),
        (90, "bikɔnɔntɔn"),
        (100, "kɛmɛ"),
        (101, "kɛmɛ ni kelen"),
        (123, "kɛmɛ ni mugan ni saba"),
        (200, "kɛmɛ fila"),
        (999, "kɛmɛ kɔnɔntɔn ni bikɔnɔntɔn ni kɔnɔntɔn"),
        (1_000, "waga kelen"),
        (1_234, "waga kelen ni kɛmɛ fila ni bisaba ni naani"),
        (20_000, "waga mugan"),
        (1_000_000, "miliyɔn kelen"),
        (2_000_123, "miliyɔn fila ni kɛmɛ ni mugan ni saba"),
        (
            999_999_999,
            "miliyɔn kɛmɛ kɔnɔntɔn ni bikɔnɔntɔn ni kɔnɔntɔn ni waga kɛmɛ kɔnɔntɔn "
            "ni bikɔnɔntɔn ni kɔnɔntɔn ni kɛmɛ kɔnɔntɔn ni bikɔnɔntɔn ni kɔnɔntɔn",
        ),
    ],
)
def test_cardinal_vocabulary_and_decomposition(number, expected):
    assert number_to_dyula(number) == expected


@pytest.mark.parametrize("number", [-1, 1_000_000_000])
def test_unsupported_values_are_rejected(number):
    with pytest.raises(ValueError):
        number_to_dyula(number)


@pytest.mark.parametrize("number", [True, 1.5, "3"])
def test_only_integers_are_accepted(number):
    with pytest.raises(TypeError):
        number_to_dyula(number)


@pytest.mark.parametrize(
    "text",
    ["007", "1.5", "1,000", "1/2", "12:30", "2026-10-29", "-3", "+3", "−3", "1000000000", "abc3", "3abc"],
)
def test_unsupported_numeric_forms_pass_through(text):
    assert numbers_to_words(text) == text


def test_public_api_normalizes_integers_without_rewriting_words():
    assert normalize("  B'a fɔ́! 5, 7, 23 .  ", lang="dyu") == "B'a fɔ́! looru, wolonfila, mugan ni saba."
    assert normalize("duuru wolonwula waa 1000", lang="dyu") == "duuru wolonwula waa waga kelen"


def test_unicode_and_zero_use_existing_text_handling():
    assert normalize("０ ２３ ½", lang="dyu") == "fu mugan ni saba 1⁄2"
    assert normalize("23, 007, 1000000000.", lang="dyu") == "mugan ni saba, 007, 1000000000."


def test_labels_preserve_tones_case_and_internal_apostrophes():
    assert normalize_transcription_text("‘B’a’ fɔ́! ƐƆ Ɲɲ Ŋŋ 5.", lang="dyu") == "B’a fɔ́ ƐƆ Ɲɲ Ŋŋ looru"
    assert normalize_transcription_text("0!", lang="dyu") == "fu"


@pytest.mark.parametrize("text", ["007", "1.5", "-3", "1000000000"])
def test_label_cleanup_cannot_drop_unsupported_numbers(text):
    with pytest.raises(ValueError, match="unsupported numbers"):
        normalize_transcription_text(text, lang="dyu")


def test_empty_text():
    assert normalize("", lang="dyu") == ""
    assert normalize_transcription_text("", lang="dyu") == ""
