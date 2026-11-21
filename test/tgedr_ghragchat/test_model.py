"""Unit tests for model API wrappers."""

import base64
from unittest.mock import Mock

import pytest

from tgedr_pycommons.utils.singleton import SingletonMeta
from tgedr_ghragchat import model as model_module


@pytest.fixture(autouse=True)
def reset_model_singleton() -> None:
    """Reset singleton state so tests do not share a model instance."""
    SingletonMeta._instances.pop(model_module.Model, None)
    model_module.Model._Model__instance = None


@pytest.fixture
def model(monkeypatch: pytest.MonkeyPatch) -> tuple[model_module.Model, Mock, Mock]:
    """Create a model with a mocked OpenAI client."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-api-key")
    api = Mock()
    openai_constructor = Mock(return_value=api)
    monkeypatch.setattr(model_module, "OpenAI", openai_constructor)
    instance = model_module.Model()
    return instance, api, openai_constructor


def test_instance_returns_singleton_and_initializes_once(model: tuple[model_module.Model, Mock, Mock]) -> None:
    """Return the same cached model instance on repeated calls."""
    expected_model, _, openai_constructor = model

    assert model_module.Model.instance() is expected_model
    assert model_module.Model.instance() is expected_model
    openai_constructor.assert_called_once_with(
        base_url="https://openrouter.ai/api/v1",
        api_key="test-api-key",
    )


def test_init_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Raise a clear error when the OpenRouter key is missing."""
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    with pytest.raises(ValueError, match="OPENROUTER_API_KEY environment variable is not set"):
        model_module.Model()


def test_text_chat_defaults_tools_to_empty_list(model: tuple[model_module.Model, Mock, Mock]) -> None:
    """Send a non-streaming request and return its message content."""
    instance, api, _ = model
    message_content = "Hello from the model"
    api.chat.completions.create.return_value.choices = [Mock(message=Mock(content=message_content))]
    messages = [{"role": "user", "content": "Hello"}]

    result = instance.text_chat(messages)

    assert result == message_content
    api.chat.completions.create.assert_called_once_with(
        model="auto",
        messages=messages,
        reasoning_effort="medium",
        stream=False,
        tools=[],
    )


def test_text_chat_passes_optional_arguments(model: tuple[model_module.Model, Mock, Mock]) -> None:
    """Pass supplied tools, reasoning effort, and streaming option through."""
    instance, api, _ = model
    api.chat.completions.create.return_value.choices = [Mock(message=Mock(content="stream response"))]
    messages = [{"role": "user", "content": "Think carefully"}]
    tools = [{"type": "function", "function": {"name": "lookup"}}]

    result = instance.text_chat(messages, model_module.ReasoningEffort.HIGH, True, tools)

    assert result == "stream response"
    api.chat.completions.create.assert_called_once_with(
        model="auto",
        messages=messages,
        reasoning_effort="high",
        stream=True,
        tools=tools,
    )


def test_image_generate_decodes_image_and_passes_parameters(model: tuple[model_module.Model, Mock, Mock]) -> None:
    """Decode the returned base64 image and pass chosen image settings."""
    instance, api, _ = model
    image_bytes = b"fake-image-bytes"
    api.images.generate.return_value.data = [Mock(b64_json=base64.b64encode(image_bytes).decode("ascii"))]

    result = instance.image_generate(
        "A test image",
        aspect_ratio=model_module.AspectRatio.SIXTEEN_NINE,
        resolution=model_module.ImageResolution.TWO_K,
    )

    assert result == image_bytes
    api.images.generate.assert_called_once_with(
        model="x-ai/grok-imagine-image-2.0",
        prompt="A test image",
        extra_body={"aspect_ratio": "16:9", "resolution": "2K"},
        n=1,
    )


def test_audio_generate_returns_audio_bytes(model: tuple[model_module.Model, Mock, Mock]) -> None:
    """Return generated audio bytes and pass custom voice and format."""
    instance, api, _ = model
    audio_bytes = b"fake-mp3-data"
    api.audio.speech.create.return_value.content = audio_bytes

    result = instance.audio_generate("Say hello", voice="custom-voice", output_format="wav")

    assert result == audio_bytes
    api.audio.speech.create.assert_called_once_with(
        model="mistralai/voxtral-mini-tts-2603",
        voice="custom-voice",
        input="Say hello",
        response_format="wav",
    )


def test_audio_transcript_returns_text(model: tuple[model_module.Model, Mock, Mock]) -> None:
    """Return transcript text and pass custom format and language."""
    instance, api, _ = model
    audio_file = object()
    api.audio.transcriptions.create.return_value.text = "Recognized words"

    result = instance.audio_transcript(audio_file, output_format="text", language="fr")

    assert result == "Recognized words"
    api.audio.transcriptions.create.assert_called_once_with(
        model="openai/gpt-4o-mini-transcribe",
        file=audio_file,
        response_format="text",
        language="fr",
    )
