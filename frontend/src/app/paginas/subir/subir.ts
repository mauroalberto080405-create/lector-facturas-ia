import { Component, inject, signal } from '@angular/core';

import { FacturaDetalle } from '../../facturas/factura-detalle/factura-detalle';
import { Factura } from '../../facturas/factura.model';
import { FacturasService, mensajeDeError } from '../../facturas/facturas.service';

@Component({
  selector: 'app-subir',
  imports: [FacturaDetalle],
  templateUrl: './subir.html',
  styleUrl: './subir.css',
})
export class Subir {
  private readonly servicio = inject(FacturasService);

  // Estado de la pantalla con signals: la vista se actualiza sola al cambiar.
  protected readonly archivo = signal<File | null>(null);
  protected readonly procesando = signal(false);
  protected readonly resultado = signal<Factura | null>(null);
  protected readonly error = signal<string | null>(null);
  protected readonly arrastrando = signal(false);

  protected elegir(evento: Event): void {
    const input = evento.target as HTMLInputElement;
    this.usarArchivo(input.files?.[0] ?? null);
    input.value = ''; // permite volver a elegir el mismo archivo
  }

  protected soltar(evento: DragEvent): void {
    evento.preventDefault(); // sin esto el navegador abre el PDF en la pestaña
    this.arrastrando.set(false);
    this.usarArchivo(evento.dataTransfer?.files[0] ?? null);
  }

  protected arrastrar(evento: DragEvent, encima: boolean): void {
    evento.preventDefault();
    this.arrastrando.set(encima);
  }

  protected procesar(): void {
    const archivo = this.archivo();
    if (!archivo || this.procesando()) return;

    this.procesando.set(true);
    this.error.set(null);
    this.resultado.set(null);

    this.servicio.subir(archivo).subscribe({
      next: (factura) => {
        this.resultado.set(factura);
        this.archivo.set(null);
        this.procesando.set(false);
      },
      error: (e) => {
        this.error.set(mensajeDeError(e));
        this.procesando.set(false);
      },
    });
  }

  private usarArchivo(archivo: File | null): void {
    this.error.set(null);
    if (!archivo) return;
    // Validación rápida en el navegador; la API vuelve a validar (nunca confiar solo en el front).
    if (!archivo.name.toLowerCase().endsWith('.pdf')) {
      this.error.set('Solo se aceptan archivos PDF.');
      return;
    }
    this.archivo.set(archivo);
    this.resultado.set(null);
  }
}
