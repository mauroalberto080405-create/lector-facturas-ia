from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import config

# El engine administra el pool de conexiones; se crea una vez para toda la app.
# pool_pre_ping: antes de usar una conexión del pool comprueba que siga viva.
# Las bases en la nube (Neon) cierran conexiones inactivas; sin esto, la primera
# petición después de un rato fallaría.
engine = create_engine(config.database_url, pool_pre_ping=True)
SesionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    """Clase padre de todas las tablas (modelos ORM)."""


def obtener_sesion() -> Iterator[Session]:
    """Dependencia de FastAPI: una sesión por petición, cerrada siempre al terminar."""
    with SesionLocal() as sesion:
        yield sesion
