from typing import Optional, Dict, Any, List
from PIL import Image, ImageDraw, ImageFont
import httpx
import io
import os
from pathlib import Path
from ..core.config import settings
from ..core.logger import logger


class ImageService:
    """
    Image processing and generation service.
    """

    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.temp_dir = Path(settings.TEMP_DIR)

        # Create directories if they don't exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    async def download_image(
        self,
        url: str,
        save_path: Optional[str] = None
    ) -> str:
        """
        Download image from URL.

        Args:
            url: Image URL
            save_path: Optional save path (auto-generated if not provided)

        Returns:
            Path to downloaded image
        """
        try:
            response = await self.http_client.get(url)
            response.raise_for_status()

            # Determine file extension
            content_type = response.headers.get("content-type", "")
            ext = ".jpg"
            if "png" in content_type:
                ext = ".png"
            elif "webp" in content_type:
                ext = ".webp"

            # Generate save path if not provided
            if not save_path:
                filename = f"image_{int(os.time() * 1000)}{ext}"
                save_path = str(self.temp_dir / filename)

            # Save image
            with open(save_path, "wb") as f:
                f.write(response.content)

            logger.info(f"Image downloaded: {save_path}")
            return save_path

        except Exception as e:
            logger.error(f"Error downloading image: {str(e)}")
            raise

    async def search_cover_image(
        self,
        keywords: str,
        width: int = 1280,
        height: int = 720
    ) -> Optional[str]:
        """
        Search for cover image using multiple sources.

        Args:
            keywords: Search keywords
            width: Desired width
            height: Desired height

        Returns:
            URL of found image or None
        """
        try:
            # Try Pollinations AI first
            image_url = f"https://image.pollinations.ai/prompt/{keywords}?width={width}&height={height}&nologo=true&seed={os.urandom(4).hex()}"

            # Verify image is accessible
            response = await self.http_client.head(image_url)
            if response.status_code == 200:
                logger.info(f"Found image from Pollinations: {image_url}")
                return image_url

            # Fallback to other sources can be added here
            logger.warning("No suitable image found")
            return None

        except Exception as e:
            logger.error(f"Error searching for cover image: {str(e)}")
            return None

    async def process_cover_image(
        self,
        image_path: str,
        target_width: int = None,
        target_height: int = None,
        add_watermark: bool = False,
        watermark_text: str = ""
    ) -> str:
        """
        Process cover image: resize, crop, add watermark.

        Args:
            image_path: Path to source image
            target_width: Target width (default from settings)
            target_height: Target height (default from settings)
            add_watermark: Whether to add watermark
            watermark_text: Watermark text

        Returns:
            Path to processed image
        """
        try:
            target_width = target_width or settings.COVER_IMAGE_WIDTH
            target_height = target_height or settings.COVER_IMAGE_HEIGHT

            # Open image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Calculate aspect ratio
                img_ratio = img.width / img.height
                target_ratio = target_width / target_height

                # Crop to target ratio
                if img_ratio > target_ratio:
                    # Image is wider, crop sides
                    new_width = int(img.height * target_ratio)
                    left = (img.width - new_width) // 2
                    img = img.crop((left, 0, left + new_width, img.height))
                else:
                    # Image is taller, crop top/bottom
                    new_height = int(img.width / target_ratio)
                    top = (img.height - new_height) // 2
                    img = img.crop((0, top, img.width, top + new_height))

                # Resize to target dimensions
                img = img.resize((target_width, target_height), Image.LANCZOS)

                # Add watermark if requested
                if add_watermark and watermark_text:
                    img = self._add_watermark(img, watermark_text)

                # Save processed image
                output_path = str(self.upload_dir / f"cover_{int(os.time() * 1000)}.jpg")
                img.save(output_path, 'JPEG', quality=90, optimize=True)

                logger.info(f"Cover image processed: {output_path}")
                return output_path

        except Exception as e:
            logger.error(f"Error processing cover image: {str(e)}")
            raise

    def _add_watermark(
        self,
        image: Image.Image,
        text: str,
        position: str = "bottom-right",
        opacity: int = 128
    ) -> Image.Image:
        """
        Add watermark to image.

        Args:
            image: PIL Image object
            text: Watermark text
            position: Watermark position
            opacity: Opacity (0-255)

        Returns:
            Image with watermark
        """
        try:
            # Create a transparent overlay
            overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)

            # Try to use a system font
            try:
                font = ImageFont.truetype("arial.ttf", 36)
            except:
                font = ImageFont.load_default()

            # Calculate text size
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # Calculate position
            padding = 20
            if position == "bottom-right":
                x = image.width - text_width - padding
                y = image.height - text_height - padding
            elif position == "bottom-left":
                x = padding
                y = image.height - text_height - padding
            elif position == "top-right":
                x = image.width - text_width - padding
                y = padding
            else:  # top-left
                x = padding
                y = padding

            # Draw text with opacity
            draw.text((x, y), text, font=font, fill=(255, 255, 255, opacity))

            # Composite overlay onto image
            watermarked = Image.alpha_composite(image.convert('RGBA'), overlay)

            return watermarked.convert('RGB')

        except Exception as e:
            logger.error(f"Error adding watermark: {str(e)}")
            return image

    async def generate_technical_diagram(
        self,
        concepts: List[str],
        style: str = "modern"
    ) -> str:
        """
        Generate a technical diagram based on concepts.

        Args:
            concepts: List of concepts to visualize
            style: Diagram style (modern, minimal, colorful)

        Returns:
            Path to generated diagram
        """
        try:
            # Create a blank canvas
            width, height = 1280, 720
            img = Image.new('RGB', (width, height), color='#1a1a2e')
            draw = ImageDraw.Draw(img)

            # Define colors based on style
            colors = {
                "modern": ['#16213e', '#0f3460', '#e94560', '#533483'],
                "minimal": ['#ffffff', '#000000', '#808080'],
                "colorful": ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']
            }

            palette = colors.get(style, colors["modern"])

            # Draw background gradient (simplified)
            for i in range(height):
                r = int(palette[0][1:3], 16) + int(palette[1][1:3], 16) * i // height
                g = int(palette[0][3:5], 16) + int(palette[1][3:5], 16) * i // height
                b = int(palette[0][5:7], 16) + int(palette[1][5:7], 16) * i // height
                draw.line([(0, i), (width, i)], fill=f'#{r:02x}{g:02x}{b:02x}')

            # Draw concept boxes
            box_width = 300
            box_height = 150
            gap = 50
            start_x = (width - (len(concepts) * (box_width + gap))) // 2 + gap // 2
            start_y = (height - box_height) // 2

            try:
                font = ImageFont.truetype("arial.ttf", 24)
                title_font = ImageFont.truetype("arial.ttf", 32)
            except:
                font = ImageFont.load_default()
                title_font = ImageFont.load_default()

            for i, concept in enumerate(concepts[:4]):  # Max 4 concepts
                x = start_x + i * (box_width + gap)
                y = start_y

                # Draw box
                color = palette[(i + 2) % len(palette)]
                draw.rectangle([x, y, x + box_width, y + box_height],
                             fill=color, outline='white', width=3)

                # Draw text
                text = concept[:20] + "..." if len(concept) > 20 else concept
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_x = x + (box_width - text_width) // 2
                text_y = y + (box_height - bbox[3] + bbox[1]) // 2

                draw.text((text_x, text_y), text, font=font, fill='white')

            # Draw title
            title = "技术概念图"
            bbox = draw.textbbox((0, 0), title, font=title_font)
            title_x = (width - (bbox[2] - bbox[0])) // 2
            draw.text((title_x, 50), title, font=title_font, fill='white')

            # Save diagram
            output_path = str(self.upload_dir / f"diagram_{int(os.time() * 1000)}.jpg")
            img.save(output_path, 'JPEG', quality=90)

            logger.info(f"Technical diagram generated: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Error generating technical diagram: {str(e)}")
            raise

    def validate_image(
        self,
        image_path: str,
        min_width: int = None,
        min_height: int = None
    ) -> Dict[str, Any]:
        """
        Validate image dimensions and quality.

        Args:
            image_path: Path to image
            min_width: Minimum width (default from settings)
            min_height: Minimum height (default from settings)

        Returns:
            Dict with validation results
        """
        try:
            min_width = min_width or settings.COVER_IMAGE_MIN_WIDTH
            min_height = min_height or settings.COVER_IMAGE_MIN_HEIGHT

            with Image.open(image_path) as img:
                width, height = img.size
                size = os.path.getsize(image_path)

                result = {
                    "valid": True,
                    "width": width,
                    "height": height,
                    "size": size,
                    "size_mb": size / (1024 * 1024),
                    "errors": []
                }

                # Check dimensions
                if width < min_width:
                    result["valid"] = False
                    result["errors"].append(f"Width {width} < minimum {min_width}")

                if height < min_height:
                    result["valid"] = False
                    result["errors"].append(f"Height {height} < minimum {min_height}")

                # Check file size
                if size > settings.IMAGE_MAX_SIZE:
                    result["valid"] = False
                    result["errors"].append(f"File size {size} > maximum {settings.IMAGE_MAX_SIZE}")

                return result

        except Exception as e:
            logger.error(f"Error validating image: {str(e)}")
            return {
                "valid": False,
                "errors": [str(e)]
            }

    async def close(self):
        """Close HTTP client."""
        await self.http_client.aclose()


# Global instance
image_service = ImageService()