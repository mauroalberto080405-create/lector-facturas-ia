from datetime import date

import pytest

from tests.datos import guardar_factura


@pytest.fixture
def tres_facturas(sesion):
    """Datos ficticios: 2 proveedores, 2 meses, una OBSERVADA."""
    guardar_factura(sesion, serie_numero="F001-00000001", fecha_emision=date(2026, 9, 10))
    guardar_factura(sesion, serie_numero="F001-00000002", fecha_emision=date(2026, 10, 5))
    guardar_factura(
        sesion, estado="OBSERVADA", ruc_emisor="20555123451",
        serie_numero="E001-00000003", fecha_emision=date(2026, 10, 20),
    )


def series(respuesta) -> list[str]:
    return [f["serie_numero"] for f in respuesta.json()]


def test_lista_todas_ordenadas_por_fecha_descendente(cliente, tres_facturas):
    respuesta = cliente.get("/facturas")
    assert respuesta.status_code == 200
    assert series(respuesta) == ["E001-00000003", "F001-00000002", "F001-00000001"]


@pytest.mark.parametrize(
    "parametros, esperadas",
    [
        ({"ruc": "20555123451"}, ["E001-00000003"]),
        ({"estado": "VALIDA"}, ["F001-00000002", "F001-00000001"]),
        ({"desde": "2026-10-01"}, ["E001-00000003", "F001-00000002"]),
        ({"hasta": "2026-09-30"}, ["F001-00000001"]),
        ({"estado": "VALIDA", "desde": "2026-10-01", "hasta": "2026-10-31"}, ["F001-00000002"]),
    ],
)
def test_filtros(cliente, tres_facturas, parametros, esperadas):
    assert series(cliente.get("/facturas", params=parametros)) == esperadas


def test_estado_invalido_devuelve_422(cliente):
    assert cliente.get("/facturas", params={"estado": "PAGADA"}).status_code == 422


def test_rango_de_fechas_al_reves_devuelve_400(cliente):
    respuesta = cliente.get("/facturas", params={"desde": "2026-10-31", "hasta": "2026-10-01"})
    assert respuesta.status_code == 400


def test_obtener_por_id(cliente, sesion):
    factura = guardar_factura(sesion)
    respuesta = cliente.get(f"/facturas/{factura.id}")
    assert respuesta.status_code == 200
    assert respuesta.json()["serie_numero"] == "F001-00000123"
    assert len(respuesta.json()["items"]) == 2


def test_id_inexistente_devuelve_404(cliente):
    assert cliente.get("/facturas/999").status_code == 404
