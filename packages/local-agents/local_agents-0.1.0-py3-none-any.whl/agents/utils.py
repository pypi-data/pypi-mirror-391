"""
Utility functions for the agents framework.

This module provides helper functions for common tasks such as:
- Health checking nodes
- Response parsing
- Timeout management
- Error handling
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


def parse_json_response(text: str, strict: bool = False) -> Optional[Dict[str, Any]]:
    """Attempt to parse JSON from a text response.

    This function handles common issues with LLM-generated JSON:
    - Markdown code blocks
    - Extra text before/after JSON
    - Malformed JSON

    Parameters
    ----------
    text : str
        The text to parse
    strict : bool, optional
        If True, raise an exception on parse failure. Otherwise return None.

    Returns
    -------
    dict or None
        The parsed JSON object, or None if parsing fails

    Raises
    ------
    ValueError
        If strict=True and parsing fails
    """
    if not text or not text.strip():
        if strict:
            raise ValueError("Empty text provided")
        return None

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to extract from markdown code blocks
    import re
    code_block_match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
    if code_block_match:
        try:
            return json.loads(code_block_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find any JSON object in the text
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass

    if strict:
        raise ValueError(f"Could not parse JSON from text: {text[:100]}...")
    return None


def check_node_health(url: str, timeout: float = 2.0) -> bool:
    """Check if an Ollama node is healthy and responsive.

    Parameters
    ----------
    url : str
        The base URL of the Ollama server
    timeout : float, optional
        Request timeout in seconds

    Returns
    -------
    bool
        True if the node is healthy, False otherwise
    """
    import requests

    try:
        response = requests.get(
            f"{url.rstrip('/')}/api/tags",
            timeout=timeout
        )
        return response.status_code == 200
    except Exception as e:
        logger.debug(f"Health check failed for {url}: {e}")
        return False


def retry_with_backoff(
    func,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """Retry a function with exponential backoff.

    Parameters
    ----------
    func : callable
        The function to retry
    max_retries : int, optional
        Maximum number of retry attempts
    initial_delay : float, optional
        Initial delay in seconds
    backoff_factor : float, optional
        Multiplier for delay after each retry
    exceptions : tuple, optional
        Tuple of exception types to catch

    Returns
    -------
    any
        The return value of func

    Raises
    ------
    Exception
        The last exception raised if all retries fail
    """
    delay = initial_delay
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            return func()
        except exceptions as e:
            last_exception = e
            if attempt < max_retries:
                logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                time.sleep(delay)
                delay *= backoff_factor
            else:
                logger.error(f"All {max_retries + 1} attempts failed")

    raise last_exception


def format_chat_history(
    messages: List[Union[Dict[str, str], Any]],
    max_length: Optional[int] = None
) -> str:
    """Format a chat history for display.

    Parameters
    ----------
    messages : list
        List of message dictionaries with 'role' and 'content' keys
    max_length : int, optional
        Maximum length for each message content (truncates if longer)

    Returns
    -------
    str
        Formatted chat history
    """
    lines = []
    for msg in messages:
        if hasattr(msg, "role"):
            role = msg.role
            content = msg.content
        elif isinstance(msg, dict):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
        else:
            continue

        if max_length and len(content) > max_length:
            content = content[:max_length] + "..."

        lines.append(f"{role.upper()}: {content}")

    return "\n".join(lines)


def estimate_tokens(text: str) -> int:
    """Rough estimation of token count for text.

    This is a simple heuristic and not accurate for all tokenizers.
    For precise counts, use the model's actual tokenizer.

    Parameters
    ----------
    text : str
        The text to estimate tokens for

    Returns
    -------
    int
        Estimated token count
    """
    # Rough heuristic: ~4 characters per token for English text
    return len(text) // 4


def truncate_to_token_limit(
    text: str,
    token_limit: int,
    chars_per_token: int = 4
) -> str:
    """Truncate text to fit within a token limit.

    Parameters
    ----------
    text : str
        The text to truncate
    token_limit : int
        Maximum number of tokens
    chars_per_token : int, optional
        Estimated characters per token

    Returns
    -------
    str
        Truncated text
    """
    max_chars = token_limit * chars_per_token
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."


def merge_response_chunks(chunks: List[Any]) -> str:
    """Merge streaming response chunks into a single string.

    Parameters
    ----------
    chunks : list
        List of response chunks

    Returns
    -------
    str
        Merged response text
    """
    content_parts = []
    for chunk in chunks:
        if hasattr(chunk, "content"):
            content_parts.append(chunk.content)
        elif isinstance(chunk, dict) and "content" in chunk:
            content_parts.append(chunk["content"])
        elif isinstance(chunk, str):
            content_parts.append(chunk)
    return "".join(content_parts)


__all__ = [
    "parse_json_response",
    "check_node_health",
    "retry_with_backoff",
    "format_chat_history",
    "estimate_tokens",
    "truncate_to_token_limit",
    "merge_response_chunks",
]
