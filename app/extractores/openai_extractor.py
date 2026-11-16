import json

from openai import OpenAI, OpenAIError

from app.extractores.base import INSTRUCCIONES, ErrorExtraccion, a_factura
from app.schemas import FacturaExtraida


class OpenAIExtractor:
    """Usa la API de OpenAI (de pago; la API key se lee del .env)."""

    def __init__(self, api_key: str, modelo: str, cliente: OpenAI | None = None):
        self.modelo = modelo
        self.cliente = cliente or OpenAI(api_key=api_key)

    def extraer(self, texto: str) -> FacturaExtraida:
        esquema = json.dumps(FacturaExtraida.model_json_schema(), ensure_ascii=False)
        try:
            respuesta = self.cliente.chat.completions.create(
                model=self.modelo,
                temperature=0,
                response_format={"type": "json_object"},  # garantiza JSON sintácticamente válido
                messages=[
                    {"role": "system", "content": f"{INSTRUCCIONES}\nEsquema JSON:\n{esquema}"},
                    {"role": "user", "content": texto},
                ],
            )
            contenido = respuesta.choices[0].message.content or ""
        except OpenAIError as error:
            raise ErrorExtraccion(f"No se pudo consultar OpenAI: {error}") from error
        return a_factura(contenido)
