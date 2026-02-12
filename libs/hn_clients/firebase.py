from __future__ import annotations

from typing import Any

import httpx

_BASE_URL = "https://hacker-news.firebaseio.com/v0"


class FirebaseHNClient:
    """Async client for the HN Firebase API."""

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._external = client is not None
        self._client = client or httpx.AsyncClient(timeout=15.0)

    async def __aenter__(self) -> FirebaseHNClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()

    async def close(self) -> None:
        if not self._external:
            await self._client.aclose()

    async def get_item(self, item_id: int) -> dict[str, Any] | None:
        """Fetch a single item by ID. Returns None if the item doesn't exist."""
        resp = await self._client.get(f"{_BASE_URL}/item/{item_id}.json")
        resp.raise_for_status()
        data = resp.json()
        return data if isinstance(data, dict) else None

    async def get_top_stories(self) -> list[int]:
        resp = await self._client.get(f"{_BASE_URL}/topstories.json")
        resp.raise_for_status()
        return resp.json()  # type: ignore[no-any-return]

    async def get_new_stories(self) -> list[int]:
        resp = await self._client.get(f"{_BASE_URL}/newstories.json")
        resp.raise_for_status()
        return resp.json()  # type: ignore[no-any-return]

    async def get_best_stories(self) -> list[int]:
        resp = await self._client.get(f"{_BASE_URL}/beststories.json")
        resp.raise_for_status()
        return resp.json()  # type: ignore[no-any-return]
