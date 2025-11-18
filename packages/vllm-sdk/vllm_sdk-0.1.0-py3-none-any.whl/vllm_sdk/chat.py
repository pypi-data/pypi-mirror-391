"""Chat completions nested classes for chat functionality."""

import json
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, AsyncIterator, List, Optional, Union

import httpx
from pydantic import ValidationError

from vllm_sdk.exceptions import VLLMConnectionError, VLLMValidationError
from vllm_sdk.schemas import (
    ChatCompletionChunk,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    InterventionSpec,
)

if TYPE_CHECKING:
    from vllm_sdk.variant import Variant


class _BaseChatCompletions(ABC):
    """Abstract base class for ChatCompletions functionality."""

    @abstractmethod
    def create(
        self,
        model: Union["Variant", str],
        messages: Union[List[ChatMessage], List[dict]],
        max_completion_tokens: int,
        temperature: float = 0.6,
        seed: Optional[int] = None,
        interventions: Optional[List[InterventionSpec]] = None,
        repetition_penalty: float = 1.0,
        stream: bool = False,
        is_feature_decode: bool = False,
        return_activations: Optional[bool] = False,
        get_activations_layer: Optional[List[int]] = None,
    ):
        """Create a chat completion.

        Args:
            model: Variant instance or model name string
            messages: List of chat messages (ChatMessage objects or dicts)
            max_completion_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            seed: Random seed
            interventions: List of SAE feature interventions
            repetition_penalty: Repetition penalty
            stream: Whether to stream the response
            is_feature_decode: Return features instead of text
            return_activations: Return activation data
            get_activations_layer: Layers to get activations from

        Returns:
            ChatCompletionResponse object
        """
        pass


