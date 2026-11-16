import { DecimalPipe } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';

import { Moneda, Resumen as DatosResumen } from '../../facturas/factura.model';
import { FacturasService, mensajeDeError } from '../../facturas/facturas.service';

interface TotalMoneda {
  moneda: Moneda;
  cantidad: number;
  total: number;
  igv: number;
}

@Component({
  selector: 'app-resumen',
  imports: [DecimalPipe],
  templateUrl: './resumen.html',
  styleUrl: './resumen.css',
})
export class Resumen implements OnInit {
  private readonly servicio = inject(FacturasService);

  protected readonly datos = signal<DatosResumen | null>(null);
  protected readonly cargando = signal(true);
  protected readonly error = signal<string | null>(null);

  /**
   * Tarjetas de arriba: un total por moneda (nunca se suman soles con dólares).
   * computed() se recalcula solo cuando cambia `datos`.
   */
  protected readonly totales = computed<TotalMoneda[]>(() => {
    const porMoneda = new Map<Moneda, TotalMoneda>();
    for (const fila of this.datos()?.por_mes ?? []) {
      const t = porMoneda.get(fila.moneda) ?? {
        moneda: fila.moneda,
        cantidad: 0,
        total: 0,
        igv: 0,
      };
      t.cantidad += fila.cantidad;
      t.total += Number(fila.total); // solo para mostrar; los cálculos exactos están en la API
      t.igv += Number(fila.igv);
      porMoneda.set(fila.moneda, t);
    }
    return [...porMoneda.values()];
  });

  /** Mayor total por moneda, para dibujar las barras proporcionales de proveedores. */
  private readonly maximos = computed(() => {
    const max = new Map<Moneda, number>();
    for (const p of this.datos()?.por_proveedor ?? []) {
      max.set(p.moneda, Math.max(max.get(p.moneda) ?? 0, Number(p.total)));
    }
    return max;
  });

  ngOnInit(): void {
    this.servicio.resumen().subscribe({
      next: (datos) => {
        this.datos.set(datos);
        this.cargando.set(false);
      },
      error: (e) => {
        this.error.set(mensajeDeError(e));
        this.cargando.set(false);
      },
    });
  }

  protected porcentaje(total: string, moneda: Moneda): number {
    const max = this.maximos().get(moneda) ?? 0;
    return max ? (Number(total) / max) * 100 : 0;
  }

  protected simbolo(moneda: string): string {
    return moneda === 'USD' ? 'US$' : 'S/';
  }
}
