import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_overview_stats(client: AsyncClient):
    """Test getting overview statistics."""
    response = await client.get("/api/statistics/overview?days=30")

    assert response.status_code == 200
    data = response.json()
    assert "total_articles" in data
    assert "published_articles" in data
    assert "total_reads" in data
    assert "total_likes" in data
    assert "success_rate" in data


@pytest.mark.asyncio
async def test_get_daily_stats(client: AsyncClient):
    """Test getting daily statistics."""
    response = await client.get("/api/statistics/daily?days=7")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 7
    assert "date" in data[0]
    assert "articles" in data[0]
    assert "reads" in data[0]


@pytest.mark.asyncio
async def test_get_top_articles(client: AsyncClient):
    """Test getting top performing articles."""
    response = await client.get("/api/statistics/top-articles?limit=10")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 10
    if len(data) > 0:
        assert "title" in data[0]
        assert "read_count" in data[0]
        assert "like_count" in data[0]


@pytest.mark.asyncio
async def test_get_source_stats(client: AsyncClient):
    """Test getting statistics by source."""
    response = await client.get("/api/statistics/sources")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "source" in data[0]
        assert "count" in data[0]
        assert "percentage" in data[0]


@pytest.mark.asyncio
async def test_get_trends(client: AsyncClient):
    """Test getting trend analysis."""
    response = await client.get("/api/statistics/trends?days=30")

    assert response.status_code == 200
    data = response.json()
    assert "article_trends" in data
    assert "quality_trends" in data
    assert isinstance(data["article_trends"], list)
    assert isinstance(data["quality_trends"], list)


@pytest.mark.asyncio
async def test_get_performance_stats(client: AsyncClient):
    """Test getting performance statistics."""
    response = await client.get("/api/statistics/performance")

    assert response.status_code == 200
    data = response.json()
    assert "quality" in data
    assert "click_through_rate" in data
    assert "average" in data["quality"]
    assert "max" in data["quality"]