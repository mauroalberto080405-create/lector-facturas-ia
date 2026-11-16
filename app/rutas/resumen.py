from fastapi import APIRouter, Depends
from sqlalchemy import extract, func, select
from sqlalchemy.orm import Session

from app.database import obtener_sesion
from app.models import ESTADO_VALIDA, Factura
from app.schemas import Resumen, TotalesPorMes, TotalesPorProveedor

router = APIRouter(prefix="/resumen", tags=["resumen"])


@router.get("", response_model=Resumen)
def resumen(sesion: Session = Depends(obtener_sesion)) -> Resumen:
    """Total e IGV por mes y por proveedor. Solo facturas VALIDAS: las OBSERVADAS
    tienen montos que no cuadran y ensuciarían los totales."""
    anio = extract("year", Factura.fecha_emision).label("anio")
    mes = extract("month", Factura.fecha_emision).label("mes")
    cantidad = func.count(Factura.id).label("cantidad")
    total = func.sum(Factura.total).label("total")
    igv = func.sum(Factura.igv).label("igv")

    filas_mes = sesion.execute(
        select(anio, mes, Factura.moneda, cantidad, total, igv)
        .where(Factura.estado == ESTADO_VALIDA)
        .group_by(anio, mes, Factura.moneda)
        .order_by(anio, mes, Factura.moneda)
    ).all()

    filas_proveedor = sesion.execute(
        select(
            Factura.ruc_emisor,
            # Agrupamos por RUC (dato confiable) y no por razón social: la IA puede
            # devolver "S.A.C" en una factura y "S.A.C." en otra para la misma empresa.
            func.max(Factura.razon_social).label("razon_social"),
            Factura.moneda,
            cantidad,
            total,
            igv,
        )
        .where(Factura.estado == ESTADO_VALIDA)
        .group_by(Factura.ruc_emisor, Factura.moneda)
        .order_by(total.desc())
    ).all()

    return Resumen(
        por_mes=[
            TotalesPorMes(
                mes=f"{int(f.anio)}-{int(f.mes):02d}",
                moneda=f.moneda,
                cantidad=f.cantidad,
                total=f.total,
                igv=f.igv,
            )
            for f in filas_mes
        ],
        por_proveedor=[TotalesPorProveedor(**f._mapping) for f in filas_proveedor],
    )
