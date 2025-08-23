# V2 MinIO Storage Service
import logging
from typing import Optional, BinaryIO, Union
from minio import Minio
from minio.error import S3Error
import json
import asyncio
from datetime import datetime, timedelta
from app.core.config import settings

logger = logging.getLogger(__name__)

class StorageService:
    """MinIO S3-compatible storage service for V2 POC"""
    
    def __init__(self):
        self.client = None
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize MinIO client"""
        try:
            self.client = Minio(
                endpoint=settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE
            )
            logger.info(f"MinIO client initialized for endpoint: {settings.MINIO_ENDPOINT}")
            
        except Exception as e:
            logger.error(f"Failed to initialize MinIO client: {e}")
            raise RuntimeError(f"MinIO initialization failed: {e}")
    
    async def _ensure_bucket_exists(self):
        """Ensure the bucket exists, create if not"""
        try:
            loop = asyncio.get_event_loop()
            bucket_exists = await loop.run_in_executor(
                None,
                self.client.bucket_exists,
                self.bucket_name
            )
            
            if not bucket_exists:
                await loop.run_in_executor(
                    None,
                    self.client.make_bucket,
                    self.bucket_name
                )
                logger.info(f"Created bucket: {self.bucket_name}")
            else:
                logger.debug(f"Bucket exists: {self.bucket_name}")
                
        except Exception as e:
            logger.error(f"Error ensuring bucket exists: {e}")
            raise RuntimeError(f"Bucket creation failed: {e}")
    
    async def save_text_file(
        self, 
        content: str, 
        filename: str,
        content_type: str = "text/plain"
    ) -> str:
        """
        Save text content to MinIO.
        
        Args:
            content: Text content to save
            filename: Name of the file
            content_type: MIME type of the content
            
        Returns:
            Public URL to the saved file
        """
        await self._ensure_bucket_exists()
        
        try:
            # Convert string to bytes
            data = content.encode('utf-8')
            
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.client.put_object(
                    bucket_name=self.bucket_name,
                    object_name=filename,
                    data=data,
                    length=len(data),
                    content_type=content_type
                )
            )
            
            # Generate public URL
            file_url = self._get_public_url(filename)
            logger.info(f"Saved text file: {filename} ({len(content)} chars)")
            return file_url
            
        except Exception as e:
            logger.error(f"Error saving text file {filename}: {e}")
            raise RuntimeError(f"Text file save failed: {e}")
    
    async def save_json_file(self, data: dict, filename: str) -> str:
        """
        Save JSON data to MinIO.
        
        Args:
            data: Dictionary to save as JSON
            filename: Name of the file
            
        Returns:
            Public URL to the saved file
        """
        try:
            json_content = json.dumps(data, indent=2, ensure_ascii=False)
            return await self.save_text_file(json_content, filename, "application/json")
            
        except Exception as e:
            logger.error(f"Error saving JSON file {filename}: {e}")
            raise RuntimeError(f"JSON file save failed: {e}")
    
    async def get_file_content(self, filename: str) -> str:
        """
        Retrieve text content from MinIO.
        
        Args:
            filename: Name of the file to retrieve
            
        Returns:
            File content as string
        """
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self.client.get_object,
                self.bucket_name,
                filename
            )
            
            content = response.read().decode('utf-8')
            response.close()
            response.release_conn()
            
            logger.debug(f"Retrieved file: {filename} ({len(content)} chars)")
            return content
            
        except Exception as e:
            logger.error(f"Error retrieving file {filename}: {e}")
            raise RuntimeError(f"File retrieval failed: {e}")
    
    async def delete_file(self, filename: str) -> bool:
        """
        Delete a file from MinIO.
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self.client.remove_object,
                self.bucket_name,
                filename
            )
            
            logger.info(f"Deleted file: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting file {filename}: {e}")
            return False
    
    async def list_files(self, prefix: str = "") -> list:
        """
        List files in the bucket.
        
        Args:
            prefix: Optional prefix to filter files
            
        Returns:
            List of file names
        """
        try:
            loop = asyncio.get_event_loop()
            objects = await loop.run_in_executor(
                None,
                lambda: list(self.client.list_objects(self.bucket_name, prefix=prefix))
            )
            
            filenames = [obj.object_name for obj in objects]
            logger.debug(f"Listed {len(filenames)} files with prefix '{prefix}'")
            return filenames
            
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            return []
    
    def _get_public_url(self, filename: str) -> str:
        """Generate public URL for a file"""
        protocol = "https" if settings.MINIO_SECURE else "http"
        return f"{protocol}://{settings.MINIO_ENDPOINT}/{self.bucket_name}/{filename}"
    
    async def get_presigned_url(self, filename: str, expires: int = 3600) -> str:
        """
        Generate a presigned URL for secure access.
        
        Args:
            filename: Name of the file
            expires: URL expiration time in seconds (default 1 hour)
            
        Returns:
            Presigned URL
        """
        try:
            loop = asyncio.get_event_loop()
            url = await loop.run_in_executor(
                None,
                lambda: self.client.presigned_get_object(
                    self.bucket_name,
                    filename,
                    expires=timedelta(seconds=expires)
                )
            )
            
            logger.debug(f"Generated presigned URL for {filename}")
            return url
            
        except Exception as e:
            logger.error(f"Error generating presigned URL for {filename}: {e}")
            raise RuntimeError(f"Presigned URL generation failed: {e}")
    
    async def health_check(self) -> dict:
        """Check if MinIO service is accessible"""
        try:
            # Test bucket access
            loop = asyncio.get_event_loop()
            bucket_exists = await loop.run_in_executor(
                None,
                self.client.bucket_exists,
                self.bucket_name
            )
            
            # Test file operations
            test_filename = "health_check.txt"
            test_content = f"Health check at {datetime.utcnow().isoformat()}"
            
            await self.save_text_file(test_content, test_filename)
            retrieved_content = await self.get_file_content(test_filename)
            await self.delete_file(test_filename)
            
            return {
                "status": "healthy",
                "bucket_exists": bucket_exists,
                "test_write_read_delete": "success",
                "endpoint": settings.MINIO_ENDPOINT
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

# Global service instance
storage_service = StorageService()