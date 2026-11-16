import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Resumen as DatosResumen } from '../../facturas/factura.model';
import { Resumen } from './resumen';

const DATOS: DatosResumen = {
  por_mes: [
    { mes: '2026-10', moneda: 'PEN', cantidad: 2, total: '1380.60', igv: '210.60' },
    { mes: '2026-11', moneda: 'PEN', cantidad: 1, total: '100.00', igv: '15.25' },
    { mes: '2026-11', moneda: 'USD', cantidad: 1, total: '500.00', igv: '76.27' },
  ],
  por_proveedor: [
    {
      ruc_emisor: '20601234565',
      razon_social: 'Comercial Andina',
      moneda: 'PEN',
      cantidad: 3,
      total: '1480.60',
      igv: '225.85',
    },
    {
      ruc_emisor: '20712345676',
      razon_social: 'Distribuidora Norte',
      moneda: 'USD',
      cantidad: 1,
      total: '500.00',
      igv: '76.27',
    },
  ],
};

describe('Resumen', () => {
  let fixture: ComponentFixture<Resumen>;
  let http: HttpTestingController;
  let pagina: HTMLElement;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [Resumen],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    fixture = TestBed.createComponent(Resumen);
    http = TestBed.inject(HttpTestingController);
    pagina = fixture.nativeElement;
    fixture.detectChanges();
  });

  function responder(datos: DatosResumen): void {
    http.expectOne((r) => r.url.endsWith('/resumen')).flush(datos);
    fixture.detectChanges();
  }

  it('muestra un total por moneda, sin sumar soles con dólares', () => {
    responder(DATOS);

    const tarjetas = [...pagina.querySelectorAll('.tarjeta')].map((t) => t.textContent);
    expect(tarjetas.length).toBe(2);
    expect(tarjetas[0]).toContain('S/ 1,480.60');
    expect(tarjetas[0]).toContain('3 factura(s)');
    expect(tarjetas[1]).toContain('US$ 500.00');
  });

  it('cada moneda tiene su propia escala en las barras de proveedores', () => {
    responder(DATOS);

    const barras = [...pagina.querySelectorAll<HTMLElement>('.barra span')].map(
      (b) => b.style.width,
    );
    expect(barras).toEqual(['100%', '100%']); // cada uno es el mayor de su moneda
  });

  it('avisa cuando aún no hay facturas válidas', () => {
    responder({ por_mes: [], por_proveedor: [] });

    expect(pagina.textContent).toContain('Aún no hay facturas válidas');
  });
});
