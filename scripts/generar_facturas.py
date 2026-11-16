"""Genera facturas electrónicas FICTICIAS en PDF para probar la API.

Todos los RUC, empresas y montos son inventados.
Uso (desde la raíz del proyecto):  python scripts/generar_facturas.py
"""

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

CARPETA_SALIDA = Path(__file__).resolve().parent.parent / "facturas_ejemplo"
TASA_IGV = Decimal("0.18")
CENTIMOS = Decimal("0.01")
PESOS_RUC = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]


def completar_ruc(base: str) -> str:
    """Agrega el dígito verificador (módulo 11 de SUNAT) a los 10 primeros dígitos."""
    suma = sum(int(d) * p for d, p in zip(base, PESOS_RUC))
    resto = 11 - (suma % 11)
    digito = {10: 0, 11: 1}.get(resto, resto)
    return f"{base}{digito}"


@dataclass
class Item:
    descripcion: str
    cantidad: int
    precio_unitario: Decimal

    @property
    def importe(self) -> Decimal:
        return (self.cantidad * self.precio_unitario).quantize(CENTIMOS)


@dataclass
class Factura:
    archivo: str
    ruc_emisor: str
    razon_social: str
    serie_numero: str
    fecha: date
    moneda: str
    items: list[Item]
    # Para fabricar facturas con errores a propósito:
    subtotal_forzado: Decimal | None = None
    igv_forzado: Decimal | None = None
    cliente: str = field(default="Cliente Demo S.A.C. - RUC 20000000001")

    @property
    def subtotal(self) -> Decimal:
        if self.subtotal_forzado is not None:
            return self.subtotal_forzado
        return sum((i.importe for i in self.items), Decimal("0"))

    @property
    def igv(self) -> Decimal:
        if self.igv_forzado is not None:
            return self.igv_forzado
        return (self.subtotal * TASA_IGV).quantize(CENTIMOS)

    @property
    def total(self) -> Decimal:
        return self.subtotal + self.igv


def dinero(valor: Decimal, moneda: str) -> str:
    simbolo = "S/" if moneda == "PEN" else "US$"
    return f"{simbolo} {valor:,.2f}"


def dibujar(factura: Factura, ruta: Path) -> None:
    c = canvas.Canvas(str(ruta), pagesize=A4)
    ancho, alto = A4
    y = alto - 60

    # Emisor (izquierda)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, factura.razon_social)
    c.setFont("Helvetica", 9)
    c.drawString(50, y - 15, "Av. Ficticia 123, Lima - Perú")

    # Recuadro SUNAT (derecha)
    c.rect(ancho - 230, y - 50, 180, 70)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(ancho - 140, y + 5, f"RUC {factura.ruc_emisor}")
    c.drawCentredString(ancho - 140, y - 12, "FACTURA ELECTRÓNICA")
    c.drawCentredString(ancho - 140, y - 29, factura.serie_numero)

    # Datos generales
    y -= 90
    c.setFont("Helvetica", 10)
    c.drawString(50, y, f"Fecha de emisión: {factura.fecha.strftime('%d/%m/%Y')}")
    c.drawString(50, y - 15, f"Moneda: {factura.moneda}")
    c.drawString(50, y - 30, f"Cliente: {factura.cliente}")

    # Tabla de ítems
    y -= 65
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Cant.")
    c.drawString(100, y, "Descripción")
    c.drawRightString(430, y, "P. Unit.")
    c.drawRightString(540, y, "Importe")
    c.line(50, y - 5, 540, y - 5)
    c.setFont("Helvetica", 10)
    for item in factura.items:
        y -= 20
        c.drawString(50, y, str(item.cantidad))
        c.drawString(100, y, item.descripcion)
        c.drawRightString(430, y, f"{item.precio_unitario:,.2f}")
        c.drawRightString(540, y, f"{item.importe:,.2f}")

    # Totales
    y -= 40
    c.line(330, y + 15, 540, y + 15)
    for etiqueta, valor in [
        ("Op. gravada:", factura.subtotal),
        ("IGV (18%):", factura.igv),
        ("Importe total:", factura.total),
    ]:
        c.drawString(330, y, etiqueta)
        c.drawRightString(540, y, dinero(valor, factura.moneda))
        y -= 18

    c.setFont("Helvetica-Oblique", 8)
    c.drawString(50, 40, "Documento FICTICIO generado para pruebas. No tiene validez tributaria.")
    c.save()


FACTURAS = [
    Factura(  # 1. Correcta, en soles
        archivo="factura_01_correcta.pdf",
        ruc_emisor=completar_ruc("2060123456"),
        razon_social="Comercial Andina del Sur S.A.C.",
        serie_numero="F001-00000123",
        fecha=date(2026, 10, 5),
        moneda="PEN",
        items=[
            Item("Papel bond A4 (millar)", 10, Decimal("22.50")),
            Item("Tóner HP 85A", 2, Decimal("180.00")),
        ],
    ),
    Factura(  # 2. Correcta, en dólares
        archivo="factura_02_correcta_usd.pdf",
        ruc_emisor=completar_ruc("2055512345"),
        razon_social="Servicios Contables Rímac E.I.R.L.",
        serie_numero="F002-00004587",
        fecha=date(2026, 10, 18),
        moneda="USD",
        items=[
            Item("Licencia software contable anual", 1, Decimal("1200.00")),
            Item("Capacitación (horas)", 8, Decimal("45.00")),
        ],
    ),
    Factura(  # 3. Error: IGV mal calculado (debería ser 540.00)
        archivo="factura_03_igv_incorrecto.pdf",
        ruc_emisor=completar_ruc("2071234567"),
        razon_social="Distribuidora Pacífico Norte S.A.",
        serie_numero="F001-00000999",
        fecha=date(2026, 11, 3),
        moneda="PEN",
        items=[Item("Servicio de auditoría", 1, Decimal("3000.00"))],
        igv_forzado=Decimal("500.00"),
    ),
    Factura(  # 4. Error: los ítems suman 245.00 pero el subtotal dice 250.00
        archivo="factura_04_items_no_cuadran.pdf",
        ruc_emisor=completar_ruc("2049876543"),
        razon_social="Tecnología Inca Digital S.A.C.",
        serie_numero="F003-00000045",
        fecha=date(2026, 11, 7),
        moneda="PEN",
        items=[
            Item("Mouse inalámbrico", 5, Decimal("40.00")),
            Item("Pad para mouse", 3, Decimal("15.00")),
        ],
        subtotal_forzado=Decimal("250.00"),
    ),
    Factura(  # 5. Error: RUC con dígito verificador incorrecto
        archivo="factura_05_ruc_invalido.pdf",
        ruc_emisor=completar_ruc("2060123456")[:-1] + "9",
        razon_social="Comercial Andina del Sur S.A.C.",
        serie_numero="F001-00000124",
        fecha=date(2026, 11, 10),
        moneda="PEN",
        items=[Item("Archivador de palanca", 50, Decimal("17.00"))],
    ),
]


def main() -> None:
    CARPETA_SALIDA.mkdir(exist_ok=True)
    for factura in FACTURAS:
        ruta = CARPETA_SALIDA / factura.archivo
        dibujar(factura, ruta)
        print(f"{factura.archivo:35} RUC {factura.ruc_emisor}  total {factura.total}")


if __name__ == "__main__":
    main()
