# V2 POC Configuration
"""
This module defines the application's configuration using Pydantic's BaseSettings.

It allows for type-validated settings that can be loaded from environment variables
or a .env file, making the application's configuration robust and easy to manage.
"""

import os
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional

class Settings(BaseSettings):
    """
    A Pydantic model for managing all application settings.
    
    Attributes are mapped to environment variables (case-sensitive).
    Default values are provided for development, but can be overridden.
    """
    
    # --- General Application Settings ---
    APP_ENV: str = Field(default="development", description="The application environment (e.g., development, production).")
    LOG_LEVEL: str = Field(default="INFO", description="The logging level (e.g., DEBUG, INFO, WARNING, ERROR).")
    
    # --- Database Configuration (PostgreSQL) ---
    DATABASE_URL: str = Field(description="The full connection string for the PostgreSQL database.")
    DB_POOL_MIN_SIZE: int = Field(default=2, ge=1, description="Minimum number of connections in the database pool.")
    DB_POOL_MAX_SIZE: int = Field(default=10, ge=1, description="Maximum number of connections in the database pool.")
    
    # --- Cache Configuration (Redis) ---
    REDIS_URL: str = Field(default="redis://redis:6379", description="The connection URL for the Redis server.")
    
    # --- Object Storage Configuration (MinIO) ---
    MINIO_ENDPOINT: str = Field(default="minio:9000", description="The endpoint URL for the MinIO server.")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin", description="The access key for MinIO.")
    MINIO_SECRET_KEY: str = Field(default="minioadmin123", description="The secret key for MinIO.")
    MINIO_BUCKET_NAME: str = Field(default="poc-bucket", description="The default bucket to use for object storage.")
    MINIO_SECURE: bool = Field(default=False, description="Whether to use HTTPS for the MinIO connection.")
    
    # --- AI Service Configuration (OpenRouter) ---
    OPENROUTER_API_KEY: str = Field(description="The API key for authenticating with OpenRouter.")
    OPENROUTER_BASE_URL: str = Field(default="https://openrouter.ai/api/v1", description="The base URL for the OpenRouter API.")
    OPENROUTER_SITE_URL: str = Field(default="http://localhost:8000", description="The site URL to send as a referrer to OpenRouter.")
    OPENROUTER_APP_NAME: str = Field(default="InkAndQuill-V2-POC", description="The application name to send to OpenRouter.")
    DEFAULT_MODEL: str = Field(default="deepseek/deepseek-r1", description="The default AI model to use for generation.")
    
    class Config:
        """Pydantic configuration settings."""
        # Load environment variables from a .env file.
        env_file = ".env"
        # Ensure that environment variable names are matched case-sensitively.
        case_sensitive = True
        # Allows for extra fields not defined in the model.
        extra = 'ignore'

    @validator("DATABASE_URL", pre=True, always=True)
    def assemble_db_connection(cls, v, values):
        """Assembles the DATABASE_URL from other PG settings if it's not provided."""
        if isinstance(v, str):
            return v
        return f"postgresql://{values.get('POSTGRES_USER')}:{values.get('POSTGRES_PASSWORD')}@postgres:5432/{values.get('POSTGRES_DB')}"

# Create a single, global instance of the Settings.
# This instance will be imported and used by other parts of the application
# to access configuration values.
try:
    settings = Settings()
except Exception as e:
    # This provides a helpful error message if configuration fails on startup.
    raise RuntimeError(f"Failed to load application settings. Please check your .env file and environment variables. Error: {e}")
