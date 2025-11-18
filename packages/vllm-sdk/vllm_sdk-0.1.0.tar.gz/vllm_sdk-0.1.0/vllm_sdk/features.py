"""Features nested classes for feature search functionality."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Union

import httpx

from vllm_sdk.schemas import FeatureSearchRequest, FeatureSearchResponse

if TYPE_CHECKING:
    from vllm_sdk.variant import Variant


class _BaseFeatures(ABC):
    """Abstract base class for Features functionality."""

    @abstractmethod
    def search(
        self,
        query: str,
        model: Union["Variant", str],
        top_k: int = 10,
    ):
        """Search for SAE features by semantic similarity.

        Args:
            query: Search query string
            model: Variant instance or model name string
            top_k: Number of top results to return

        Returns:
            FeatureSearchResponse with list of matching features
        """
        pass


class Features(_BaseFeatures):
    """Synchronous Features class for feature search."""

    def __init__(self, client):
        """Initialize Features with a synchronous HTTP client.

        Args:
            client: The parent Client instance with sync HTTP client
        """
        self._client = client

    def search(
        self,
        query: str,
        model: Union["Variant", str],
        top_k: int = 10,
    ) -> FeatureSearchResponse:
        """Search for SAE features by semantic similarity (synchronous).

        Args:
            query: Search query string
            model: Variant instance or model name string
            top_k: Number of top results to return

        Returns:
            FeatureSearchResponse with list of matching features
        """
        # Extract model name from Variant if needed
        model_name = model.model_name if isinstance(model, Variant) else model

        # Get base URL for the model
        base_url = self._client._get_base_url(model_name)

        # Build request
        request = FeatureSearchRequest(
            query=query,
            model=model_name,
            top_k=top_k,
        )

        # Make HTTP request
        # Ensure base_url doesn't have trailing slash
        base_url = base_url.rstrip("/")
        try:
            response = self._client._http_client.post(
                f"{base_url}/v1/features/search",
                json=request.model_dump(),
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._client._handle_error(e.response)
        except httpx.RequestError as e:
            from vllm_sdk.exceptions import VLLMConnectionError

            raise VLLMConnectionError(
                message=f"Connection error: {str(e)}",
            ) from e

        # Parse and return response
        return self._client._parse_feature_search_response(response)


class AsyncFeatures(_BaseFeatures):
    """Asynchronous Features class for feature search."""

    def __init__(self, client):
        """Initialize AsyncFeatures with an asynchronous HTTP client.

        Args:
            client: The parent AsyncClient instance with async HTTP client
        """
        self._client = client

    async def search(
        self,
        query: str,
        model: Union["Variant", str],
        top_k: int = 10,
    ) -> FeatureSearchResponse:
        """Search for SAE features by semantic similarity (asynchronous).

        Args:
            query: Search query string
            model: Variant instance or model name string
            top_k: Number of top results to return

        Returns:
            FeatureSearchResponse with list of matching features
        """
        # Extract model name from Variant if needed
        model_name = model.model_name if isinstance(model, Variant) else model

        # Get base URL for the model
        base_url = self._client._get_base_url(model_name)

        # Build request
        request = FeatureSearchRequest(
            query=query,
            model=model_name,
            top_k=top_k,
        )

        # Make HTTP request
        # Ensure base_url doesn't have trailing slash
        base_url = base_url.rstrip("/")
        try:
            response = await self._client._http_client.post(
                f"{base_url}/v1/features/search",
                json=request.model_dump(),
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            self._client._handle_error(e.response)
        except httpx.RequestError as e:
            from vllm_sdk.exceptions import VLLMConnectionError

            raise VLLMConnectionError(
                message=f"Connection error: {str(e)}",
            ) from e

        # Parse and return response
        return self._client._parse_feature_search_response(response)


# Import here to avoid circular dependency
from vllm_sdk.variant import Variant  # noqa: E402
