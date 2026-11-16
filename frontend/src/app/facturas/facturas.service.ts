import { HttpClient, HttpErrorResponse, HttpParams } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';

import { environment } from '../../environments/environment';
import { Factura, FiltrosFacturas, Resumen } from './factura.model';

/** Única puerta de entrada a la API: los componentes nunca arman URLs. */
@Injectable({ providedIn: 'root' })
export class FacturasService {
  private readonly http = inject(HttpClient);
  private readonly api = environment.apiUrl;

  salud(): Observable<{ estado: string }> {
    return this.http.get<{ estado: string }>(`${this.api}/salud`);
  }

  subir(archivo: File): Observable<Factura> {
    const datos = new FormData();
    datos.append('archivo', archivo); // mismo nombre que el parámetro de FastAPI
    return this.http.post<Factura>(`${this.api}/facturas`, datos);
  }

  listar(filtros: FiltrosFacturas = {}): Observable<Factura[]> {
    // Solo se envían los filtros con valor: "?estado=" daría 422 en la API.
    let params = new HttpParams();
    for (const [clave, valor] of Object.entries(filtros)) {
      if (valor) params = params.set(clave, valor);
    }
    return this.http.get<Factura[]>(`${this.api}/facturas`, { params });
  }

  obtener(id: number): Observable<Factura> {
    return this.http.get<Factura>(`${this.api}/facturas/${id}`);
  }

  resumen(): Observable<Resumen> {
    return this.http.get<Resumen>(`${this.api}/resumen`);
  }
}

/** Convierte un error HTTP en un mensaje para el usuario (FastAPI lo envía en "detail"). */
export function mensajeDeError(error: unknown): string {
  if (error instanceof HttpErrorResponse) {
    if (error.status === 0) return 'No se pudo conectar con la API. ¿Está encendida?';
    const detalle = error.error?.detail;
    if (typeof detalle === 'string') return detalle;
    return `Error ${error.status} al llamar a la API`;
  }
  return 'Error inesperado';
}
