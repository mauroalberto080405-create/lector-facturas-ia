// Espejo de los esquemas Pydantic de app/schemas.py.
// Los montos llegan como string ("690.30") porque la API usa Decimal:
// así no se pierden céntimos con los decimales binarios de JavaScript.

export type Estado = 'VALIDA' | 'OBSERVADA';
export type Moneda = 'PEN' | 'USD';

export interface Item {
  id: number;
  descripcion: string;
  cantidad: string;
  precio_unitario: string;
}

export interface Factura {
  id: number;
  ruc_emisor: string;
  razon_social: string;
  serie_numero: string;
  fecha_emision: string; // AAAA-MM-DD
  moneda: Moneda;
  subtotal: string;
  igv: string;
  total: string;
  estado: Estado;
  errores: string[];
  creado_en: string;
  items: Item[];
}

export interface FiltrosFacturas {
  ruc?: string;
  estado?: Estado | '';
  desde?: string;
  hasta?: string;
}

export interface TotalesPorMes {
  mes: string;
  moneda: Moneda;
  cantidad: number;
  total: string;
  igv: string;
}

export interface TotalesPorProveedor {
  ruc_emisor: string;
  razon_social: string;
  moneda: Moneda;
  cantidad: number;
  total: string;
  igv: string;
}

export interface Resumen {
  por_mes: TotalesPorMes[];
  por_proveedor: TotalesPorProveedor[];
}
