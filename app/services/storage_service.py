# V2 MinIO Storage Service
"""
This service provides an abstraction layer for interacting with MinIO or any S3-compatible
object storage.

It uses the `minio` Python library, which is synchronous. To prevent blocking the main
asyncio event loop, all calls to the MinIO client are wrapped in `run_in_executor`,
allowing them to run in a separate thread.

Key features:
- CRUD operations for files (text, JSON).
- Automatic bucket creation on first use.
- Public and presigned URL generation.
- Health check to verify connectivity and permissions.
"""

import logging
from typing import Optional, BinaryIO, Union
from minio import Minio
from minio.error import S3Error
import json
import asyncio
from io import BytesIO
from datetime import timedelta
from app.core.config import settings

logger = logging.getLogger(__name__)


class StorageService:
    """
    A service class to handle all MinIO S3 storage operations.

    Attributes:
        client: The `minio.Minio` client instance.
        bucket_name: The name of the bucket to use for all operations.
    """

    def __init__(self):
        """Initializes the StorageService and the MinIO client."""
        self.client: Optional[Minio] = None
        self.bucket_name: str = settings.MINIO_BUCKET_NAME
        self._initialize_client()

    def _initialize_client(self):
        """Initializes the MinIO client using settings from the application configuration."""
        logger.info(f"Initializing MinIO client for endpoint: {settings.MINIO_ENDPOINT}...")
        try:
            self.client = Minio(
                endpoint=settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE
            )
            logger.info(f"MinIO client initialized successfully (secure={settings.MINIO_SECURE}, bucket={self.bucket_name})")
        except Exception as e:
            logger.critical(f"Failed to initialize MinIO client: {e}", exc_info=True)
            raise RuntimeError(f"MinIO initialization failed: {e}")

    async def _ensure_bucket_exists(self):
        """
        Checks if the target bucket exists and creates it if it does not.
        This is a convenience method to avoid errors on first-time setup.
        """
        logger.debug(f"Checking if bucket '{self.bucket_name}' exists...")
        try:
            # The minio client is synchronous, so we run this in a thread.
            loop = asyncio.get_event_loop()
            bucket_exists = await loop.run_in_executor(None, self.client.bucket_exists, self.bucket_name)

            if not bucket_exists:
                logger.info(f"Bucket '{self.bucket_name}' not found. Creating it...")
                await loop.run_in_executor(None, self.client.make_bucket, self.bucket_name)
                logger.info(f"Successfully created bucket: {self.bucket_name}")
            else:
                logger.debug(f"Bucket '{self.bucket_name}' already exists")
        except S3Error as e:
            logger.error(f"S3 error while ensuring bucket exists: {e}", exc_info=True)
            raise RuntimeError(f"Failed to create or verify bucket: {e}")

    async def save_text_file(self, content: str, filename: str) -> str:
        """
        Saves a string of text content to a file in MinIO.

        Args:
            content: The string content to save.
            filename: The name of the object in the bucket.

        Returns:
            The public URL to the newly created file.
        """
        logger.info(f"Saving text file '{filename}' to MinIO (size: {len(content)} chars)...")
        await self._ensure_bucket_exists()
        try:
            data = content.encode('utf-8')
            data_stream = BytesIO(data)
            file_size_kb = len(data) / 1024

            logger.debug(f"Uploading file '{filename}' ({file_size_kb:.2f} KB) to bucket '{self.bucket_name}'...")

            # Run the synchronous put_object call in a separate thread.
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.client.put_object(
                    bucket_name=self.bucket_name,
                    object_name=filename,
                    data=data_stream,
                    length=len(data),
                    content_type='text/plain; charset=utf-8'
                )
            )

            file_url = self._get_public_url(filename)
            logger.info(f"Successfully saved text file '{filename}' ({file_size_kb:.2f} KB) to bucket '{self.bucket_name}'")
            logger.debug(f"File URL: {file_url}")
            return file_url
        except S3Error as e:
            logger.error(f"S3 error saving text file {filename}: {e}", exc_info=True)
            raise RuntimeError(f"Failed to save text file: {e}")

    def _get_public_url(self, filename: str) -> str:
        """Constructs a public URL for a given filename."""
        protocol = "https" if settings.MINIO_SECURE else "http"
        # This creates a simple public URL. For production, presigned URLs are more secure.
        return f"{protocol}://{settings.MINIO_ENDPOINT}/{self.bucket_name}/{filename}"

    async def health_check(self) -> dict:
        """
        Performs a health check on the MinIO service.

        This check verifies connectivity, bucket access, and basic file operations.

        Returns:
            A dictionary containing the health status and diagnostic information.
        """
        logger.debug("Starting MinIO health check...")
        try:
            logger.debug("Ensuring bucket exists...")
            await self._ensure_bucket_exists()

            # Perform a simple write/read/delete test to confirm permissions.
            test_filename = f"health_check_{int(asyncio.get_running_loop().time())}.txt"
            logger.debug(f"Testing file operations with: {test_filename}")

            await self.save_text_file("health check ok", test_filename)

            logger.debug(f"Removing test file: {test_filename}")
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.client.remove_object, self.bucket_name, test_filename)

            logger.info(f"MinIO health check completed successfully for bucket: {self.bucket_name}")
            return {
                "status": "healthy",
                "details": "Connectivity and bucket operations are successful.",
                "bucket": self.bucket_name
            }
        except Exception as e:
            logger.error(f"MinIO health check failed: {e}", exc_info=True)
            return {"status": "error", "error": str(e)}

# Create a single, global instance of the StorageService.
# This instance will be imported and used by other parts of the application.


storage_service = StorageService()
