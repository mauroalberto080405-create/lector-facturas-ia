from datetime import date
from decimal import Decimal

import pytest

from app.schemas import ItemExtraido
from app.validaciones import validar_factura, validar_igv, validar_ruc
from tests.datos import factura_valida

HOY = date(2026, 11, 15)


def test_factura_correcta_no_tiene_errores():
    assert validar_factura(factura_valida(), hoy=HOY) == []


@pytest.mark.parametrize("ruc", ["20601234565", "20555123451", "20712345676"])
def test_ruc_valido(ruc):
    assert validar_ruc(ruc) is None


@pytest.mark.parametrize(
    "ruc, fragmento",
    [
        ("2060123456", "11 dígitos"),         # 10 dígitos
        ("2060123456A", "11 dígitos"),        # letra
        ("20601234569", "dígito verificador"),  # verificador incorrecto
    ],
)
def test_ruc_invalido(ruc, fragmento):
    assert fragmento in validar_ruc(ruc)


def test_igv_dentro_de_tolerancia_por_redondeo():
    assert validar_igv(Decimal("585.00"), Decimal("105.34")) is None


def test_igv_incorrecto():
    errores = validar_factura(
        factura_valida(subtotal=Decimal("3000.00"), igv=Decimal("500.00"), total=Decimal("3500.00"),
                       items=[ItemExtraido(descripcion="Auditoría", cantidad=1, precio_unitario=Decimal("3000.00"))]),
        hoy=HOY,
    )
    assert len(errores) == 1
    assert "IGV" in errores[0]


def test_total_no_cuadra():
    errores = validar_factura(factura_valida(total=Decimal("700.00")), hoy=HOY)
    assert errores == ["Subtotal 585.00 + IGV 105.30 = 690.30, pero el total es 700.00"]


def test_items_no_suman_el_subtotal():
    errores = validar_factura(
        factura_valida(items=[ItemExtraido(descripcion="Algo", cantidad=1, precio_unitario=Decimal("500.00"))]),
        hoy=HOY,
    )
    assert any("suma de los ítems" in e for e in errores)


def test_fecha_futura():
    errores = validar_factura(factura_valida(fecha_emision=date(2026, 12, 1)), hoy=HOY)
    assert any("futura" in e for e in errores)


def test_junta_todos_los_errores_en_vez_de_parar_en_el_primero():
    factura = factura_valida(ruc_emisor="123", total=Decimal("1.00"), fecha_emision=date(2027, 1, 1))
    assert len(validar_factura(factura, hoy=HOY)) == 3
