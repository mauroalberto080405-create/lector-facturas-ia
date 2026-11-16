from typing import Protocol

from pydantic import ValidationError

from app.schemas import FacturaExtraida


class ErrorExtraccion(Exception):
    """La IA no respondió o devolvió algo que no tiene forma de factura."""


class ExtractorIA(Protocol):
    """Contrato común: cualquier extractor recibe texto y devuelve una FacturaExtraida."""

    def extraer(self, texto: str) -> FacturaExtraida: ...


INSTRUCCIONES = """Eres un asistente contable peruano. Extrae los datos de la factura electrónica SUNAT del texto que te envíe.
Reglas:
- ruc_emisor: RUC de 11 dígitos de la empresa que EMITE la factura (aparece junto a su razón social y "FACTURA ELECTRÓNICA"). NO uses el RUC del cliente.
- serie_numero: con el formato F001-00012345.
- fecha_emision: con el formato AAAA-MM-DD.
- moneda: "PEN" si los montos usan S/ y "USD" si usan US$.
- Montos como números con punto decimal y sin separador de miles (1840.80, no 1,840.80).
- subtotal es la "Op. gravada" (base imponible).
- Copia los valores tal como aparecen en el texto, aunque parezcan incorrectos. NO los corrijas ni los recalcules.
Responde SOLO con el JSON."""


def a_factura(json_texto: str) -> FacturaExtraida:
    """Convierte la respuesta de la IA en FacturaExtraida; si no encaja, ErrorExtraccion."""
    try:
        return FacturaExtraida.model_validate_json(json_texto)
    except ValidationError as error:
        raise ErrorExtraccion(f"La IA devolvió un JSON que no es una factura: {error}") from error
