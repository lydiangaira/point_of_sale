
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    
    PROJECT_NAME: str = "Secure POS Backend API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    
    SECRET_KEY: str = Field("09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7", alias="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8
    
    
    DATABASE_URL: str = Field("postgresql://postgres:postgres@localhost:5432/pos", alias="DATABASE_URL")

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()
