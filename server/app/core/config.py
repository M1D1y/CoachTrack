from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')
    database_url: str = 'postgresql+psycopg://coachtrack:password@localhost:5432/coachtrack'
    jwt_secret_key: str = Field(min_length=32)
    access_token_expire_minutes: int = Field(30, gt=0)
    refresh_token_expire_days: int = Field(7, gt=0)
    cors_origins: str = 'http://localhost:5173'

    @field_validator('jwt_secret_key')
    @classmethod
    def reject_placeholder_secret(cls, value: str) -> str:
        if value.startswith('replace_with'):
            raise ValueError('Replace JWT_SECRET_KEY with a random secret')
        return value

@lru_cache
def settings() -> Settings:
    return Settings()
