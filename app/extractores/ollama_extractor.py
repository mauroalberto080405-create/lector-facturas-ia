import httpx

from app.extractores.base import INSTRUCCIONES, ErrorExtraccion, a_factura
from app.schemas import FacturaExtraida


class OllamaExtractor:
    """Usa un modelo local de Ollama (gratis, sin enviar datos a internet)."""

    def __init__(self, url: str, modelo: str, cliente: httpx.Client | None = None):
        self.url = url.rstrip("/")
        self.modelo = modelo
        # El cliente se puede inyectar: en las pruebas pasamos uno falso.
        self.cliente = cliente or httpx.Client(timeout=180)

    def extraer(self, texto: str) -> FacturaExtraida:
        cuerpo = {
            "model": self.modelo,
            "stream": False,
            # Ollama obliga al modelo a responder con JSON que siga este esquema.
            "format": FacturaExtraida.model_json_schema(),
            "options": {"temperature": 0},
            "messages": [
                {"role": "system", "content": INSTRUCCIONES},
                {"role": "user", "content": texto},
            ],
        }
        try:
            respuesta = self.cliente.post(f"{self.url}/api/chat", json=cuerpo)
            respuesta.raise_for_status()
            contenido = respuesta.json()["message"]["content"]
        except (httpx.HTTPError, KeyError, ValueError) as error:
            raise ErrorExtraccion(f"No se pudo consultar Ollama en {self.url}: {error}") from error
        return a_factura(contenido)
