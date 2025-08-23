# V2 POC Configuration
import os
import logging
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional

logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """V2 POC Application Settings"""
    
    # Environment
    APP_ENV: str = Field(default="development", alias="APP_ENV")
    LOG_LEVEL: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # Database Configuration
    DATABASE_URL: str = Field(alias="DATABASE_URL")
    POSTGRES_USER: str = Field(default="pocuser", alias="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="pocpass", alias="POSTGRES_PASSWORD") 
    POSTGRES_DB: str = Field(default="poc_db", alias="POSTGRES_DB")
    
    # Redis Configuration
    REDIS_URL: str = Field(default="redis://redis:6379", alias="REDIS_URL")
    
    # MinIO Configuration
    MINIO_ENDPOINT: str = Field(default="minio:9000", alias="MINIO_ENDPOINT")
    MINIO_ACCESS_KEY: str = Field(default="minioadmin", alias="MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY: str = Field(default="minioadmin123", alias="MINIO_SECRET_KEY")
    MINIO_BUCKET_NAME: str = Field(default="poc-bucket", alias="MINIO_BUCKET_NAME")
    MINIO_SECURE: bool = Field(default=False, alias="MINIO_SECURE")
    
    # OpenRouter Configuration
    OPENROUTER_API_KEY: Optional[str] = Field(default=None, alias="OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL: str = Field(default="https://openrouter.ai/api/v1", alias="OPENROUTER_BASE_URL")
    OPENROUTER_SITE_URL: Optional[str] = Field(default=None, alias="OPENROUTER_SITE_URL") 
    OPENROUTER_APP_NAME: Optional[str] = Field(default="InkAndQuill-V2-POC", alias="OPENROUTER_APP_NAME")
    
    # AI Model Configuration
    DEFAULT_MODEL: str = Field(default="deepseek/deepseek-r1", alias="DEFAULT_MODEL")
    
    # Connection Pool Configuration
    DB_POOL_MIN_SIZE: int = Field(default=2, ge=1, alias="DB_POOL_MIN_SIZE")
    DB_POOL_MAX_SIZE: int = Field(default=10, ge=1, alias="DB_POOL_MAX_SIZE")
    DB_COMMAND_TIMEOUT: int = Field(default=60, ge=1, alias="DB_COMMAND_TIMEOUT")
    
    # Redis Configuration
    REDIS_MAX_CONNECTIONS: int = Field(default=10, ge=1, alias="REDIS_MAX_CONNECTIONS")
    REDIS_PASSWORD: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    
    # Security Configuration
    API_KEY: Optional[str] = Field(default=None, alias="API_KEY")
    ALLOWED_ORIGINS: str = Field(default="http://localhost:3000,http://localhost:8000", alias="ALLOWED_ORIGINS")
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, ge=1, alias="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_PERIOD: int = Field(default=60, ge=1, alias="RATE_LIMIT_PERIOD")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        """Validate database URL format"""
        if not v.startswith("postgresql://"):
            raise ValueError("DATABASE_URL must start with postgresql://")
        return v
    
    @validator("OPENROUTER_API_KEY")
    def validate_api_key(cls, v):
        """Ensure API key is set in production"""
        if not v or v == "your_openrouter_api_key_here":
            raise ValueError("Valid OPENROUTER_API_KEY must be set")
        return v

# Global settings instance
settings = Settings()