"""Fixtures compartidas. pytest carga este archivo automáticamente."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, obtener_sesion
from app.extractores.fabrica import obtener_extractor
from app.extractores.falso import ExtractorFalso
from app.main import app
from tests.datos import factura_valida


@pytest.fixture
def sesion():
    """Base SQLite en memoria, nueva y vacía para cada prueba."""
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine)() as sesion:
        yield sesion
    engine.dispose()


@pytest.fixture
def extractor() -> ExtractorFalso:
    """Extractor sin IA; cada prueba puede cambiar `extractor.factura`."""
    return ExtractorFalso(factura_valida())


@pytest.fixture
def cliente(sesion, extractor):
    """Cliente HTTP de prueba con la base y el extractor reemplazados."""
    app.dependency_overrides[obtener_sesion] = lambda: sesion
    app.dependency_overrides[obtener_extractor] = lambda: extractor
    yield TestClient(app)
    app.dependency_overrides.clear()
