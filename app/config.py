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
    # Vacío = OpenAI. Con otra URL se usa cualquier API compatible (p. ej. Groq).
    openai_base_url: str | None = None
    database_url: str = "postgresql+psycopg://facturas:facturas@localhost:5432/facturas"
    # Orígenes (frontends) que el navegador deja llamar a esta API. En .env va como JSON:
    # CORS_ORIGENES=["http://localhost:4200","https://mi-front.com"]
    cors_origenes: list[str] = ["http://localhost:4200"]


config = Config()
