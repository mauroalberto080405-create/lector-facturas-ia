from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

ESTADO_VALIDA = "VALIDA"
ESTADO_OBSERVADA = "OBSERVADA"


class Factura(Base):
    __tablename__ = "facturas"
    # La base de datos impide duplicados aunque lleguen dos peticiones a la vez.
    __table_args__ = (UniqueConstraint("ruc_emisor", "serie_numero", name="uq_factura_ruc_serie"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    ruc_emisor: Mapped[str] = mapped_column(String(20), index=True)
    razon_social: Mapped[str] = mapped_column(String(200))
    serie_numero: Mapped[str] = mapped_column(String(30))
    fecha_emision: Mapped[date] = mapped_column(Date, index=True)
    moneda: Mapped[str] = mapped_column(String(3))
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    igv: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    estado: Mapped[str] = mapped_column(String(10), index=True)
    errores: Mapped[list[str]] = mapped_column(JSON, default=list)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    items: Mapped[list["Item"]] = relationship(
        back_populates="factura", cascade="all, delete-orphan", order_by="Item.id"
    )


class Item(Base):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(primary_key=True)
    factura_id: Mapped[int] = mapped_column(ForeignKey("facturas.id", ondelete="CASCADE"))
    descripcion: Mapped[str] = mapped_column(String(300))
    cantidad: Mapped[Decimal] = mapped_column(Numeric(12, 3))
    precio_unitario: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    factura: Mapped[Factura] = relationship(back_populates="items")
