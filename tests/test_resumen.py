from datetime import date
from decimal import Decimal

from tests.datos import guardar_factura


def test_resumen_vacio(cliente):
    assert cliente.get("/resumen").json() == {"por_mes": [], "por_proveedor": []}


def test_resumen_por_mes_y_proveedor(cliente, sesion):
    # Proveedor A: 2 facturas en octubre (690.30 c/u) y 1 en septiembre
    guardar_factura(sesion, serie_numero="F001-1", fecha_emision=date(2026, 9, 10))
    guardar_factura(sesion, serie_numero="F001-2", fecha_emision=date(2026, 10, 5))
    guardar_factura(sesion, serie_numero="F001-3", fecha_emision=date(2026, 10, 25),
                    razon_social="Comercial Andina del Sur S.A.C")  # la IA omitió el punto
    # OBSERVADA: no debe sumarse
    guardar_factura(sesion, estado="OBSERVADA", serie_numero="F001-4", fecha_emision=date(2026, 10, 6))

    cuerpo = cliente.get("/resumen").json()

    por_mes = {(m["mes"], m["moneda"]): m for m in cuerpo["por_mes"]}
    assert set(por_mes) == {("2026-09", "PEN"), ("2026-10", "PEN")}
    assert por_mes[("2026-10", "PEN")]["cantidad"] == 2
    assert Decimal(por_mes[("2026-10", "PEN")]["total"]) == Decimal("1380.60")
    assert Decimal(por_mes[("2026-10", "PEN")]["igv"]) == Decimal("210.60")

    # Un solo proveedor aunque la razón social venga escrita distinta
    assert len(cuerpo["por_proveedor"]) == 1
    proveedor = cuerpo["por_proveedor"][0]
    assert proveedor["ruc_emisor"] == "20601234565"
    assert proveedor["cantidad"] == 3
    assert Decimal(proveedor["total"]) == Decimal("2070.90")


def test_no_mezcla_monedas(cliente, sesion):
    guardar_factura(sesion, serie_numero="F001-1", moneda="PEN")
    guardar_factura(sesion, serie_numero="F001-2", moneda="USD")

    cuerpo = cliente.get("/resumen").json()

    assert {m["moneda"] for m in cuerpo["por_mes"]} == {"PEN", "USD"}
    assert len(cuerpo["por_proveedor"]) == 2
