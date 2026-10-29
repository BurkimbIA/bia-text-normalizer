import subprocess
import sys
from importlib.metadata import version
from pathlib import Path

import pytest

from bia_text_normalizer import normalize, normalize_transcription_text


def test_version():
    assert version("bia-text-normalizer") == "0.1.0"


def test_public_normalizers():
    text = "Mam zoe 3 ruki la a 20 yʋʋmd ."
    assert normalize(text, lang="mos") == "Mam zoe tãabo ruki la a pisi yʋʋmd."
    assert normalize_transcription_text(text, lang="mos") == "Mam zoe tãabo ruki la a pisi yʋʋmd"


def test_unknown_language_is_explicit():
    with pytest.raises(NotImplementedError, match="zzz"):
        normalize("3", lang="zzz")


@pytest.mark.parametrize("labels", [False, True])
@pytest.mark.parametrize(("lang", "expected"), [("mos", "tãabo"), ("dyu", "saba"), ("fuh", "tati")])
def test_installed_cli(labels, lang, expected):
    command = [str(Path(sys.executable).with_name("bia-text-normalizer")), "--lang", lang, "3."]
    if labels:
        command.append("--labels")
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    assert result.stdout.strip() == (expected if labels else expected + ".")


def test_cli_reports_unsupported_labels_without_a_traceback():
    command = [str(Path(sys.executable).with_name("bia-text-normalizer")), "--labels", "0"]
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 2
    assert "unsupported numbers" in result.stderr
    assert "Traceback" not in result.stderr
