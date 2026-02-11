"""
Unit tests for Image Service.
"""
import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from pathlib import Path
from PIL import Image
import io
from app.services.image_generation_service import ImageGenerationService


@pytest.fixture
def image_service(tmp_path):
    """Create image service instance for testing."""
    with patch('app.services.image_service.settings') as mock_settings:
        mock_settings.UPLOAD_DIR = str(tmp_path / "uploads")
        mock_settings.TEMP_DIR = str(tmp_path / "temp")
        mock_settings.COVER_IMAGE_WIDTH = 1280
        mock_settings.COVER_IMAGE_HEIGHT = 720
        mock_settings.COVER_IMAGE_MIN_WIDTH = 800
        mock_settings.COVER_IMAGE_MIN_HEIGHT = 600
        mock_settings.IMAGE_MAX_SIZE = 10 * 1024 * 1024  # 10MB

        service = ImageGenerationService()
        yield service


@pytest.fixture
def mock_image_response():
    """Mock HTTP image response."""
    mock_response = Mock()
    mock_response.headers = {"content-type": "image/jpeg"}
    mock_response.content = b"fake image data"
    mock_response.raise_for_status = Mock()
    return mock_response


@pytest.fixture
def sample_image(tmp_path):
    """Create a sample test image."""
    img = Image.new('RGB', (1000, 800), color='red')
    img_path = tmp_path / "sample.jpg"
    img.save(img_path, 'JPEG')
    return str(img_path)


