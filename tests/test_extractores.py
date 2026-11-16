"""Pruebas de los extractores SIN llamar a ninguna IA real (clientes simulados)."""

import json
from decimal import Decimal
from types import SimpleNamespace

import httpx
import pytest

from app.config import Config
from app.extractores.base import ErrorExtraccion
from app.extractores.fabrica import crear_extractor
from app.extractores.ollama_extractor import OllamaExtractor
from app.extractores.openai_extractor import OpenAIExtractor

RESPUESTA_IA = json.dumps({
    "ruc_emisor": "20601234565",
    "razon_social": "Comercial Andina del Sur S.A.C.",
    "serie_numero": "F001-00000123",
    "fecha_emision": "2026-10-05",
    "moneda": "PEN",
    "subtotal": 585.00,
    "igv": 105.30,
    "total": 690.30,
    "items": [
        {"descripcion": "Papel bond A4 (millar)", "cantidad": 10, "precio_unitario": 22.50},
        {"descripcion": "Tóner HP 85A", "cantidad": 2, "precio_unitario": 180.00},
    ],
})


def ollama_simulado(manejador) -> OllamaExtractor:
    """OllamaExtractor cuyo cliente HTTP no sale a la red: responde `manejador`."""
    cliente = httpx.Client(transport=httpx.MockTransport(manejador))
    return OllamaExtractor("http://ollama-falso:11434", "modelo-x", cliente=cliente)


def test_ollama_convierte_la_respuesta_en_factura():
    peticiones = []

    def manejador(request: httpx.Request) -> httpx.Response:
        peticiones.append(json.loads(request.content))
        return httpx.Response(200, json={"message": {"content": RESPUESTA_IA}})

    factura = ollama_simulado(manejador).extraer("texto del pdf")

    assert factura.ruc_emisor == "20601234565"
    assert factura.total == Decimal("690.30")
    assert peticiones[0]["model"] == "modelo-x"
    assert "properties" in peticiones[0]["format"]  # se envió el esquema JSON


def test_ollama_con_json_que_no_es_factura_lanza_error():
    manejador = lambda request: httpx.Response(200, json={"message": {"content": '{"hola": 1}'}})

    with pytest.raises(ErrorExtraccion, match="no es una factura"):
        ollama_simulado(manejador).extraer("texto")


def test_ollama_apagado_lanza_error():
    def manejador(request):
        raise httpx.ConnectError("conexión rechazada")

    with pytest.raises(ErrorExtraccion, match="No se pudo consultar Ollama"):
        ollama_simulado(manejador).extraer("texto")


def test_openai_convierte_la_respuesta_en_factura():
    mensaje = SimpleNamespace(content=RESPUESTA_IA)
    respuesta = SimpleNamespace(choices=[SimpleNamespace(message=mensaje)])
    cliente = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **kwargs: respuesta))
    )

    factura = OpenAIExtractor("sk-falsa", "gpt-x", cliente=cliente).extraer("texto")

    assert factura.serie_numero == "F001-00000123"


def test_fabrica_elige_ollama_por_defecto():
    assert isinstance(crear_extractor(Config(_env_file=None)), OllamaExtractor)


def test_fabrica_elige_openai_si_hay_api_key():
    config = Config(_env_file=None, ia_proveedor="openai", openai_api_key="sk-falsa")
    assert isinstance(crear_extractor(config), OpenAIExtractor)


def test_fabrica_openai_sin_api_key_falla_con_mensaje_claro():
    with pytest.raises(ValueError, match="OPENAI_API_KEY"):
        crear_extractor(Config(_env_file=None, ia_proveedor="openai"))
