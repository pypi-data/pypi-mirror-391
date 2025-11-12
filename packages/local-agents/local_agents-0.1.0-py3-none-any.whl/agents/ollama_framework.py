"""
Unified Ollama Agent Framework
==============================

This module provides a unified abstraction for interacting with Ollama models
across both single-node and distributed deployments. It defines a base client
interface and concrete implementations for local and distributed use cases.

Classes
-------
* BaseOllamaClient – Abstract base class defining common methods
* LocalOllamaClient – Single-node HTTP client implementation
* DistributedOllamaClient – Multi-node client with SOLLOL integration

Example
-------
```python
from ollama_framework import LocalOllamaClient

# Create a client for a single local server
client = LocalOllamaClient(model_name="llama3:latest", api_base="http://localhost:11434")

# Generate an embedding
embedding = await client.generate_embedding("Hello world")

# Chat with streaming responses
async for chunk in client.chat([{"role": "user", "content": "Tell me a joke."}]):
    print(chunk.content, end="")

await client.close()
```
"""

from __future__ import annotations

import abc
import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Dict, Iterable, List, Optional, Union

# Conditional import for SOLLOL
try:
    from sollol import OllamaPool
except ImportError:
    OllamaPool = None

logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    """Representation of a chat message.

    Parameters
    ----------
    role : str
        The role of the sender (e.g. "user", "assistant", "system")
    content : str
        The textual content of the message
    """
    role: str
    content: str


@dataclass
class ChatResponse:
    """Represents a partial or complete chat response.

    Parameters
    ----------
    content : str
        The textual content of the response chunk
    role : str, optional
        The role of the responder (defaults to "assistant")
    done : bool, optional
        Whether this chunk marks the end of the response
    metadata : dict, optional
        Arbitrary metadata associated with the response
    """
    content: str
    role: str = "assistant"
    done: bool = False
    metadata: Dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.metadata is None:
            self.metadata = {}


class BaseOllamaClient(abc.ABC):
    """Abstract base class defining the common interface for Ollama clients.

    Implementations must provide methods for generating embeddings and sending
    chat requests. Both asynchronous and synchronous entry points are offered.
    """

    def __init__(self, model_name: str, embed_model: Optional[str] = None) -> None:
        self.model_name = model_name
        self.embed_model = embed_model or model_name

    # ----------------------- Embedding API -----------------------

    @abc.abstractmethod
    async def generate_embedding(self, text: str) -> List[float]:
        """Generate an embedding for the given text asynchronously.

        Parameters
        ----------
        text : str
            Input text to embed

        Returns
        -------
        list of float
            The embedding vector
        """

    async def embeddings(self, text: str) -> List[float]:
        """Alias of generate_embedding for backward compatibility."""
        return await self.generate_embedding(text)

    # ----------------------- Chat API ----------------------------

    @abc.abstractmethod
    async def chat(
        self,
        messages: Iterable[Union[ChatMessage, Dict[str, Any]]],
        stream: bool = True,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **options: Any,
    ) -> AsyncGenerator[ChatResponse, None]:
        """Send a chat request and yield streaming responses.

        Parameters
        ----------
        messages : iterable of ChatMessage or dict
            The conversation history to send to the model
        stream : bool, optional
            Whether to stream partial responses (default True)
        temperature : float, optional
            Sampling temperature
        top_p : float, optional
            Nucleus sampling probability
        max_tokens : int, optional
            Maximum number of tokens to generate
        options : any
            Additional options passed to the underlying engine

        Yields
        ------
        ChatResponse
            Streaming response chunks
        """

    # ----------------------- Synchronous Wrappers ----------------

    def generate_embedding_sync(self, text: str) -> List[float]:
        """Synchronous wrapper around generate_embedding."""
        return asyncio.run(self.generate_embedding(text))

    def embeddings_sync(self, text: str) -> List[float]:
        """Alias for generate_embedding_sync."""
        return self.generate_embedding_sync(text)

    def chat_sync(
        self,
        messages: Iterable[Union[ChatMessage, Dict[str, Any]]],
        stream: bool = False,
        **options: Any,
    ) -> List[ChatResponse]:
        """Synchronous wrapper around chat.

        Collects streaming responses into a list.
        """
        async def _collect() -> List[ChatResponse]:
            collected: List[ChatResponse] = []
            async for chunk in self.chat(messages, stream=stream, **options):
                collected.append(chunk)
            return collected

        return asyncio.run(_collect())


