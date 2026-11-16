"""Reglas contables de una factura SUNAT.

Cada regla devuelve un mensaje de error o None, para poder JUNTAR todos los
errores de una factura en vez de detenerse en el primero.
"""

from datetime import date
from decimal import Decimal

from app.schemas import FacturaExtraida, ItemExtraido

TASA_IGV = Decimal("0.18")
TOLERANCIA = Decimal("0.05")
CENTIMOS = Decimal("0.01")
PESOS_RUC = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]


def validar_ruc(ruc: str) -> str | None:
    if len(ruc) != 11 or not ruc.isdigit():
        return f"RUC {ruc!r} debe tener exactamente 11 dígitos"

    suma = sum(int(d) * p for d, p in zip(ruc[:10], PESOS_RUC))
    resto = 11 - (suma % 11)
    esperado = {10: 0, 11: 1}.get(resto, resto)
    if int(ruc[10]) != esperado:
        return f"RUC {ruc} tiene dígito verificador inválido (esperado {esperado})"
    return None


def validar_igv(subtotal: Decimal, igv: Decimal) -> str | None:
    esperado = (subtotal * TASA_IGV).quantize(CENTIMOS)
    if abs(esperado - igv) > TOLERANCIA:
        return f"IGV {igv} no coincide con el 18 % de {subtotal} ({esperado})"
    return None


def validar_total(subtotal: Decimal, igv: Decimal, total: Decimal) -> str | None:
    if abs(subtotal + igv - total) > TOLERANCIA:
        return f"Subtotal {subtotal} + IGV {igv} = {subtotal + igv}, pero el total es {total}"
    return None


def validar_items(items: list[ItemExtraido], subtotal: Decimal) -> str | None:
    suma = sum((i.cantidad * i.precio_unitario for i in items), Decimal("0")).quantize(CENTIMOS)
    if abs(suma - subtotal) > TOLERANCIA:
        return f"La suma de los ítems ({suma}) no coincide con el subtotal ({subtotal})"
    return None


def validar_fecha(fecha: date, hoy: date) -> str | None:
    if fecha > hoy:
        return f"La fecha de emisión {fecha} es futura"
    return None


def validar_factura(factura: FacturaExtraida, hoy: date | None = None) -> list[str]:
    """Aplica todas las reglas y devuelve la lista de errores (vacía = factura válida)."""
    hoy = hoy or date.today()
    errores = [
        validar_ruc(factura.ruc_emisor),
        validar_igv(factura.subtotal, factura.igv),
        validar_total(factura.subtotal, factura.igv, factura.total),
        validar_items(factura.items, factura.subtotal),
        validar_fecha(factura.fecha_emision, hoy),
    ]
    return [e for e in errores if e is not None]
