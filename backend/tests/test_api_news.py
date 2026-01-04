import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_fetch_news(client: AsyncClient):
    """Test fetching news from a source."""
    response = await client.post(
        "/api/news/fetch",
        json={
            "source": "ithome",
            "limit": 10
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_fetch_all_news(client: AsyncClient):
    """Test fetching news from all sources."""
    response = await client.post("/api/news/fetch/all?limit_per_source=20")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_list_news(client: AsyncClient):
    """Test listing news items."""
    response = await client.get("/api/news/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_hot_news(client: AsyncClient):
    """Test getting hottest news."""
    response = await client.get("/api/news/hot?limit=10")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 10


@pytest.mark.asyncio
async def test_get_news_item(client: AsyncClient, db: AsyncSession):
    """Test getting a specific news item."""
    # First fetch some news
    fetch_response = await client.post(
        "/api/news/fetch",
        json={
            "source": "ithome",
            "limit": 5
        }
    )

    if fetch_response.status_code == 200 and len(fetch_response.json()) > 0:
        news_id = fetch_response.json()[0]["id"]

        # Then get it
        response = await client.get(f"/api/news/{news_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == news_id