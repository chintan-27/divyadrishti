from __future__ import annotations

import os
import threading

from dotenv import load_dotenv
from openai import OpenAI

_client: OpenAI | None = None
_lock = threading.Lock()
_dotenv_loaded = False


def _ensure_dotenv() -> None:
    global _dotenv_loaded  # noqa: PLW0603
    if not _dotenv_loaded:
        load_dotenv()
        _dotenv_loaded = True


def get_embedding_model() -> str:
    _ensure_dotenv()
    return os.getenv("DD_EMBEDDING_MODEL", "text-embedding-3-large")


def get_opinion_model() -> str:
    _ensure_dotenv()
    return os.getenv("DD_OPINION_MODEL", "llama-3.3-70b-instruct")


def get_labeling_model() -> str:
    _ensure_dotenv()
    return os.getenv("DD_LABELING_MODEL", "llama-3.3-70b-instruct")


def get_client() -> OpenAI:
    """Lazy singleton for the Navigator OpenAI client."""
    global _client  # noqa: PLW0603
    if _client is not None:
        return _client

    with _lock:
        if _client is not None:
            return _client

        _ensure_dotenv()
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        if not api_key or not base_url:
            raise RuntimeError("Need OPENAI_API_KEY and OPENAI_BASE_URL in .env")

        extra_headers = {}
        hdr_name = os.getenv("PROXY_AUTH_HEADER")
        if hdr_name:
            extra_headers[hdr_name] = api_key
            _client = OpenAI(
                api_key="DUMMY", base_url=base_url, default_headers=extra_headers,
            )
        else:
            _client = OpenAI(api_key=api_key, base_url=base_url)
    return _client
