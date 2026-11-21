"""Model module for interacting with various AI models via OpenRouter API."""

import os
from typing import Any, ClassVar
from enum import Enum
import base64

from tgedr_pycommons.utils.singleton import SingletonMeta

from openai import OpenAI, Stream
from openai.types.audio.transcription import Transcription
from openai.types.chat import ChatCompletion, ChatCompletionChunk


class ReasoningEffort(Enum):
    """Reasoning effort levels supported by the model."""

    NONE = "none"
    MINIMAL = "minimal"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    XHIGH = "xhigh"
    MAX = "max"


class ImageResolution(Enum):
    """Image resolution levels supported by the model."""

    ONE_K = "1K"
    TWO_K = "2K"


class AspectRatio(Enum):
    """Aspect ratio levels supported by the model."""

    ONE_ONE = "1:1"
    SIXTEEN_NINE = "16:9"
    NINE_SIXTEEN = "9:16"
    FOUR_THREE = "4:3"
    THREE_FOUR = "3:4"
    THREE_TWO = "3:2"
    TWO_THREE = "2:3"
    AUTO = "auto"


class Model(metaclass=SingletonMeta):
    """Singleton model manager for interacting with various AI models via OpenRouter API."""

    __api_url: ClassVar[str] = "https://openrouter.ai/api/v1"
    __instance: ClassVar["Model"] = None
    __provider: ClassVar[str] = "openrouter"

    __models: ClassVar[dict[str, dict[str, str]]] = {
        "text": "auto",
        "image": "x-ai/grok-imagine-image-2.0",
        "voice": "mistralai/voxtral-mini-tts-2603",
        "audio": "openai/gpt-4o-mini-transcribe",
    }

    @classmethod
    def instance(cls) -> "Model":
        """Get the singleton instance of the model."""
        if cls.__instance is None:
            cls.__instance = cls()
        return cls.__instance

    def __init__(self) -> None:
        """Initialize the model with an OpenRouter API key."""
        api_key = os.getenv("OPENROUTER_API_KEY")  # pyright: ignore[reportAttributeAccessIssue]
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set.")  # noqa: EM101, TRY003
        self._api = OpenAI(base_url=Model.__api_url, api_key=api_key)

    def text_chat(
        self,
        messages: list[dict[str, Any]],
        reasoning_effort: ReasoningEffort = ReasoningEffort.MEDIUM,
        stream: bool = False,  # noqa: FBT001, FBT002
        tools: list[dict[str, Any]] | None = None,
    ) -> ChatCompletion | Stream[ChatCompletionChunk]:
        """Send a chat completion request to the model.

        Parameters
        ----------
        messages : list[dict[str, Any]]
            The conversation messages to send.
        reasoning_effort : ReasoningEffort, optional
            The reasoning effort level, is MEDIUM by default.
        stream : bool, optional
            Whether to stream the response, is False by default.
        tools : list[dict[str, Any]] | Omit, optional
            Tools available to the model, omitted by default.

        Returns
        -------
        ChatCompletion | Stream[ChatCompletionChunk]
            The chat completion response, or a stream of chunks if streaming.
        """
        if tools is None:
            tools = []
        response = self._api.chat.completions.create(
            model=self.__models["text"],
            messages=messages,
            reasoning_effort=reasoning_effort.value,
            stream=stream,
            tools=tools,
        )
        return response.choices[0].message.content

    def image_generate(
        self,
        prompt: str,
        aspect_ratio: AspectRatio = AspectRatio.AUTO,
        resolution: ImageResolution = ImageResolution.ONE_K,
    ) -> bytes:
        """Generate an image from a text prompt.

        you can use the output image bytes in several ways:
          Image.open(BytesIO(response))

        You can also save it to a file using:
          output_path = Path("generated.png")
          output_path.write_bytes(response)
        or:
          with open(output_path, "wb") as f:
              f.write(response)

        and then open the saved image using:
          Image.open(output_path.resolve())

        Parameters
        ----------
        prompt : str
            The text prompt describing the image to generate.
        aspect_ratio : AspectRatio, optional
            The aspect ratio of the generated image, is AUTO by default.
        resolution : ImageResolution, optional
            The resolution of the generated image, is ONE_K by default.


        Returns
        -------
        bytes
            The generated image data as bytes.
        """
        response = self._api.images.generate(
            model=self.__models["image"],
            prompt=prompt,
            extra_body={"aspect_ratio": aspect_ratio.value, "resolution": resolution.value},
            n=1,
        )
        image_base64 = response.data[0].b64_json
        image_data = base64.b64decode(image_base64)

        return image_data

    def audio_generate(
        self,
        text_input: str,
        voice: str = "en_paul_neutral",
        output_format: str = "mp3",
    ) -> Any:  # noqa: ANN401
        """Generate audio speech from text.

        Parameters
        ----------
        text_input : str
            The text to convert to speech.
        voice : str, optional
            The voice to use, is "en_paul_neutral" by default.
        output_format : str, optional
            The audio format, is "mp3" by default.

        Returns
        -------
        Any
            The generated audio speech response.
        """
        response = self._api.audio.speech.create(
            model=self.__models["voice"], voice=voice, input=text_input, response_format=output_format
        )
        return response.content

    def audio_transcript(
        self,
        audio_file: "FileTypes",  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
        output_format: str = "json",
        language: str = "en",
    ) -> Transcription:
        """Transcribe audio to text.

        Parameters
        ----------
        audio_file : FileTypes
            The audio file to transcribe.
        output_format : str, optional
            The output format, is "json" by default.
        language : str, optional
            The language of the audio, is "en" by default.

        Returns
        -------
        Transcription
            The transcription response.
        """
        response = self._api.audio.transcriptions.create(
            model=self.__models["audio"],
            file=audio_file,
            response_format=output_format,
            language=language,
        )
        return response.text
