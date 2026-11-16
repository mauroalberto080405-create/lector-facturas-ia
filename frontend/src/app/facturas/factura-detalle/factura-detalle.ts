import { DecimalPipe } from '@angular/common';
import { Component, input } from '@angular/core';

import { Factura } from '../factura.model';

/**
 * Muestra una factura completa: estado, errores, cabecera e ítems.
 * Es "tonto" (presentacional): solo recibe datos por input(), no llama a la API.
 * Lo reutilizan la pantalla Subir PDF y la de Facturas.
 */
@Component({
  selector: 'app-factura-detalle',
  imports: [DecimalPipe],
  templateUrl: './factura-detalle.html',
  styleUrl: './factura-detalle.css',
})
export class FacturaDetalle {
  readonly factura = input.required<Factura>();

  protected simbolo(moneda: string): string {
    return moneda === 'USD' ? 'US$' : 'S/';
  }
}
