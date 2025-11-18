# vLLM SDK

Minimal Python SDK for the vLLM API. This package provides a lightweight client library for interacting with vLLM API servers, with only `httpx` and `pydantic` as dependencies.

## Installation

```bash
pip install vllm-sdk
```

## Quick Start

```python
import asyncio
from vllm_sdk import VLLMClient, ChatMessage

async def main():
    async with VLLMClient(base_url="http://localhost:8000") as client:
        # Non-streaming chat completion
        response = await client.chat_completions(
            model="meta-llama/Meta-Llama-3.3-70B-Instruct",
            messages=[
                ChatMessage(role="user", content="Hello!")
            ],
        )
        print(response.choices[0].message.content)

        # Streaming chat completion
        async for chunk in client.chat_completions_stream(
            model="meta-llama/Meta-Llama-3.3-70B-Instruct",
            messages=[
                ChatMessage(role="user", content="Tell me a story")
            ],
        ):
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)

asyncio.run(main())
```

## Features

- **Minimal Dependencies**: Only requires `httpx` and `pydantic`
- **Type Safety**: Full Pydantic schema validation for requests and responses
- **Async Support**: Built on `httpx` for async/await support
- **Streaming**: Support for streaming chat completions
- **Feature Search**: Search SAE features by semantic similarity

## API Reference

### VLLMClient

The main client class for interacting with the vLLM API.

#### Methods

- `chat_completions()` - Create a non-streaming chat completion
- `chat_completions_stream()` - Stream chat completions (async generator)
- `feature_search()` - Search for SAE features

### Schemas

All request and response models are available for import:

- `ChatMessage` - Individual chat message
- `ChatCompletionRequest` - Chat completion request
- `ChatCompletionResponse` - Chat completion response
- `ChatCompletionChunk` - Streaming chunk
- `FeatureSearchRequest` - Feature search request
- `FeatureSearchResponse` - Feature search response
- `ModelName` - Supported model names enum

## Examples

### Feature Search

```python
from vllm_sdk import VLLMClient, FeatureSearchRequest

async with VLLMClient(base_url="http://localhost:8000") as client:
    response = await client.feature_search(
        query="pirate speech",
        model="meta-llama/Meta-Llama-3.3-70B-Instruct",
        top_k=10,
    )
    for feature in response.data:
        print(f"{feature.id}: {feature.label} (layer {feature.layer})")
```

### With Interventions

```python
from vllm_sdk import VLLMClient, ChatMessage, InterventionSpec

async with VLLMClient(base_url="http://localhost:8000") as client:
    response = await client.chat_completions(
        model="meta-llama/Meta-Llama-3.3-70B-Instruct",
        messages=[ChatMessage(role="user", content="Hello!")],
        interventions=[
            InterventionSpec(
                feature_id="feature_123",
                strength=2.0,
                mode="add"
            )
        ],
    )
```

## License

Apache 2.0

## Links

- [Documentation](https://docs.vllm.ai/en/latest/)
- [GitHub Repository](https://github.com/vllm-project/vllm)
- [Issue Tracker](https://github.com/vllm-project/vllm/issues)