class TestImageService:
    """Test cases for ImageGenerationService."""

    def test_initialization(self, image_service):
        """Test service initialization."""
        assert image_service.http_client is not None
        assert image_service.upload_dir.exists()
        assert image_service.temp_dir.exists()

    @pytest.mark.asyncio
    async def test_download_image_jpeg(self, image_service, mock_image_response):
        """Test downloading JPEG image."""
        image_service.http_client.get = AsyncMock(return_value=mock_image_response)

        result = await image_service.download_image("https://example.com/image.jpg")

        assert Path(result).exists()
        assert result.endswith(".jpg")

    @pytest.mark.asyncio
    async def test_download_image_png(self, image_service):
        """Test downloading PNG image."""
        mock_response = Mock()
        mock_response.headers = {"content-type": "image/png"}
        mock_response.content = b"fake png data"
        mock_response.raise_for_status = Mock()

        image_service.http_client.get = AsyncMock(return_value=mock_response)

        result = await image_service.download_image("https://example.com/image.png")

        assert result.endswith(".png")

    @pytest.mark.asyncio
    async def test_download_image_with_custom_path(self, image_service, mock_image_response, tmp_path):
        """Test downloading image with custom save path."""
        custom_path = str(tmp_path / "custom.jpg")
        image_service.http_client.get = AsyncMock(return_value=mock_image_response)

        result = await image_service.download_image("https://example.com/image.jpg", save_path=custom_path)

        assert result == custom_path
        assert Path(custom_path).exists()

    @pytest.mark.asyncio
    async def test_download_image_on_error(self, image_service):
        """Test error handling in download_image."""
        image_service.http_client.get = AsyncMock(side_effect=Exception("Network error"))

        with pytest.raises(Exception, match="Network error"):
            await image_service.download_image("https://example.com/image.jpg")

    @pytest.mark.asyncio
    async def test_search_cover_image_success(self, image_service):
        """Test successful cover image search."""
        mock_response = Mock()
        mock_response.status_code = 200
        image_service.http_client.head = AsyncMock(return_value=mock_response)

        result = await image_service.search_cover_image("AI technology")

        assert result is not None
        assert "pollinations.ai" in result

    @pytest.mark.asyncio
    async def test_search_cover_image_failure(self, image_service):
        """Test cover image search failure."""
        mock_response = Mock()
        mock_response.status_code = 404
        image_service.http_client.head = AsyncMock(return_value=mock_response)

        result = await image_service.search_cover_image("AI technology")

        assert result is None

    @pytest.mark.asyncio
    async def test_search_cover_image_with_custom_dimensions(self, image_service):
        """Test searching cover image with custom dimensions."""
        mock_response = Mock()
        mock_response.status_code = 200
        image_service.http_client.head = AsyncMock(return_value=mock_response)

        result = await image_service.search_cover_image("AI", width=1920, height=1080)

        assert result is not None
        assert "width=1920" in result
        assert "height=1080" in result

    @pytest.mark.asyncio
    async def test_process_cover_image_resize(self, image_service, sample_image):
        """Test processing cover image with resize."""
        result = await image_service.process_cover_image(sample_image)

        assert Path(result).exists()
        assert result.endswith(".jpg")

        # Verify dimensions
        with Image.open(result) as img:
            assert img.width == 1280
            assert img.height == 720

    @pytest.mark.asyncio
    async def test_process_cover_image_with_watermark(self, image_service, sample_image):
        """Test processing cover image with watermark."""
        result = await image_service.process_cover_image(
            sample_image,
            add_watermark=True,
            watermark_text="Test Watermark"
        )

        assert Path(result).exists()

    @pytest.mark.asyncio
    async def test_process_cover_image_custom_dimensions(self, image_service, sample_image):
        """Test processing with custom dimensions."""
        result = await image_service.process_cover_image(
            sample_image,
            target_width=800,
            target_height=600
        )

        with Image.open(result) as img:
            assert img.width == 800
            assert img.height == 600

    @pytest.mark.asyncio
    async def test_process_cover_image_wider_aspect_ratio(self, image_service, tmp_path):
        """Test processing image wider than target ratio."""
        # Create wide image
        img = Image.new('RGB', (2000, 500), color='blue')
        img_path = tmp_path / "wide.jpg"
        img.save(img_path, 'JPEG')

        result = await image_service.process_cover_image(str(img_path))

        with Image.open(result) as processed:
            assert processed.width == 1280
            assert processed.height == 720

    @pytest.mark.asyncio
    async def test_process_cover_image_taller_aspect_ratio(self, image_service, tmp_path):
        """Test processing image taller than target ratio."""
        # Create tall image
        img = Image.new('RGB', (500, 2000), color='green')
        img_path = tmp_path / "tall.jpg"
        img.save(img_path, 'JPEG')

        result = await image_service.process_cover_image(str(img_path))

        with Image.open(result) as processed:
            assert processed.width == 1280
            assert processed.height == 720

    def test_add_watermark_bottom_right(self, image_service, sample_image):
        """Test adding watermark at bottom-right position."""
        with Image.open(sample_image) as img:
            result = image_service._add_watermark(img, "Test", position="bottom-right")

            assert result.size == img.size

    def test_add_watermark_bottom_left(self, image_service, sample_image):
        """Test adding watermark at bottom-left position."""
        with Image.open(sample_image) as img:
            result = image_service._add_watermark(img, "Test", position="bottom-left")

            assert result.size == img.size

    def test_add_watermark_with_opacity(self, image_service, sample_image):
        """Test adding watermark with custom opacity."""
        with Image.open(sample_image) as img:
            result = image_service._add_watermark(img, "Test", opacity=50)

            assert result.size == img.size

    def test_add_watermark_on_error(self, image_service):
        """Test watermark addition error handling."""
        # Create invalid image
        img = Mock()
        img.size = (100, 100)
        img.convert = Mock(side_effect=Exception("Error"))

        result = image_service._add_watermark(img, "Test")

        # Should return original image on error
        assert result == img

    @pytest.mark.asyncio
    async def test_generate_technical_diagram_modern(self, image_service):
        """Test generating technical diagram with modern style."""
        result = await image_service.generate_technical_diagram(
            ["Concept1", "Concept2"],
            style="modern"
        )

        assert Path(result).exists()
        assert result.endswith(".jpg")

        # Verify image was created
        with Image.open(result) as img:
            assert img.width == 1280
            assert img.height == 720

    @pytest.mark.asyncio
    async def test_generate_technical_diagram_minimal(self, image_service):
        """Test generating technical diagram with minimal style."""
        result = await image_service.generate_technical_diagram(
            ["AI", "ML"],
            style="minimal"
        )

        assert Path(result).exists()

    @pytest.mark.asyncio
    async def test_generate_technical_diagram_max_concepts(self, image_service):
        """Test generating diagram with maximum concepts."""
        result = await image_service.generate_technical_diagram(
            ["AI", "ML", "DL", "NLP", "CV"],  # 5 concepts, should limit to 4
            style="colorful"
        )

        assert Path(result).exists()

    def test_validate_image_valid(self, image_service, sample_image):
        """Test validating a valid image."""
        result = image_service.validate_image(sample_image)

        assert result["valid"] is True
        assert result["width"] == 1000
        assert result["height"] == 800
        assert "errors" in result
        assert len(result["errors"]) == 0

    def test_validate_image_too_small(self, image_service, tmp_path):
        """Test validating an image that's too small."""
        # Create small image
        img = Image.new('RGB', (100, 100), color='red')
        img_path = tmp_path / "small.jpg"
        img.save(img_path, 'JPEG')

        result = image_service.validate_image(str(img_path))

        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_validate_image_custom_min_dimensions(self, image_service, sample_image):
        """Test validation with custom minimum dimensions."""
        result = image_service.validate_image(
            sample_image,
            min_width=2000,
            min_height=2000
        )

        assert result["valid"] is False
        assert any("Width" in error for error in result["errors"])

    def test_validate_image_invalid_file(self, image_service, tmp_path):
        """Test validating a non-image file."""
        # Create text file
        text_path = tmp_path / "not_image.txt"
        text_path.write_text("Not an image")

        result = image_service.validate_image(str(text_path))

        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_validate_image_returns_size_info(self, image_service, sample_image):
        """Test that validation returns size information."""
        result = image_service.validate_image(sample_image)

        assert "size" in result
        assert "size_mb" in result
        assert result["size_mb"] > 0

    @pytest.mark.asyncio
    async def test_close(self, image_service):
        """Test closing the service."""
        image_service.http_client.aclose = AsyncMock()

        await image_service.close()

        image_service.http_client.aclose.assert_called_once()