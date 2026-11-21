"""Application settings module."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and the .env file."""

    source_impl: str | None = Field(None, description="Source implementation class to retrieve data with")
    secret_key: str = Field(description="Secret key for JWT tokens")

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)
