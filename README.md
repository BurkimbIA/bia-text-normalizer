# bia-text-normalizer

Text normalization (TN) for Mooré, Dyula, and Fulfulde.

The Python distribution is named `bia-text-normalizer`, with the import name
`bia_text_normalizer`.

## Status

Early development. Mooré (`mos`), Dyula (`dyu`), and Fulfulde (`fuh`) text
normalization expand supported integers using language-specific vocabulary and
rules. Supported number ranges differ by language.

## Initial languages

- `mos`: Mooré (implemented)
- `dyu`: Dyula (implemented)
- `fuh`: Western Niger Fulfulde (implemented)

## Scope

- **Text normalization:** convert written forms into spoken forms for TTS,
  such as `23` → `pisi la a tã` in Mooré.
- **Evaluation normalization:** provide configurable cleanup for comparing
  reference transcripts with ASR predictions.

The approach starts with small Python modules and language-specific rules.
Composable parsers and vocabulary files can be added as the grammar grows.
Evaluation cleanup is separate from TN so that changes to case,
punctuation, and diacritics are explicit choices.

## Mooré usage

Install from this checkout with `uv sync`, then run Python with `uv run python`:

```python
from bia_text_normalizer import normalize, normalize_transcription_text
from bia_text_normalizer.languages.mos import number_to_moore

number_to_moore(2500)
# 'tusa yi la kobs-nu'

normalize("Mam zoe 3 ruki la a 20 yʋʋmd .", lang="mos")
# 'Mam zoe tãabo ruki la a pisi yʋʋmd.'

normalize_transcription_text("Mam zoe 3 ruki la a 20 yʋʋmd .", lang="mos")
# 'Mam zoe tãabo ruki la a pisi yʋʋmd'
```

`normalize` applies Unicode NFKC normalization, expands supported integers, and
normalizes spacing. It preserves letter case, spelling, and punctuation.
`normalize_transcription_text` additionally removes punctuation and characters
outside the supplied Mooré label alphabet. Use this lossy cleanup only when
preparing labels that require that alphabet.

The command line supports the same two modes:

```bash
uv run bia-text-normalizer --lang mos "Mam zoe 3 ruki."
uv run bia-text-normalizer --lang mos --labels "Mam zoe 3 ruki."
```

### Current limits

- The supplied word forms cover integers from 1 through 99,999, plus millions
  whose multiplier and remainder can also be expressed by these rules.
- Zero and thousand multipliers from 100 through 999 still need confirmed spoken
  forms. `normalize` leaves unsupported numbers unchanged; `number_to_moore`
  raises `ValueError` for unsupported values.
- Leading-zero sequences and contiguous numeric expressions containing signs,
  decimal separators, grouping separators, fraction bars, date separators, or
  time separators pass through unchanged. Dates, times, money, measurements, and
  telephone numbers do not yet have dedicated normalization rules.
- Label cleanup raises `ValueError` if digits remain after expansion, preventing
  unsupported numbers from silently disappearing.
- Language codes other than `mos`, `dyu`, and `fuh` raise `NotImplementedError`.

## Fulfulde usage

Fulfulde rules are based on 52 supplied examples, retained as a
[regression test fixture](tests/data/fuh_numbers.csv).

```python
from bia_text_normalizer import normalize, normalize_transcription_text
from bia_text_normalizer.languages.fuh import number_to_fulfulde

number_to_fulfulde(1789)
# "ujunere e keme je'di e cappanɗe jeetati e jeenayi"

normalize("22, 10000.", lang="fuh")
# 'noogay e ɗiɗi, ujunaaji sapo.'

normalize_transcription_text("1, 7, 22!", lang="fuh")
# "go'o je'di noogay e ɗiɗi"
```

```bash
uv run bia-text-normalizer --lang fuh "22, 10000."
uv run bia-text-normalizer --lang fuh --labels "1, 7, 22!"
```

Generated number words are lowercase. The surrounding text keeps its case.
The CSV's variants are retained: `didi` and `ɗiɗi` (in 22), `nay` and `nayi`,
`jeenay` and `jeenayi`, and `sappo` and `sapo` (as a thousands multiplier).
No spelling corrections have been inferred.

### Current limits

- All 52 CSV examples match after lowercasing and trimming incidental whitespace.
  The examples extend through 10,000; compositional tens, hundreds, and thousands
  rules are extrapolated to integers from 1 through 999,999. Forms absent from the
  CSV still need speaker review.
- Zero and millions need source forms. TN preserves them; direct verbalization
  and label cleanup raise `ValueError`.
- Numeric-expression handling follows the same rules as Mooré: leading zeros,
  signed values, decimals, dates, and similar forms pass through unchanged.
- Fulfulde label cleanup preserves Unicode letters and combining marks, plus
  internal apostrophes in words such as `go'o` and `je'di`. It removes other
  punctuation. A restricted Fulfulde label alphabet has not been specified.

## Dyula usage

```python
from bia_text_normalizer import normalize, normalize_transcription_text
from bia_text_normalizer.languages.dyu import number_to_dyula

number_to_dyula(1234)
# 'waga kelen ni kɛmɛ fila ni bisaba ni naani'

normalize("5, 7, 23, 1000.", lang="dyu")
# 'looru, wolonfila, mugan ni saba, waga kelen.'

normalize_transcription_text("0, 23!", lang="dyu")
# 'fu mugan ni saba'
```

```bash
uv run bia-text-normalizer --lang dyu "5, 7, 23, 1000."
uv run bia-text-normalizer --lang dyu --labels "0, 23!"
```

The initial vocabulary follows the [Jula numerals reference](https://lingweb.eva.mpg.de/channumerals/Jula.htm),
selecting `looru`, `wolonfila`, `seegi`, `kɔnɔntɔn`, and `waga`. Tens from 30
through 90 are written together, such as `bisaba` and `bilooru`. Zero (`fu`) is
attested in the [Dioula lexicon](https://dev.coastsystems.net/fr/docs/lexique-dyu/),
and million (`miliyɔn`) in the [Dioula dictionary index](https://coastsystems.net/fr/docs/index-list/).
These are explicit initial spelling choices, not a claim that other variants
are incorrect. Speaker review against the target corpus is still needed.

The cardinal decomposition is adapted from
[MALIBA-AI/bambara-text-normalization](https://github.com/MALIBA-AI/bambara-text-normalization/blob/896140160616285d0a03d22e96622a581fb12c00/src/bambara_normalizer/numbers.py).
Its [MIT copyright and license notice](src/bia_text_normalizer/_licenses/bambara-text-normalization.txt)
is included in the package. No upstream runtime dependency is added.

### Current limits

- Supports integers from 0 through 999,999,999. Direct verbalization rejects
  negative values and billions with `ValueError`; TN leaves them unchanged.
- Leading zeros, signed values, decimals, dates, times, and fractions follow the
  existing text handling and pass through unchanged. No money, measurement,
  contraction, or spelling-rewriting rules are enabled.
- Generated words are lowercase; surrounding text retains its spelling, case,
  and tone marks. Label cleanup retains Unicode letters, combining marks, and
  internal apostrophes, and rejects numbers it would otherwise erase.

## Development

Requires Python 3.12 or later and [uv](https://github.com/astral-sh/uv).

```bash
git clone https://github.com/BurkimbIA/bia-text-normalizer.git
cd bia-text-normalizer
uv sync --all-groups
```

Run the checks with:

```bash
uv run ruff format --check .
uv run ruff check .
uv run pytest
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Language contributions should include
reviewed examples of written and spoken forms, accepted spelling variants, and
sentences that should remain unchanged.
