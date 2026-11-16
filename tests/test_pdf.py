from pathlib import Path

import pytest

from app.pdf import PDFInvalidoError, extraer_texto

CARPETA = Path(__file__).resolve().parent.parent / "facturas_ejemplo"


def test_extrae_datos_clave_de_factura_ficticia():
    contenido = (CARPETA / "factura_01_correcta.pdf").read_bytes()

    texto = extraer_texto(contenido)

    assert "F001-00000123" in texto
    assert "Comercial Andina del Sur S.A.C." in texto
    assert "690.30" in texto  # importe total


def test_archivo_que_no_es_pdf_lanza_error():
    with pytest.raises(PDFInvalidoError):
        extraer_texto(b"esto no es un pdf")
