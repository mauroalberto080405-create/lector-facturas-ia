"""Datos de prueba compartidos (ficticios)."""

from datetime import date
from decimal import Decimal

from app.models import Factura, Item
from app.schemas import FacturaExtraida, ItemExtraido


def factura_valida(**cambios) -> FacturaExtraida:
    """Datos de factura_01_correcta.pdf; `cambios` permite romper un campo a la vez."""
    datos = dict(
        ruc_emisor="20601234565",
        razon_social="Comercial Andina del Sur S.A.C.",
        serie_numero="F001-00000123",
        fecha_emision=date(2026, 10, 5),
        moneda="PEN",
        subtotal=Decimal("585.00"),
        igv=Decimal("105.30"),
        total=Decimal("690.30"),
        items=[
            ItemExtraido(descripcion="Papel bond A4 (millar)", cantidad=10, precio_unitario=Decimal("22.50")),
            ItemExtraido(descripcion="Tóner HP 85A", cantidad=2, precio_unitario=Decimal("180.00")),
        ],
    )
    datos.update(cambios)
    return FacturaExtraida(**datos)


def guardar_factura(sesion, estado: str = "VALIDA", **cambios) -> Factura:
    """Inserta una factura directo en la base (sin pasar por el PDF ni la IA)."""
    datos = factura_valida(**cambios)
    factura = Factura(
        **datos.model_dump(exclude={"items"}),
        estado=estado,
        errores=[] if estado == "VALIDA" else ["error de prueba"],
        items=[Item(**item.model_dump()) for item in datos.items],
    )
    sesion.add(factura)
    sesion.commit()
    return factura
