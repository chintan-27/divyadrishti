import httpx
import pytest

from libs.hn_clients.algolia import AlgoliaHNClient


def _mock_transport(payload: dict) -> httpx.MockTransport:  # type: ignore[type-arg]
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)

    return httpx.MockTransport(handler)


def _error_transport(status: int = 500) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, json={"error": "fail"})

    return httpx.MockTransport(handler)


@pytest.mark.asyncio
async def test_search_front_page():
    hits = [{"objectID": "1", "title": "Test"}]
    transport = _mock_transport({"hits": hits})
    async with httpx.AsyncClient(transport=transport) as http:
        client = AlgoliaHNClient(client=http)
        result = await client.search_front_page()
    assert result == hits


@pytest.mark.asyncio
async def test_search_by_date():
    hits = [{"objectID": "2"}]
    transport = _mock_transport({"hits": hits})
    async with httpx.AsyncClient(transport=transport) as http:
        client = AlgoliaHNClient(client=http)
        result = await client.search_by_date(tags="comment", numeric_filters="created_at_i>1000")
    assert result == hits


@pytest.mark.asyncio
async def test_search_query():
    hits = [{"objectID": "3", "title": "Rust"}]
    transport = _mock_transport({"hits": hits})
    async with httpx.AsyncClient(transport=transport) as http:
        client = AlgoliaHNClient(client=http)
        result = await client.search_query("Rust")
    assert result == hits


@pytest.mark.asyncio
async def test_error_raises():
    transport = _error_transport(500)
    async with httpx.AsyncClient(transport=transport) as http:
        client = AlgoliaHNClient(client=http)
        with pytest.raises(httpx.HTTPStatusError):
            await client.search_front_page()


@pytest.mark.asyncio
async def test_context_manager_closes_own_client():
    transport = _mock_transport({"hits": []})
    async with AlgoliaHNClient(client=httpx.AsyncClient(transport=transport)) as client:
        result = await client.search_front_page()
    assert result == []
