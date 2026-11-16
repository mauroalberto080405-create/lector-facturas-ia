from fastapi.testclient import TestClient

from app.main import app

cliente = TestClient(app)


def test_salud_responde_ok():
    respuesta = cliente.get("/salud")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"estado": "ok"}


def test_raiz_redirige_a_la_documentacion():
    respuesta = cliente.get("/", follow_redirects=False)

    assert respuesta.status_code == 307
    assert respuesta.headers["location"] == "/docs"


def test_cors_permite_al_frontend_local():
    respuesta = cliente.get("/salud", headers={"Origin": "http://localhost:4200"})

    assert respuesta.headers["access-control-allow-origin"] == "http://localhost:4200"


def test_cors_no_permite_origenes_desconocidos():
    respuesta = cliente.get("/salud", headers={"Origin": "https://sitio-malicioso.com"})

    assert "access-control-allow-origin" not in respuesta.headers
