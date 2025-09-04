from pydantic_settings import BaseSettings, SettingsConfigDict
from  typing import Optional

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    REDIS_HOST: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    LOG_LEVEL: str = 'INFO'
    LOG_FILE: Optional[str] = None

    CORS_ORIGINS: list = ['http://localhost:3000']
    RATE_LIMIT_PER_MINUTE: int = 60

    SMTP_SERVER: Optional[str] = None
    SMTP_PORT = 587
    SMTP_USERNAME = Optional[str] = None
    SMTP_PASSWORD = Optional[str] = None

    ENVIORONMENT: str = 'development'
    DEBUG: bool = False
    

    @property
    def DATA_URL(self):
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    @property
    def REDIS_URL(self):
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8'
    )

settings = Settings()