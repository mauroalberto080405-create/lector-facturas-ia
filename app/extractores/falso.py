from app.schemas import FacturaExtraida


class ExtractorFalso:
    """Para pruebas: devuelve siempre la factura que le damos, sin llamar a ninguna IA."""

    def __init__(self, factura: FacturaExtraida):
        self.factura = factura
        self.textos_recibidos: list[str] = []

    def extraer(self, texto: str) -> FacturaExtraida:
        self.textos_recibidos.append(texto)
        return self.factura
