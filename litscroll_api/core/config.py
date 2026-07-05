from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    debug: bool = False
    database_url: str

    model_config = SettingsConfigDict(
        env_file='.env.dev', case_sensitive=False, extra='ignore'
    )


@lru_cache
def get_settings():
    return Settings()
