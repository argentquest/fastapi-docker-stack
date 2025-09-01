# V2 POC Configuration
"""
This module defines the application's configuration using Pydantic's BaseSettings.

It allows for type-validated settings that can be loaded from environment variables
or a .env file, making the application's configuration robust and easy to manage.
"""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Explicitly load .env file before creating settings
env_path = Path(__file__).parent.parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path, override=True)
    print(f"Loaded .env from: {env_path}")
else:
    print(f"Warning: .env file not found at {env_path}")


class Settings(BaseSettings):
    """
    A Pydantic model for managing all application settings.

    Attributes are mapped to environment variables (case-sensitive).
    Default values are provided for development, but can be overridden.
    """

    # --- General Application Settings ---
    APP_ENV: str = Field(default="development", description="The application environment (e.g., development, production).")
    LOG_LEVEL: str = Field(default="INFO", description="The logging level (e.g., DEBUG, INFO, WARNING, ERROR).")
    DEBUG: bool = Field(default=True, description="Debug mode flag.")

    # --- AI Service Configuration (OpenRouter) ---
    OPENROUTER_API_KEY: str = Field(description="The API key for authenticating with OpenRouter.")
    OPENROUTER_BASE_URL: str = Field(default="https://openrouter.ai/api/v1", description="The base URL for the OpenRouter API.")
    OPENROUTER_SITE_URL: str = Field(default="http://localhost:8000", description="The site URL to send as a referrer to OpenRouter.")
    OPENROUTER_APP_NAME: str = Field(default="InkAndQuill-V2-POC", description="The application name to send to OpenRouter.")
    DEFAULT_MODEL: str = Field(default="deepseek/deepseek-r1", description="The default AI model to use for generation.")
    OPENROUTER_DEFAULT_MODEL: str = Field(default="google/gemini-2.5-flash-lite", description="The default model for OpenRouter services.")
    GOOGLE_DEFAULT_MODEL: str = Field(default="gemini-2.5-flash-image-preview", description="The default model for Google AI services.")
    
    # --- Alternative AI Provider Configuration (Azure OpenAI) ---
    AZURE_OPENAI_ENDPOINT: Optional[str] = Field(default=None, description="Azure OpenAI endpoint URL.")
    AZURE_OPENAI_API_KEY: Optional[str] = Field(default=None, description="Azure OpenAI API key.")
    AZURE_OPENAI_DEPLOYMENT_NAME: Optional[str] = Field(default=None, description="Azure OpenAI deployment name.")
    
    # --- Google AI Configuration (Gemini API) ---
    GOOGLE_API_KEY: Optional[str] = Field(default=None, description="Google AI API key for Gemini models.")

    # --- Database Configuration (PostgreSQL) ---
    POSTGRES_USER: str = Field(default="pocuser", description="PostgreSQL username.")
    POSTGRES_PASSWORD: str = Field(default="pocpass", description="PostgreSQL password.")
    POSTGRES_DB: str = Field(default="poc_local", description="PostgreSQL database name.")
    DATABASE_URL: str = Field(description="The full connection string for the PostgreSQL database.")
    DB_POOL_MIN_SIZE: int = Field(default=2, ge=1, description="Minimum number of connections in the database pool.")
    DB_POOL_MAX_SIZE: int = Field(default=10, ge=1, description="Maximum number of connections in the database pool.")
    DB_COMMAND_TIMEOUT: int = Field(default=60, ge=1, description="Database command timeout in seconds.")

    # --- MongoDB Configuration ---
    MONGO_INITDB_ROOT_USERNAME: str = Field(default="mongoadmin", description="MongoDB root username.")
    MONGO_INITDB_ROOT_PASSWORD: str = Field(default="mongopass123", description="MongoDB root password.")
    MONGO_INITDB_DATABASE: str = Field(default="poc_mongo_db", description="MongoDB database name.")
    MONGODB_URL: str = Field(description="MongoDB connection URL.")

    # --- Cache Configuration (Redis) ---
    REDIS_URL: str = Field(description="The connection URL for the Redis server.")
    REDIS_PASSWORD: str = Field(default="devpass", description="Redis password.")

    # --- Object Storage Configuration (MinIO) ---
    MINIO_ROOT_USER: str = Field(default="minioadmin", description="MinIO root username.")
    MINIO_ROOT_PASSWORD: str = Field(default="minioadmin123", description="MinIO root password.")
    MINIO_ENDPOINT: str = Field(description="The endpoint URL for the MinIO server.")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin", description="The access key for MinIO.")
    MINIO_SECRET_KEY: str = Field(default="minioadmin123", description="The secret key for MinIO.")
    MINIO_BUCKET_NAME: str = Field(default="v2-poc-storage", description="The default bucket to use for object storage.")
    MINIO_SECURE: bool = Field(default=False, description="Whether to use HTTPS for the MinIO connection.")

    # --- JWT Configuration ---
    JWT_SECRET_KEY: str = Field(default="local-dev-jwt-secret-key-change-in-production", description="JWT secret key.")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm.")
    JWT_EXPIRATION_HOURS: int = Field(default=24, description="JWT expiration time in hours.")

    # --- CORS Configuration ---
    ALLOWED_ORIGINS: str = Field(default="http://localhost:3000,https://pocmaster.argentquest.com,http://localhost:8000,http://localhost:8003", description="Comma-separated list of allowed CORS origins.")
    ALLOWED_METHODS: str = Field(default="GET,POST,PUT,DELETE,OPTIONS", description="Comma-separated list of allowed HTTP methods.")

    # --- Azure Services Configuration ---
    AZURE_SEARCH_ENDPOINT: Optional[str] = Field(default=None, description="Azure Search service endpoint.")
    AZURE_SEARCH_API_KEY: Optional[str] = Field(default=None, description="Azure Search API key.")
    AZURE_SEARCH_INDEX_NAME: Optional[str] = Field(default=None, description="Azure Search index name.")
    AZURE_OPENAI_EMBEDDING_ENDPOINT: Optional[str] = Field(default=None, description="Azure OpenAI endpoint for embeddings.")
    AZURE_OPENAI_EMBEDDING_API_KEY: Optional[str] = Field(default=None, description="Azure OpenAI API key for embeddings.")
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: Optional[str] = Field(default=None, description="Azure OpenAI embedding deployment name.")
    AZURE_OPENAI_EMBEDDING_MODEL: Optional[str] = Field(default=None, description="Azure OpenAI embedding model name.")
    AZURE_OPENAI_EMBEDDING_DIMENSIONS: Optional[int] = Field(default=None, description="Azure OpenAI embedding dimensions.")

    # --- Security Configuration ---
    SECRET_KEY: str = Field(default="dev-secret-key", description="Application secret key.")

    # --- Additional Development Tools ---
    VSCODE_PASSWORD: Optional[str] = Field(default="changeme", description="VS Code server password.")

    model_config = {
        "env_file": Path(__file__).parent.parent.parent / ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }

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
    print(f"Settings loaded successfully. API key present: {bool(settings.OPENROUTER_API_KEY)}")
except Exception as e:
    # This provides a helpful error message if configuration fails on startup.
    raise RuntimeError(f"Failed to load application settings. Please check your .env file and environment variables. Error: {e}")
