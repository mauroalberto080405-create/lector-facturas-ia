"""Prueba manual contra la IA REAL configurada en .env (Ollama por defecto).

Uso (desde la raíz del proyecto):
    python -m scripts.probar_extractor                      -> todas las facturas de ejemplo
    python -m scripts.probar_extractor facturas_ejemplo/factura_03_igv_incorrecto.pdf
"""

import sys
import time
from pathlib import Path

from app.config import config
from app.extractores.base import ErrorExtraccion
from app.extractores.fabrica import crear_extractor
from app.pdf import extraer_texto
from app.validaciones import validar_factura


def main(rutas: list[str]) -> None:
    archivos = [Path(r) for r in rutas] or sorted(Path("facturas_ejemplo").glob("*.pdf"))
    extractor = crear_extractor(config)
    print(f"Proveedor: {config.ia_proveedor}")

    for archivo in archivos:
        inicio = time.perf_counter()
        try:
            factura = extractor.extraer(extraer_texto(archivo.read_bytes()))
        except ErrorExtraccion as error:
            print(f"\n=== {archivo.name}: ERROR DE EXTRACCIÓN -> {error}")
            continue
        segundos = time.perf_counter() - inicio

        print(f"\n=== {archivo.name} ({segundos:.1f} s)")
        print(factura.model_dump_json(indent=2))
        errores = validar_factura(factura)
        print("Validación:", "OK" if not errores else errores)


if __name__ == "__main__":
    main(sys.argv[1:])
