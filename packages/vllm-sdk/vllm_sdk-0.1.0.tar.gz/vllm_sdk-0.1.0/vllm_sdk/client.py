"""HTTPX-based client for the vLLM API with sync and async support."""

import json
from abc import ABC, abstractmethod
from typing import List, Union

import httpx
from pydantic import ValidationError

from vllm_sdk.config import get_model_url
from vllm_sdk.exceptions import VLLMAPIError, VLLMConnectionError, VLLMValidationError
from vllm_sdk.schemas import ChatCompletionResponse, ChatMessage, FeatureSearchResponse


class _BaseClient(ABC):
    """Abstract base class for vLLM API clients with shared logic."""

    def __init__(self, api_key: str, timeout: float = 60.0):
        """Initialize the base client.

        Args:
            api_key: API key for authentication (required)
            timeout: Request timeout in seconds
        """
        if not api_key:
            raise ValueError("api_key is required")

        self.api_key = api_key
        self.timeout = timeout
        self._http_client = None  # Will be set by subclasses

    def _get_base_url(self, model_name: str) -> str:
        """Get the base URL for a given model name.

        Args:
            model_name: The model identifier string

        Returns:
            The base URL for the model
        """
        return get_model_url(model_name)

    def _handle_error(self, response: httpx.Response) -> None:
        """Parse and raise appropriate exception from error response.

        Args:
            response: The HTTP response object

        Raises:
            VLLMAPIError: If the API returns an error
        """
        status_code = response.status_code
        url = str(response.url)
        response_text = response.text or "(empty response)"

        try:
            error_data = response.json()
            detail = (
                error_data.get("detail") or error_data.get("message") or response_text
            )
            error_message = (
                f"API request failed with status {status_code}: {detail}\n"
                f"URL: {url}"
            )
            raise VLLMAPIError(
                message=error_message,
                status_code=status_code,
                response=error_data,
            )
        except (json.JSONDecodeError, ValueError):
            # Response is not valid JSON
            error_message = (
                f"API request failed with status {status_code}\n"
                f"URL: {url}\n"
                f"Response: {response_text[:500]}"  # Limit response text length
            )
            raise VLLMAPIError(
                message=error_message,
                status_code=status_code,
            )

    def _normalize_messages(
        self, messages: Union[List[ChatMessage], List[dict]]
    ) -> List[ChatMessage]:
        """Convert dict messages to ChatMessage objects if needed.

        Args:
            messages: List of ChatMessage objects or dicts

        Returns:
            List of ChatMessage objects
        """
        normalized = []
        for msg in messages:
            if isinstance(msg, dict):
                normalized.append(ChatMessage(**msg))
            elif isinstance(msg, ChatMessage):
                normalized.append(msg)
            else:
                raise ValueError(f"Invalid message type: {type(msg)}")
        return normalized

    def _parse_chat_completion_response(
        self, response: httpx.Response
    ) -> ChatCompletionResponse:
        """Parse a chat completion response.

        Args:
            response: The HTTP response object

        Returns:
            ChatCompletionResponse object

        Raises:
            VLLMValidationError: If response validation fails
        """
        try:
            return ChatCompletionResponse(**response.json())
        except ValidationError as e:
            raise VLLMValidationError(
                message=f"Response validation error: {str(e)}",
            ) from e

    def _parse_feature_search_response(
        self, response: httpx.Response
    ) -> FeatureSearchResponse:
        """Parse a feature search response.

        Args:
            response: The HTTP response object

        Returns:
            FeatureSearchResponse object

        Raises:
            VLLMValidationError: If response validation fails
        """
        try:
            return FeatureSearchResponse(**response.json())
        except ValidationError as e:
            raise VLLMValidationError(
                message=f"Response validation error: {str(e)}",
            ) from e


class Client(_BaseClient):
    """Synchronous client for the vLLM API."""

    def __init__(self, api_key: str, timeout: float = 60.0):
        """Initialize the synchronous vLLM API client.

        Args:
            api_key: API key for authentication (required). Can be just the token
                    or include "Bearer " prefix.
            timeout: Request timeout in seconds
        """
        super().__init__(api_key, timeout)

        # Handle API key that might already include "Bearer " prefix
        auth_header = api_key if api_key.startswith("Bearer ") else f"Bearer {api_key}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_header,
        }

        self._http_client = httpx.Client(
            headers=headers,
            timeout=self.timeout,
        )

        # Initialize nested classes
        from vllm_sdk.chat import Chat
        from vllm_sdk.features import Features

        self.features = Features(self)
        self.chat = Chat(self)

    def close(self):
        """Close the HTTP client."""
        if self._http_client:
            self._http_client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class AsyncClient(_BaseClient):
    """Asynchronous client for the vLLM API."""

    def __init__(self, api_key: str, timeout: float = 60.0):
        """Initialize the asynchronous vLLM API client.

        Args:
            api_key: API key for authentication (required). Can be just the token
                    or include "Bearer " prefix.
            timeout: Request timeout in seconds
        """
        super().__init__(api_key, timeout)

        # Handle API key that might already include "Bearer " prefix
        auth_header = api_key if api_key.startswith("Bearer ") else f"Bearer {api_key}"

        headers = {
            "Content-Type": "application/json",
            "Authorization": auth_header,
        }

        self._http_client = httpx.AsyncClient(
            headers=headers,
            timeout=self.timeout,
        )

        # Initialize nested classes
        from vllm_sdk.chat import AsyncChat
        from vllm_sdk.features import AsyncFeatures

        self.features = AsyncFeatures(self)
        self.chat = AsyncChat(self)

    async def close(self):
        """Close the HTTP client."""
        if self._http_client:
            await self._http_client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