class ChatCompletions(_BaseChatCompletions):
    """Synchronous ChatCompletions class."""

    def __init__(self, client):
        """Initialize ChatCompletions with a synchronous HTTP client.

        Args:
            client: The parent Client instance with sync HTTP client
        """
        self._client = client

    def create(
        self,
        model: Union["Variant", str],
        messages: Union[List[ChatMessage], List[dict]],
        max_completion_tokens: int,
        temperature: float = 0.6,
        seed: Optional[int] = None,
        interventions: Optional[List[InterventionSpec]] = None,
        repetition_penalty: float = 1.0,
        stream: bool = False,
        is_feature_decode: bool = False,
        return_activations: Optional[bool] = False,
        get_activations_layer: Optional[List[int]] = None,
    ) -> ChatCompletionResponse:
        """Create a chat completion (synchronous).

        Args:
            model: Variant instance or model name string
            messages: List of chat messages (ChatMessage objects or dicts)
            max_completion_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            seed: Random seed
            interventions: List of SAE feature interventions
            repetition_penalty: Repetition penalty
            stream: Whether to stream the response (not supported in sync)
            is_feature_decode: Return features instead of text
            return_activations: Return activation data
            get_activations_layer: Layers to get activations from

        Returns:
            ChatCompletionResponse object
        """
        if stream:
            raise ValueError(
                "Streaming is not supported in synchronous client. Use AsyncClient instead."
            )

        # Extract model name from Variant if needed
        model_name = model.model_name if isinstance(model, Variant) else model

        # Get base URL for the model
        base_url = self._client._get_base_url(model_name)

        # Convert dict messages to ChatMessage objects if needed
        chat_messages = self._client._normalize_messages(messages)

        # Build request
        request = ChatCompletionRequest(
            model=model_name,
            messages=chat_messages,
            temperature=temperature,
            max_completion_tokens=max_completion_tokens,
            repetition_penalty=repetition_penalty,
            seed=seed,
            interventions=interventions,
            stream=False,
            is_feature_decode=is_feature_decode,
            return_activations=return_activations,
            get_activations_layer=get_activations_layer,
        )

        # Make HTTP request
        # Ensure base_url doesn't have trailing slash
        base_url = base_url.rstrip("/")
        try:
            response = self._client._http_client.post(
                f"{base_url}/v1/chat/completions",
                json=request.model_dump(),
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._client._handle_error(e.response)
        except httpx.RequestError as e:
            raise VLLMConnectionError(
                message=f"Connection error: {str(e)}",
            ) from e

        # Parse and return response
        return self._client._parse_chat_completion_response(response)


class AsyncChatCompletions(_BaseChatCompletions):
    """Asynchronous ChatCompletions class."""

    def __init__(self, client):
        """Initialize AsyncChatCompletions with an asynchronous HTTP client.

        Args:
            client: The parent AsyncClient instance with async HTTP client
        """
        self._client = client

    async def create(
        self,
        model: Union["Variant", str],
        messages: Union[List[ChatMessage], List[dict]],
        max_completion_tokens: int,
        temperature: float = 0.6,
        seed: Optional[int] = None,
        interventions: Optional[List[InterventionSpec]] = None,
        repetition_penalty: float = 1.0,
        stream: bool = False,
        is_feature_decode: bool = False,
        return_activations: Optional[bool] = False,
        get_activations_layer: Optional[List[int]] = None,
    ) -> ChatCompletionResponse:
        """Create a chat completion (asynchronous).

        Args:
            model: Variant instance or model name string
            messages: List of chat messages (ChatMessage objects or dicts)
            max_completion_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            seed: Random seed
            interventions: List of SAE feature interventions
            repetition_penalty: Repetition penalty
            stream: Whether to stream the response (use create_stream for streaming)
            is_feature_decode: Return features instead of text
            return_activations: Return activation data
            get_activations_layer: Layers to get activations from

        Returns:
            ChatCompletionResponse object
        """
        if stream:
            raise ValueError("Use create_stream() method for streaming responses")

        # Extract model name from Variant if needed
        model_name = model.model_name if isinstance(model, Variant) else model

        # Get base URL for the model
        base_url = self._client._get_base_url(model_name)

        # Convert dict messages to ChatMessage objects if needed
        chat_messages = self._client._normalize_messages(messages)

        # Build request
        request = ChatCompletionRequest(
            model=model_name,
            messages=chat_messages,
            temperature=temperature,
            max_completion_tokens=max_completion_tokens,
            repetition_penalty=repetition_penalty,
            seed=seed,
            interventions=interventions,
            stream=False,
            is_feature_decode=is_feature_decode,
            return_activations=return_activations,
            get_activations_layer=get_activations_layer,
        )

        # Make HTTP request
        # Ensure base_url doesn't have trailing slash
        base_url = base_url.rstrip("/")
        try:
            response = await self._client._http_client.post(
                f"{base_url}/v1/chat/completions",
                json=request.model_dump(),
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._client._handle_error(e.response)
        except httpx.RequestError as e:
            raise VLLMConnectionError(
                message=f"Connection error: {str(e)}",
            ) from e

        # Parse and return response
        return self._client._parse_chat_completion_response(response)

    async def create_stream(
        self,
        model: Union["Variant", str],
        messages: Union[List[ChatMessage], List[dict]],
        max_completion_tokens: int,
        temperature: float = 0.6,
        seed: Optional[int] = None,
        interventions: Optional[List[InterventionSpec]] = None,
        repetition_penalty: float = 1.0,
        is_feature_decode: bool = False,
    ) -> AsyncIterator[ChatCompletionChunk]:
        """Stream chat completions (asynchronous).

        Yields:
            ChatCompletionChunk objects
        """
        # Extract model name from Variant if needed
        model_name = model.model_name if isinstance(model, Variant) else model

        # Get base URL for the model
        base_url = self._client._get_base_url(model_name)

        # Convert dict messages to ChatMessage objects if needed
        chat_messages = self._client._normalize_messages(messages)

        # Build request
        request = ChatCompletionRequest(
            model=model_name,
            messages=chat_messages,
            temperature=temperature,
            max_completion_tokens=max_completion_tokens,
            repetition_penalty=repetition_penalty,
            seed=seed,
            interventions=interventions,
            stream=True,
            is_feature_decode=is_feature_decode,
        )

        # Ensure base_url doesn't have trailing slash
        base_url = base_url.rstrip("/")
        try:
            async with self._client._http_client.stream(
                "POST",
                f"{base_url}/v1/chat/completions",
                json=request.model_dump(),
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk_data = json.loads(data)
                            yield ChatCompletionChunk(**chunk_data)
                        except (
                            json.JSONDecodeError,
                            ValidationError,
                            TypeError,
                            KeyError,
                        ):
                            # Skip invalid chunks
                            continue

        except Exception as e:
            raise VLLMConnectionError(
                message=f"Streaming error: {str(e)}",
            ) from e


# Import here to avoid circular dependency
from vllm_sdk.variant import Variant  # noqa: E402


class Chat:
    """Synchronous Chat wrapper class following OpenAI SDK structure."""

    def __init__(self, client):
        """Initialize Chat with a synchronous HTTP client.

        Args:
            client: The parent Client instance with sync HTTP client
        """
        self.completions = ChatCompletions(client)


class AsyncChat:
    """Asynchronous Chat wrapper class following OpenAI SDK structure."""

    def __init__(self, client):
        """Initialize AsyncChat with an asynchronous HTTP client.

        Args:
            client: The parent AsyncClient instance with async HTTP client
        """
        self.completions = AsyncChatCompletions(client)
