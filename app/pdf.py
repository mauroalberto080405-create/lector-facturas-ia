import io

import pdfplumber


class PDFInvalidoError(ValueError):
    """El archivo no es un PDF legible o no contiene texto."""


def extraer_texto(contenido: bytes) -> str:
    """Devuelve el texto de todas las páginas de un PDF recibido como bytes."""
    try:
        with pdfplumber.open(io.BytesIO(contenido)) as pdf:
            paginas = [pagina.extract_text() or "" for pagina in pdf.pages]
    except Exception as error:  # pdfplumber lanza varios tipos según el daño del archivo
        raise PDFInvalidoError("El archivo no es un PDF válido") from error

    texto = "\n".join(paginas).strip()
    if not texto:
        # Un PDF escaneado (solo imagen) no tiene texto: necesitaría OCR, que está fuera de alcance.
        raise PDFInvalidoError("El PDF no contiene texto (¿es una imagen escaneada?)")
    return texto
