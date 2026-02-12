from __future__ import annotations

from typing import Any

import httpx

_BASE_URL = "https://hn.algolia.com/api/v1"


class AlgoliaHNClient:
    """Async client for the Algolia HN Search API."""

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._external = client is not None
        self._client = client or httpx.AsyncClient(timeout=15.0)

    async def __aenter__(self) -> AlgoliaHNClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()

    async def close(self) -> None:
        if not self._external:
            await self._client.aclose()

    async def search_front_page(self, hits_per_page: int = 30) -> list[dict[str, Any]]:
        """Fetch current front page stories."""
        resp = await self._client.get(
            f"{_BASE_URL}/search",
            params={"tags": "front_page", "hitsPerPage": hits_per_page},
        )
        resp.raise_for_status()
        return resp.json()["hits"]  # type: ignore[no-any-return]

    async def search_by_date(
        self,
        tags: str = "story",
        hits_per_page: int = 30,
        numeric_filters: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search items sorted by date."""
        params: dict[str, str | int] = {
            "tags": tags,
            "hitsPerPage": hits_per_page,
        }
        if numeric_filters:
            params["numericFilters"] = numeric_filters
        resp = await self._client.get(f"{_BASE_URL}/search_by_date", params=params)
        resp.raise_for_status()
        return resp.json()["hits"]  # type: ignore[no-any-return]

    async def search_query(
        self, query: str, tags: str = "story", hits_per_page: int = 30
    ) -> list[dict[str, Any]]:
        """Full-text search."""
        resp = await self._client.get(
            f"{_BASE_URL}/search",
            params={"query": query, "tags": tags, "hitsPerPage": hits_per_page},
        )
        resp.raise_for_status()
        return resp.json()["hits"]  # type: ignore[no-any-return]
