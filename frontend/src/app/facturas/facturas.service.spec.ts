import { HttpErrorResponse, provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';

import { FacturasService, mensajeDeError } from './facturas.service';

describe('FacturasService', () => {
  let servicio: FacturasService;
  let http: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    servicio = TestBed.inject(FacturasService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify()); // falla si quedó alguna petición sin revisar

  it('listar envía solo los filtros que tienen valor', () => {
    servicio.listar({ estado: 'VALIDA', ruc: '' }).subscribe();

    const peticion = http.expectOne((r) => r.url.endsWith('/facturas'));
    expect(peticion.request.params.get('estado')).toBe('VALIDA');
    expect(peticion.request.params.has('ruc')).toBeFalse();
    peticion.flush([]);
  });

  it('subir envía el PDF como multipart con el campo "archivo"', () => {
    const pdf = new File(['%PDF'], 'factura.pdf', { type: 'application/pdf' });

    servicio.subir(pdf).subscribe();

    const peticion = http.expectOne((r) => r.url.endsWith('/facturas'));
    expect(peticion.request.method).toBe('POST');
    expect((peticion.request.body as FormData).get('archivo')).toBe(pdf);
    peticion.flush({});
  });

  it('mensajeDeError usa el "detail" de FastAPI', () => {
    const error = new HttpErrorResponse({
      status: 409,
      error: { detail: 'La factura ya fue registrada' },
    });

    expect(mensajeDeError(error)).toBe('La factura ya fue registrada');
  });

  it('mensajeDeError avisa si la API está apagada', () => {
    expect(mensajeDeError(new HttpErrorResponse({ status: 0 }))).toContain('No se pudo conectar');
  });
});
