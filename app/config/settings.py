from __future__ import annotations

import urllib.parse
from functools import lru_cache

from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(extra="ignore")

    app_name: str = "Agent LTM API"
    app_version: str = "0.1.0"

    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "agent_ltm"
    db_user: str = "postgres"
    db_password: str = "postgres"
    
    store_schema: str = "public"
    checkpoint_schema: str = "public"

    redis_host: str = "localhost"
    redis_port: int = 6379

    openai_api_key: str | None = None
    azure_openai_api_endpoint: str | None = None
    azure_openai_api_key: str | None = None
    azure_openai_deployment_name: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache(maxsize=1)
def get_pg_store_conn_string() -> str:
    settings = get_settings()
    base_uri = f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    
    if settings.store_schema != "public":
        options = f"-c search_path={settings.store_schema},public"
        encoded_options = urllib.parse.quote_plus(options)
        return f"{base_uri}?options={encoded_options}"
    
    return base_uri


@lru_cache(maxsize=1)
def get_pg_checkpointer_conn_string() -> str:
    settings = get_settings()
    base_uri = f"postgresql://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"
    
    if settings.checkpoint_schema != "public":
        options = f"-c search_path={settings.checkpoint_schema},public"
        encoded_options = urllib.parse.quote_plus(options)
        return f"{base_uri}?options={encoded_options}"
    
    return base_uri
