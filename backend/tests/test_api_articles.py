import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_create_article(client: AsyncClient, db: AsyncSession):
    """Test creating a new article."""
    response = await client.post(
        "/api/articles/",
        json={
            "topic": "测试主题",
            "style": "professional",
            "length": "short",
            "enable_research": False,
            "generate_cover": False,
            "ai_model": "gpt-4"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["title"] is not None
    assert data["content"] is not None


@pytest.mark.asyncio
async def test_list_articles(client: AsyncClient):
    """Test listing articles."""
    response = await client.get("/api/articles/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_article(client: AsyncClient, db: AsyncSession):
    """Test getting a specific article."""
    # First create an article
    create_response = await client.post(
        "/api/articles/",
        json={
            "topic": "测试主题",
            "style": "professional",
            "length": "short",
            "enable_research": False,
            "generate_cover": False
        }
    )
    article_id = create_response.json()["id"]

    # Then get it
    response = await client.get(f"/api/articles/{article_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == article_id


@pytest.mark.asyncio
async def test_generate_titles(client: AsyncClient):
    """Test generating article titles."""
    response = await client.post(
        "/api/articles/titles/generate",
        json={
            "topic": "AI技术突破",
            "count": 5
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 5
    assert "title" in data[0]
    assert "predicted_click_rate" in data[0]


@pytest.mark.asyncio
async def test_generate_content(client: AsyncClient):
    """Test generating article content."""
    response = await client.post(
        "/api/articles/content/generate",
        json={
            "topic": "AI技术突破",
            "title": "AI技术重大突破：改变未来的力量",
            "style": "professional",
            "length": "short",
            "enable_research": False
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert "summary" in data
    assert "tags" in data


@pytest.mark.asyncio
async def test_delete_article(client: AsyncClient, db: AsyncSession):
    """Test deleting an article."""
    # First create an article
    create_response = await client.post(
        "/api/articles/",
        json={
            "topic": "测试主题",
            "style": "professional",
            "length": "short",
            "enable_research": False,
            "generate_cover": False
        }
    )
    article_id = create_response.json()["id"]

    # Then delete it
    response = await client.delete(f"/api/articles/{article_id}")

    assert response.status_code == 200

    # Verify it's deleted
    get_response = await client.get(f"/api/articles/{article_id}")
    assert get_response.status_code == 404