from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ItemExtraido(BaseModel):
    descripcion: str = Field(min_length=1)
    cantidad: Decimal = Field(gt=0)
    precio_unitario: Decimal = Field(ge=0)


class FacturaExtraida(BaseModel):
    """Lo que la IA debe devolver. Pydantic valida TIPOS y FORMA, no reglas contables."""

    ruc_emisor: str
    razon_social: str
    serie_numero: str = Field(examples=["F001-00012345"])
    fecha_emision: date
    moneda: Literal["PEN", "USD"]
    subtotal: Decimal = Field(ge=0)
    igv: Decimal = Field(ge=0)
    total: Decimal = Field(ge=0)
    items: list[ItemExtraido]


class ItemRespuesta(ItemExtraido):
    model_config = ConfigDict(from_attributes=True)  # permite construirlo desde el modelo ORM

    id: int


class FacturaRespuesta(FacturaExtraida):
    """Lo que la API devuelve: los datos extraídos + lo que agrega el sistema."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    estado: Literal["VALIDA", "OBSERVADA"]
    errores: list[str]
    creado_en: datetime
    items: list[ItemRespuesta]


class TotalesPorMes(BaseModel):
    mes: str = Field(examples=["2026-10"])
    moneda: str
    cantidad: int
    total: Decimal
    igv: Decimal


class TotalesPorProveedor(BaseModel):
    ruc_emisor: str
    razon_social: str
    moneda: str
    cantidad: int
    total: Decimal
    igv: Decimal


class Resumen(BaseModel):
    """Totales de las facturas VALIDAS, separados por moneda (no se suman soles con dólares)."""

    por_mes: list[TotalesPorMes]
    por_proveedor: list[TotalesPorProveedor]