class LocalOllamaClient(BaseOllamaClient):
    """Implementation of BaseOllamaClient for a single Ollama server.

    Uses aiohttp for asynchronous HTTP requests. Supports basic error
    handling and streaming responses.

    Parameters
    ----------
    model_name : str
        The default model to use for generation
    api_base : str
        The base URL of the Ollama server
    embed_model : str, optional
        The model to use for embeddings (defaults to model_name)
    """

    def __init__(
        self,
        model_name: str,
        api_base: str,
        embed_model: Optional[str] = None,
        keep_alive: Optional[str] = None
    ) -> None:
        super().__init__(model_name, embed_model=embed_model)
        self.api_base = api_base.rstrip("/")
        self.keep_alive = keep_alive  # Keep model in memory (e.g., "5m", "1h")
        self._session: Optional["aiohttp.ClientSession"] = None

    async def _ensure_session(self) -> None:
        if self._session is None:
            import aiohttp
            self._session = aiohttp.ClientSession()

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate an embedding using the configured embedding model."""
        await self._ensure_session()
        if not text.strip():
            return []

        url = f"{self.api_base}/api/embeddings"
        payload: Dict[str, Any] = {
            "model": self.embed_model,
            "prompt": text,
        }

        import aiohttp
        async with self._session.post(url, json=payload) as response:
            if response.status != 200:
                body = await response.text()
                raise RuntimeError(f"Embedding request failed: {response.status} {body}")
            result = await response.json()
            embedding = result.get("embedding")
            if not embedding:
                raise RuntimeError("Missing 'embedding' in response")
            return embedding

    async def chat(
        self,
        messages: Iterable[Union[ChatMessage, Dict[str, Any]]],
        stream: bool = True,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **options: Any,
    ) -> AsyncGenerator[ChatResponse, None]:
        """Send chat completion requests and yield responses as they arrive."""
        await self._ensure_session()

        # Normalize message format
        message_dicts: List[Dict[str, Any]] = []
        for msg in messages:
            if isinstance(msg, ChatMessage):
                message_dicts.append({"role": msg.role, "content": msg.content})
            elif isinstance(msg, dict):
                message_dicts.append(msg)
            else:
                message_dicts.append({"role": "user", "content": str(msg)})

        url = f"{self.api_base}/api/chat"
        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": message_dicts,
            "stream": stream,
            "options": {},
        }

        if temperature is not None:
            payload["options"]["temperature"] = temperature
        if top_p is not None:
            payload["options"]["top_p"] = top_p
        if max_tokens is not None:
            payload["options"]["num_predict"] = max_tokens
        if self.keep_alive is not None:
            payload["keep_alive"] = self.keep_alive

        payload["options"].update(options)

        import aiohttp
        async with self._session.post(url, json=payload) as response:
            if response.status != 200:
                body = await response.text()
                raise RuntimeError(f"Chat request failed: {response.status} {body}")

            # Parse line by line for streaming
            async for line in response.content:
                if not line:
                    continue
                try:
                    chunk = json.loads(line)
                except json.JSONDecodeError:
                    continue

                if "error" in chunk:
                    raise RuntimeError(f"Error from Ollama: {chunk['error']}")

                if "message" in chunk and "content" in chunk["message"]:
                    yield ChatResponse(
                        content=chunk["message"]["content"],
                        role=chunk["message"].get("role", "assistant"),
                        done=chunk.get("done", False),
                        metadata={
                            key: chunk[key]
                            for key in ["eval_count", "eval_duration", "total_duration", "load_duration"]
                            if key in chunk
                        },
                    )

    async def close(self) -> None:
        """Close the underlying HTTP session."""
        if self._session is not None:
            await self._session.close()
            self._session = None


class DistributedOllamaClient(BaseOllamaClient):
    """Client implementation that delegates requests to a SOLLOL OllamaPool.

    The OllamaPool handles auto-discovery, intelligent routing, and fail-over
    across multiple Ollama nodes.

    Parameters
    ----------
    model_name : str
        The default model to use for generation
    embed_model : str, optional
        The model to use for embeddings (defaults to model_name)
    pool_kwargs : any
        Additional arguments passed to OllamaPool initialization
    """

    def __init__(
        self,
        model_name: str,
        embed_model: Optional[str] = None,
        **pool_kwargs: Any,
    ) -> None:
        super().__init__(model_name, embed_model=embed_model)
        if OllamaPool is None:
            raise ImportError(
                "sollol package not found; install it to use DistributedOllamaClient"
            )

        # Create a pool configured with the supplied arguments
        self.pool = OllamaPool(
            default_model=model_name,
            enable_intelligent_routing=True,
            **pool_kwargs,
        )

    async def generate_embedding(self, text: str) -> List[float]:
        """Generate an embedding via the SOLLOL pool."""
        if not text.strip():
            return []

        # Check if pool has an embed method
        if hasattr(self.pool, "embed"):
            return await self.pool.embed(text, model=self.embed_model)

        # Otherwise route manually
        node_url = await self.pool.route_request(model=self.embed_model)
        if not node_url:
            raise RuntimeError("No available Ollama nodes for embeddings")

        import aiohttp
        async with aiohttp.ClientSession() as session:
            payload = {"model": self.embed_model, "prompt": text}
            async with session.post(f"{node_url}/api/embeddings", json=payload) as resp:
                if resp.status != 200:
                    body = await resp.text()
                    raise RuntimeError(f"Embedding request failed: {resp.status} {body}")
                data = await resp.json()
                return data.get("embedding", [])

    async def chat(
        self,
        messages: Iterable[Union[ChatMessage, Dict[str, Any]]],
        stream: bool = True,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **options: Any,
    ) -> AsyncGenerator[ChatResponse, None]:
        """Send chat requests via the SOLLOL pool."""
        # Normalize messages
        message_dicts: List[Dict[str, Any]] = []
        for msg in messages:
            if isinstance(msg, ChatMessage):
                message_dicts.append({"role": msg.role, "content": msg.content})
            elif isinstance(msg, dict):
                message_dicts.append(msg)
            else:
                message_dicts.append({"role": "user", "content": str(msg)})

        # Check if pool has a chat method
        if hasattr(self.pool, "chat"):
            async for chunk in self.pool.chat(
                message_dicts,
                stream=stream,
                temperature=temperature,
                top_p=top_p,
                max_tokens=max_tokens,
                **options,
            ):
                # Adapt to ChatResponse
                yield ChatResponse(
                    content=chunk.get("content", ""),
                    role=chunk.get("role", "assistant"),
                    done=chunk.get("done", False),
                    metadata=chunk.get("metadata", {}),
                )
            return

        # Otherwise select a node and perform streaming chat manually
        node_url = await self.pool.route_request(model=self.model_name)
        if not node_url:
            raise RuntimeError("No available Ollama nodes for chat")

        url = f"{node_url}/api/chat"
        payload: Dict[str, Any] = {
            "model": self.model_name,
            "messages": message_dicts,
            "stream": stream,
            "options": {},
        }

        if temperature is not None:
            payload["options"]["temperature"] = temperature
        if top_p is not None:
            payload["options"]["top_p"] = top_p
        if max_tokens is not None:
            payload["options"]["num_predict"] = max_tokens
        payload["options"].update(options)

        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    body = await response.text()
                    raise RuntimeError(f"Chat request failed: {response.status} {body}")

                async for line in response.content:
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    if "error" in chunk:
                        raise RuntimeError(f"Error from Ollama: {chunk['error']}")

                    if "message" in chunk and "content" in chunk["message"]:
                        yield ChatResponse(
                            content=chunk["message"]["content"],
                            role="assistant",
                            done=chunk.get("done", False),
                            metadata={
                                key: chunk[key]
                                for key in ["eval_count", "eval_duration", "total_duration", "load_duration"]
                                if key in chunk
                            },
                        )


__all__ = [
    "ChatMessage",
    "ChatResponse",
    "BaseOllamaClient",
    "LocalOllamaClient",
    "DistributedOllamaClient",
]
