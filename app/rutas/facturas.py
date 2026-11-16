from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.database import obtener_sesion
from app.extractores.base import ErrorExtraccion, ExtractorIA
from app.extractores.fabrica import obtener_extractor
from app.models import ESTADO_OBSERVADA, ESTADO_VALIDA, Factura, Item
from app.pdf import PDFInvalidoError, extraer_texto
from app.schemas import FacturaRespuesta
from app.validaciones import validar_factura

router = APIRouter(prefix="/facturas", tags=["facturas"])


@router.post("", response_model=FacturaRespuesta, status_code=status.HTTP_201_CREATED)
def subir_factura(
    archivo: UploadFile,
    sesion: Session = Depends(obtener_sesion),
    extractor: ExtractorIA = Depends(obtener_extractor),
) -> Factura:
    """Recibe un PDF, extrae sus datos con IA, los valida y los guarda."""
    # 1. PDF -> texto
    try:
        texto = extraer_texto(archivo.file.read())
    except PDFInvalidoError as error:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, str(error)) from error

    # 2. texto -> datos estructurados (IA)
    try:
        datos = extractor.extraer(texto)
    except ErrorExtraccion as error:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(error)) from error

    # 3. ¿Ya existe? (mismo RUC + serie y número)
    existente = sesion.scalar(
        select(Factura).where(
            Factura.ruc_emisor == datos.ruc_emisor,
            Factura.serie_numero == datos.serie_numero,
        )
    )
    if existente:
        raise HTTPException(
            status.HTTP_409_CONFLICT, f"La factura ya fue registrada (id {existente.id})"
        )

    # 4. Reglas contables: si fallan se guarda igual, pero OBSERVADA
    errores = validar_factura(datos)
    factura = Factura(
        **datos.model_dump(exclude={"items"}),
        estado=ESTADO_OBSERVADA if errores else ESTADO_VALIDA,
        errores=errores,
        items=[Item(**item.model_dump()) for item in datos.items],
    )
    sesion.add(factura)
    try:
        sesion.commit()
    except IntegrityError as error:  # otra petición guardó la misma factura un instante antes
        sesion.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "La factura ya fue registrada") from error
    sesion.refresh(factura)
    return factura


@router.get("", response_model=list[FacturaRespuesta])
def listar_facturas(
    ruc: str | None = None,
    estado: Literal["VALIDA", "OBSERVADA"] | None = None,
    desde: date | None = Query(None, description="Fecha de emisión mínima (AAAA-MM-DD)"),
    hasta: date | None = Query(None, description="Fecha de emisión máxima (AAAA-MM-DD)"),
    sesion: Session = Depends(obtener_sesion),
) -> list[Factura]:
    """Lista facturas; cada filtro es opcional y se combinan con AND."""
    if desde and hasta and desde > hasta:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "'desde' no puede ser posterior a 'hasta'")

    consulta = select(Factura).options(selectinload(Factura.items))
    if ruc:
        consulta = consulta.where(Factura.ruc_emisor == ruc)
    if estado:
        consulta = consulta.where(Factura.estado == estado)
    if desde:
        consulta = consulta.where(Factura.fecha_emision >= desde)
    if hasta:
        consulta = consulta.where(Factura.fecha_emision <= hasta)

    consulta = consulta.order_by(Factura.fecha_emision.desc(), Factura.id.desc())
    return list(sesion.scalars(consulta))


@router.get("/{factura_id}", response_model=FacturaRespuesta)
def obtener_factura(factura_id: int, sesion: Session = Depends(obtener_sesion)) -> Factura:
    factura = sesion.get(Factura, factura_id)
    if factura is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"No existe la factura {factura_id}")
    return factura
