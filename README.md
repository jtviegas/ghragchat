# tgedr-ghragchat

![Coverage](./coverage.svg)
[![PyPI](https://img.shields.io/pypi/v/tgedr-ghragchat)](https://pypi.org/project/tgedr-ghragchat/)

`tgedr-ghragchat` is a Python toolkit for document preparation and AI model operations through the OpenRouter API. It includes utilities to load documents from a configurable source, split document content into chunks, and call text, image-generation, text-to-speech, and audio-transcription models.

## Features

- **Document loading:** `DocLoader` loads matching files from a configured source into a destination.
- **Model access:** `Model` provides wrappers for chat completions, image generation, audio generation, and audio transcription.
- **Configuration:** Pydantic Settings reads application settings from environment variables and a `.env` file.

## Configuration

Set the required `SECRET_KEY` and `OPENROUTER_API_KEY` environment variables. They can be placed in a `.env` file in the working directory. The optional `SOURCE_IMPL` setting selects the document source implementation; if omitted, `DocLoader` uses its built-in local filesystem source.

Do not commit secrets or a real `.env` file. Keep credentials in your deployment environment or a local, ignored file.

## Development

Requirements: Python 3.12, [uv](https://docs.astral.sh/uv/), and Bash.

```bash
git clone git@github.com:jtviegas/ghragchat.git
cd ghragchat
./helper.sh reqs
```

Run tests with `./helper.sh test`. To run a focused coverage check for the model wrapper:

```bash
uv run pytest test/tgedr_ghragchat/test_model.py --cov=tgedr_ghragchat.model --cov-report=term-missing
```
