import { DecimalPipe } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule } from '@angular/forms';

import { FacturaDetalle } from '../../facturas/factura-detalle/factura-detalle';
import { Factura, FiltrosFacturas } from '../../facturas/factura.model';
import { FacturasService, mensajeDeError } from '../../facturas/facturas.service';

@Component({
  selector: 'app-listado',
  imports: [ReactiveFormsModule, DecimalPipe, FacturaDetalle],
  templateUrl: './listado.html',
  styleUrl: './listado.css',
})
export class Listado implements OnInit {
  private readonly servicio = inject(FacturasService);

  // Formulario reactivo: los nombres coinciden con los query params de GET /facturas.
  protected readonly filtros = inject(FormBuilder).nonNullable.group({
    ruc: '',
    estado: '' as FiltrosFacturas['estado'],
    desde: '',
    hasta: '',
  });

  protected readonly facturas = signal<Factura[]>([]);
  protected readonly cargando = signal(false);
  protected readonly error = signal<string | null>(null);
  protected readonly seleccionada = signal<Factura | null>(null);

  ngOnInit(): void {
    this.buscar();
  }

  protected buscar(): void {
    this.cargando.set(true);
    this.error.set(null);
    this.seleccionada.set(null);

    this.servicio.listar(this.filtros.getRawValue()).subscribe({
      next: (facturas) => {
        this.facturas.set(facturas);
        this.cargando.set(false);
      },
      error: (e) => {
        this.error.set(mensajeDeError(e));
        this.facturas.set([]);
        this.cargando.set(false);
      },
    });
  }

  protected limpiar(): void {
    this.filtros.reset();
    this.buscar();
  }

  /** Clic en una fila: abre su detalle; clic otra vez: lo cierra. */
  protected alternar(factura: Factura): void {
    this.seleccionada.update((actual) => (actual?.id === factura.id ? null : factura));
  }

  protected simbolo(moneda: string): string {
    return moneda === 'USD' ? 'US$' : 'S/';
  }
}
