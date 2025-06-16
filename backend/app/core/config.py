from typing import Any
from pydantic import field_validator, PostgresDsn
from pydantic_settings import BaseSettings
from pydantic_core.core_schema import ValidationInfo


class Settings(BaseSettings):
    PROJECT_NAME: str = "DocIntell"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "docintell"
    DATABASE_URI: PostgresDsn | None = None
    
    @field_validator("DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str | None, info: ValidationInfo) -> Any:
        if isinstance(v, str):
            return v
        values = info.data
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=values.get("POSTGRES_DB", ""),
        )
    
    REDIS_URL: str = "redis://localhost:6379"
    
    OPENAI_API_KEY: str = ""
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    LLM_MODEL: str = "gpt-3.5-turbo"
    
    CHROMA_PERSIST_DIRECTORY: str = "./chromadb"
    CHROMA_COLLECTION_NAME: str = "documents"
    
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set[str] = {".pdf", ".txt", ".doc", ".docx"}
    
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()