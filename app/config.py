from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Lee variables de entorno (o del archivo .env). IA_PROVEEDOR -> ia_proveedor."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ia_proveedor: Literal["ollama", "openai"] = "ollama"
    ollama_url: str = "http://localhost:11434"
    ollama_modelo: str = "qwen2.5:3b"
    openai_api_key: str | None = None
    openai_modelo: str = "gpt-4o-mini"
    database_url: str = "postgresql+psycopg://facturas:facturas@localhost:5432/facturas"


config = Config()
