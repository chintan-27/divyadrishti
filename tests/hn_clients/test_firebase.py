import httpx
import pytest

from libs.hn_clients.firebase import FirebaseHNClient


def _mock_transport(payload: object) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=payload)

    return httpx.MockTransport(handler)


def _error_transport(status: int = 500) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status, text="error")

    return httpx.MockTransport(handler)


@pytest.mark.asyncio
async def test_get_item():
    item = {"id": 1, "type": "story", "title": "Test"}
    transport = _mock_transport(item)
    async with httpx.AsyncClient(transport=transport) as http:
        client = FirebaseHNClient(client=http)
        result = await client.get_item(1)
    assert result == item


def _null_transport() -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="null", headers={"content-type": "application/json"})

    return httpx.MockTransport(handler)


@pytest.mark.asyncio
async def test_get_item_null():
    transport = _null_transport()
    async with httpx.AsyncClient(transport=transport) as http:
        client = FirebaseHNClient(client=http)
        result = await client.get_item(999)
    assert result is None


@pytest.mark.asyncio
async def test_get_top_stories():
    ids = [1, 2, 3]
    transport = _mock_transport(ids)
    async with httpx.AsyncClient(transport=transport) as http:
        client = FirebaseHNClient(client=http)
        result = await client.get_top_stories()
    assert result == ids


@pytest.mark.asyncio
async def test_get_new_stories():
    ids = [10, 11]
    transport = _mock_transport(ids)
    async with httpx.AsyncClient(transport=transport) as http:
        client = FirebaseHNClient(client=http)
        result = await client.get_new_stories()
    assert result == ids


@pytest.mark.asyncio
async def test_get_best_stories():
    ids = [100]
    transport = _mock_transport(ids)
    async with httpx.AsyncClient(transport=transport) as http:
        client = FirebaseHNClient(client=http)
        result = await client.get_best_stories()
    assert result == ids


@pytest.mark.asyncio
async def test_error_raises():
    transport = _error_transport(500)
    async with httpx.AsyncClient(transport=transport) as http:
        client = FirebaseHNClient(client=http)
        with pytest.raises(httpx.HTTPStatusError):
            await client.get_item(1)
