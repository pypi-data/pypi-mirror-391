"""Pydantic schemas for vLLM API requests and responses.

All schemas are standalone with no dependencies on vllm_api.
"""

from enum import Enum
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field


class ModelName(str, Enum):
    """Enumeration of supported model names."""

    META_LLAMA_3_1_8B_INSTRUCT = "meta-llama/Meta-Llama-3.1-8B-Instruct"
    META_LLAMA_3_3_70B_INSTRUCT = "meta-llama/Meta-Llama-3.3-70B-Instruct"


# Chat schemas
RoleLiteral = Literal["system", "user", "assistant"]


class ChatMessage(BaseModel):
    role: RoleLiteral
    content: str


class InterventionSpec(BaseModel):
    feature_id: Union[int, str]
    strength: float
    mode: Optional[Literal["add", "clamp"]] = "add"


class ChatCompletionRequest(BaseModel):
    model: Union[ModelName, str]
    messages: List[ChatMessage]
    temperature: float = 0.6
    max_completion_tokens: int = 256
    repetition_penalty: float = 1.0
    seed: Optional[int] = None
    interventions: Optional[List[InterventionSpec]] = Field(
        default=None, description="List of SAE feature interventions"
    )
    stream: bool = False
    is_feature_decode: bool = False
    return_activations: Optional[bool] = False
    get_activations_layer: Optional[List[int]] = None


class ChatCompletionMessage(BaseModel):
    role: Literal["assistant"]
    content: str


class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatCompletionMessage
    finish_reason: Optional[str] = "stop"
    logprobs: Optional[dict] = None


class ChatCompletionUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    id: str
    object: Literal["chat.completion"]
    created: int
    model: str
    choices: List[ChatCompletionChoice]
    usage: ChatCompletionUsage
    features: Optional[dict] = None
    activations: Optional[dict] = None


class ChatCompletionDelta(BaseModel):
    role: Optional[str] = None
    content: Optional[str] = None


class ChatCompletionChunkChoice(BaseModel):
    index: int
    delta: ChatCompletionDelta
    finish_reason: Optional[str] = None


class ChatCompletionChunk(BaseModel):
    id: str
    object: Literal["chat.completion.chunk"]
    created: int
    model: str
    choices: List[ChatCompletionChunkChoice]


# Feature search schemas
class FeatureItem(BaseModel):
    """Schema for a single feature item in search results."""

    id: Union[int, str]
    label: str
    layer: int
    dimension: Optional[int] = None
    activation_stats: Optional[dict] = None


class FeatureSearchRequest(BaseModel):
    """Request schema for feature search."""

    query: str = Field(..., description="Search query string")
    model: Union[ModelName, str] = Field(..., description="Model identifier")
    top_k: int = Field(
        default=10, ge=1, le=100, description="Number of top results to return"
    )


class FeatureSearchResponse(BaseModel):
    """Response schema for feature search."""

    object: str = "feature.list"
    data: List[FeatureItem]
