import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Factura } from '../../facturas/factura.model';
import { Subir } from './subir';

const FACTURA_OBSERVADA: Factura = {
  id: 7,
  ruc_emisor: '20601234565',
  razon_social: 'Comercial Andina del Sur S.A.C.',
  serie_numero: 'F001-00000123',
  fecha_emision: '2026-10-05',
  moneda: 'PEN',
  subtotal: '585.00',
  igv: '105.30',
  total: '700.00',
  estado: 'OBSERVADA',
  errores: ['El total no coincide con subtotal + IGV'],
  creado_en: '2026-11-16T10:00:00',
  items: [{ id: 1, descripcion: 'Papel bond A4', cantidad: '10', precio_unitario: '58.50' }],
};

describe('Subir', () => {
  let fixture: ComponentFixture<Subir>;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [Subir],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    fixture = TestBed.createComponent(Subir);
    http = TestBed.inject(HttpTestingController);
    fixture.detectChanges();
  });

  /** Simula que el usuario elige un archivo en el input. */
  function elegirArchivo(nombre: string): void {
    const input: HTMLInputElement = fixture.nativeElement.querySelector('input[type=file]');
    const datos = new DataTransfer();
    datos.items.add(new File(['%PDF'], nombre));
    input.files = datos.files;
    input.dispatchEvent(new Event('change'));
    fixture.detectChanges();
  }

  function boton(): HTMLButtonElement {
    return fixture.nativeElement.querySelector('button');
  }

  it('el botón está deshabilitado hasta elegir un PDF', () => {
    expect(boton().disabled).toBeTrue();
    elegirArchivo('factura.pdf');
    expect(boton().disabled).toBeFalse();
  });

  it('rechaza archivos que no son PDF sin llamar a la API', () => {
    elegirArchivo('foto.png');

    expect(fixture.nativeElement.textContent).toContain('Solo se aceptan archivos PDF');
    expect(boton().disabled).toBeTrue();
  });

  it('muestra la factura OBSERVADA con sus errores', () => {
    elegirArchivo('factura.pdf');
    boton().click();
    http.expectOne((r) => r.method === 'POST').flush(FACTURA_OBSERVADA);
    fixture.detectChanges();

    const texto = fixture.nativeElement.textContent;
    expect(texto).toContain('OBSERVADA');
    expect(texto).toContain('El total no coincide');
    expect(texto).toContain('F001-00000123');
  });

  it('muestra el mensaje de la API si la factura está duplicada (409)', () => {
    elegirArchivo('factura.pdf');
    boton().click();
    http
      .expectOne((r) => r.method === 'POST')
      .flush(
        { detail: 'La factura ya fue registrada (id 3)' },
        { status: 409, statusText: 'Conflict' },
      );
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('La factura ya fue registrada (id 3)');
    expect(boton().disabled).toBeFalse(); // puede reintentar
  });
});
