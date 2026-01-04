from typing import Optional, Dict, Any, List
import boto3
from botocore.client import Config
from pathlib import Path
import os
from ..core.config import settings
from ..core.logger import logger


class ImageBedService:
    """
    Image bed service supporting multiple S3-compatible storage providers.
    """

    def __init__(
        self,
        provider: str = "r2",
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        bucket_name: Optional[str] = None,
        endpoint_url: Optional[str] = None,
        custom_domain: Optional[str] = None,
        base_path: str = ""
    ):
        self.provider = provider
        self.access_key_id = access_key_id or settings.IMAGE_BED_ACCESS_KEY_ID
        self.secret_access_key = secret_access_key or settings.IMAGE_BED_SECRET_ACCESS_KEY
        self.bucket_name = bucket_name or settings.IMAGE_BED_BUCKET_NAME
        self.endpoint_url = endpoint_url or settings.IMAGE_BED_ENDPOINT_URL
        self.custom_domain = custom_domain or settings.IMAGE_BED_CUSTOM_DOMAIN
        self.base_path = base_path or settings.IMAGE_BED_BASE_PATH

        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            endpoint_url=self.endpoint_url,
            config=Config(signature_version='s3v4')
        )

    async def upload_image(
        self,
        file_path: str,
        filename: Optional[str] = None,
        content_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """
        Upload image to image bed.

        Args:
            file_path: Path to image file
            filename: Optional custom filename
            content_type: Content type of the image

        Returns:
            Dict with url, filename, and other metadata
        """
        try:
            # Generate filename if not provided
            if not filename:
                filename = f"{int(os.time() * 1000)}_{os.path.basename(file_path)}"

            # Add base path if configured
            key = f"{self.base_path}/{filename}" if self.base_path else filename

            # Upload to S3
            self.s3_client.upload_file(
                file_path,
                self.bucket_name,
                key,
                ExtraArgs={
                    'ContentType': content_type,
                    'CacheControl': 'public, max-age=31536000'
                }
            )

            # Generate URL
            if self.custom_domain:
                url = f"{self.custom_domain}/{key}"
            else:
                url = f"{self.endpoint_url}/{self.bucket_name}/{key}"

            logger.info(f"Image uploaded to {self.provider}: {url}")

            return {
                "url": url,
                "filename": filename,
                "key": key,
                "provider": self.provider,
                "bucket": self.bucket_name
            }

        except Exception as e:
            logger.error(f"Error uploading image to {self.provider}: {str(e)}")
            raise

    async def upload_image_from_bytes(
        self,
        image_bytes: bytes,
        filename: str,
        content_type: str = "image/jpeg"
    ) -> Dict[str, Any]:
        """
        Upload image from bytes.

        Args:
            image_bytes: Image data as bytes
            filename: Filename for the image
            content_type: Content type of the image

        Returns:
            Dict with url, filename, and other metadata
        """
        try:
            # Add base path if configured
            key = f"{self.base_path}/{filename}" if self.base_path else filename

            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=image_bytes,
                ContentType=content_type,
                CacheControl='public, max-age=31536000'
            )

            # Generate URL
            if self.custom_domain:
                url = f"{self.custom_domain}/{key}"
            else:
                url = f"{self.endpoint_url}/{self.bucket_name}/{key}"

            logger.info(f"Image uploaded to {self.provider}: {url}")

            return {
                "url": url,
                "filename": filename,
                "key": key,
                "provider": self.provider,
                "bucket": self.bucket_name
            }

        except Exception as e:
            logger.error(f"Error uploading image to {self.provider}: {str(e)}")
            raise

    async def delete_image(self, key: str) -> bool:
        """
        Delete image from image bed.

        Args:
            key: Image key in the bucket

        Returns:
            True if deleted successfully
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )

            logger.info(f"Image deleted from {self.provider}: {key}")
            return True

        except Exception as e:
            logger.error(f"Error deleting image from {self.provider}: {str(e)}")
            return False

    async def list_images(
        self,
        prefix: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List images in the bucket.

        Args:
            prefix: Optional prefix to filter
            limit: Maximum number of images to return

        Returns:
            List of image metadata
        """
        try:
            # Add base path to prefix
            full_prefix = f"{self.base_path}/{prefix}" if prefix and self.base_path else (prefix or self.base_path)

            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=full_prefix,
                MaxKeys=limit
            )

            images = []
            for obj in response.get('Contents', []):
                # Generate URL
                key = obj['Key']
                if self.custom_domain:
                    url = f"{self.custom_domain}/{key}"
                else:
                    url = f"{self.endpoint_url}/{self.bucket_name}/{key}"

                images.append({
                    "key": key,
                    "filename": os.path.basename(key),
                    "url": url,
                    "size": obj['Size'],
                    "last_modified": obj['LastModified']
                })

            return images

        except Exception as e:
            logger.error(f"Error listing images from {self.provider}: {str(e)}")
            return []

    async def get_image_url(self, key: str, expires_in: int = 3600) -> str:
        """
        Get a presigned URL for an image.

        Args:
            key: Image key in the bucket
            expires_in: URL expiration time in seconds

        Returns:
            Presigned URL
        """
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': key
                },
                ExpiresIn=expires_in
            )

            return url

        except Exception as e:
            logger.error(f"Error generating presigned URL: {str(e)}")
            raise

    async def batch_upload(
        self,
        file_paths: List[str],
        progress_callback: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Upload multiple images in batch.

        Args:
            file_paths: List of file paths to upload
            progress_callback: Optional callback for progress updates

        Returns:
            List of upload results
        """
        results = []

        for index, file_path in enumerate(file_paths):
            try:
                result = await self.upload_image(file_path)
                results.append({
                    "file_path": file_path,
                    "success": True,
                    "result": result
                })

                if progress_callback:
                    progress_callback(index + 1, len(file_paths))

            except Exception as e:
                results.append({
                    "file_path": file_path,
                    "success": False,
                    "error": str(e)
                })

                if progress_callback:
                    progress_callback(index + 1, len(file_paths))

        return results

    def test_connection(self) -> bool:
        """
        Test connection to the image bed.

        Returns:
            True if connection successful
        """
        try:
            # Try to list buckets
            self.s3_client.list_buckets()
            logger.info(f"Successfully connected to {self.provider}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to {self.provider}: {str(e)}")
            return False


# Factory function to create image bed service
def create_image_bed_service(
    provider: str = "r2",
    **kwargs
) -> ImageBedService:
    """
    Create an image bed service instance.

    Args:
        provider: Provider name (r2, oss, cos)
        **kwargs: Additional configuration

    Returns:
        ImageBedService instance
    """
    # Default endpoints for different providers
    default_endpoints = {
        "r2": "https://<account-id>.r2.cloudflarestorage.com",
        "oss": "https://oss-cn-hangzhou.aliyuncs.com",
        "cos": "https://cos.ap-guangzhou.myqcloud.com"
    }

    if provider not in default_endpoints:
        raise ValueError(f"Unsupported provider: {provider}")

    return ImageBedService(provider=provider, **kwargs)


# Global instance (will be initialized with config)
image_bed_service: Optional[ImageBedService] = None


def get_image_bed_service() -> ImageBedService:
    """Get or create global image bed service instance."""
    global image_bed_service

    if image_bed_service is None:
        image_bed_service = create_image_bed_service(
            provider=settings.IMAGE_BED_PROVIDER,
            access_key_id=settings.IMAGE_BED_ACCESS_KEY_ID,
            secret_access_key=settings.IMAGE_BED_SECRET_ACCESS_KEY,
            bucket_name=settings.IMAGE_BED_BUCKET_NAME,
            endpoint_url=settings.IMAGE_BED_ENDPOINT_URL,
            custom_domain=settings.IMAGE_BED_CUSTOM_DOMAIN,
            base_path=settings.IMAGE_BED_BASE_PATH
        )

    return image_bed_service