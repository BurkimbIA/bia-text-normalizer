# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

### Added

- Mooré integer text normalization, explicit transcription label cleanup, and a command-line interface.
- Preserve unsupported numeric forms during TN and reject label cleanup that would erase them.
- Fulfulde (`fuh`) cardinal normalization and CLI support based on all 52 supplied CSV examples, with word apostrophes retained in labels.
- Dyula (`dyu`) integer normalization and CLI support with Jula vocabulary, adapting MALIBA-AI's cardinal decomposition with its MIT notice retained in the package.

### Changed

- Configured `bia-text-normalizer` and documented its project scope.
- Use Python 3.12 for development and CI, and support Python 3.12 or later.
- Focus the project on text normalization for Mooré, Dyula, and Fulfulde.

### Security

- Bumped the `uv-pre-commit` hook to uv 0.13.4. Earlier versions ship the compromised emSign ECC Root CA - G3 root, which certifi 2026.10.19 and uv 0.13.4 remove.
