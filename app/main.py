from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app import models  # noqa: F401  (registra las tablas en Base.metadata)
from app.config import config
from app.database import Base, engine
from app.rutas import facturas, resumen


@asynccontextmanager
async def ciclo_de_vida(_: FastAPI) -> AsyncIterator[None]:
    # Al arrancar: crea las tablas que falten. (En un proyecto grande: migraciones con Alembic.)
    Base.metadata.create_all(engine)
    yield


app = FastAPI(
    title="Lector de facturas con IA",
    description="Extrae, valida y guarda facturas electrónicas peruanas (SUNAT) desde PDF.",
    version="0.1.0",
    lifespan=ciclo_de_vida,
)
# CORS: el front (localhost:4200) es otro "origen" que la API (localhost:8000);
# sin esto el NAVEGADOR bloquea las respuestas. Solo se permiten orígenes conocidos.
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origenes,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.include_router(facturas.router)
app.include_router(resumen.router)


@app.get("/", include_in_schema=False)
def inicio() -> RedirectResponse:
    """Quien abre la URL pública llega directo a la documentación interactiva."""
    return RedirectResponse("/docs")


@app.get("/salud")
def salud() -> dict[str, str]:
    """Endpoint de verificación: responde si la API está viva."""
    return {"estado": "ok"}
