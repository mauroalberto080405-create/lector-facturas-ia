# Frontend — Lector de facturas con IA

Interfaz web en **Angular 20** para la API del proyecto (ver el [README principal](../README.md)).

## Pantallas

- **Subir PDF** (`/subir`): arrastrar o elegir una factura; muestra si quedó `VALIDA` u `OBSERVADA`,
  sus observaciones, ítems y totales.
- **Facturas** (`/facturas`): listado con filtros por RUC, estado y fechas; detalle al hacer clic.
- **Resumen** (`/resumen`): totales de las facturas válidas por moneda, mes y proveedor.

## Estructura

```
src/app/
├── facturas/
│   ├── factura.model.ts        # interfaces que reflejan los esquemas de la API
│   ├── facturas.service.ts     # única puerta a la API (HttpClient)
│   └── factura-detalle/        # componente presentacional reutilizable
└── paginas/
    ├── subir/                  # carga del PDF
    ├── listado/                # tabla + filtros (formulario reactivo)
    └── resumen/                # tarjetas, tablas y barras (computed)
```

Componentes standalone, signals, control de flujo `@if`/`@for` y rutas con carga diferida.
La URL de la API está en `src/environments/`.

## Ejecutar

Con la API corriendo en `http://localhost:8000`:

```bash
npm install
npx ng serve -o          # http://localhost:4200
```

## Tests

```bash
npm test                 # Karma + Jasmine, con Chrome
npm run test:ci          # sin ventana (lo usa GitHub Actions)
```

Los tests simulan la API con `HttpTestingController`; no necesitan el backend.
