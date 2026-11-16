from functools import lru_cache

from app.config import Config, config
from app.extractores.base import ExtractorIA
from app.extractores.ollama_extractor import OllamaExtractor
from app.extractores.openai_extractor import OpenAIExtractor


def crear_extractor(config: Config) -> ExtractorIA:
    """Elige la implementación según IA_PROVEEDOR. El resto del código no sabe cuál es."""
    if config.ia_proveedor == "openai":
        if not config.openai_api_key:
            raise ValueError("IA_PROVEEDOR=openai requiere OPENAI_API_KEY en el archivo .env")
        return OpenAIExtractor(config.openai_api_key, config.openai_modelo)
    return OllamaExtractor(config.ollama_url, config.ollama_modelo)


@lru_cache
def obtener_extractor() -> ExtractorIA:
    """Dependencia de FastAPI: un solo extractor para toda la app (reutiliza conexiones)."""
    return crear_extractor(config)
