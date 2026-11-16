from decimal import Decimal
from pathlib import Path

from app.extractores.base import ErrorExtraccion
from tests.datos import factura_valida

PDF = (Path(__file__).resolve().parent.parent / "facturas_ejemplo" / "factura_01_correcta.pdf").read_bytes()


def subir(cliente, contenido: bytes = PDF, nombre: str = "factura.pdf"):
    return cliente.post("/facturas", files={"archivo": (nombre, contenido, "application/pdf")})


def test_factura_correcta_se_guarda_como_valida(cliente, extractor):
    respuesta = subir(cliente)

    assert respuesta.status_code == 201
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "VALIDA"
    assert cuerpo["errores"] == []
    assert cuerpo["serie_numero"] == "F001-00000123"
    assert len(cuerpo["items"]) == 2
    assert "F001-00000123" in extractor.textos_recibidos[0]  # a la IA le llegó el texto del PDF


def test_factura_con_errores_se_guarda_como_observada(cliente, extractor):
    extractor.factura = factura_valida(igv=Decimal("50.00"), total=Decimal("635.00"))

    respuesta = subir(cliente)

    assert respuesta.status_code == 201
    assert respuesta.json()["estado"] == "OBSERVADA"
    assert any("IGV" in e for e in respuesta.json()["errores"])


def test_factura_duplicada_devuelve_409(cliente):
    primera = subir(cliente)
    segunda = subir(cliente)

    assert segunda.status_code == 409
    assert f"id {primera.json()['id']}" in segunda.json()["detail"]


def test_archivo_que_no_es_pdf_devuelve_400(cliente):
    respuesta = subir(cliente, contenido=b"hola", nombre="nota.txt")
    assert respuesta.status_code == 400


def test_si_la_ia_falla_devuelve_502(cliente, extractor):
    def falla(texto):
        raise ErrorExtraccion("Ollama no responde")

    extractor.extraer = falla

    respuesta = subir(cliente)

    assert respuesta.status_code == 502
    assert "Ollama no responde" in respuesta.json()["detail"]
