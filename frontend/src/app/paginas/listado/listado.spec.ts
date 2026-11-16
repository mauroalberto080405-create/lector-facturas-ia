import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Factura } from '../../facturas/factura.model';
import { Listado } from './listado';

function factura(id: number, estado: Factura['estado']): Factura {
  return {
    id,
    ruc_emisor: '20601234565',
    razon_social: 'Comercial Andina del Sur S.A.C.',
    serie_numero: `F001-0000000${id}`,
    fecha_emision: '2026-10-05',
    moneda: 'PEN',
    subtotal: '100.00',
    igv: '18.00',
    total: '118.00',
    estado,
    errores: estado === 'OBSERVADA' ? ['IGV incorrecto'] : [],
    creado_en: '2026-11-16T10:00:00',
    items: [],
  };
}

describe('Listado', () => {
  let fixture: ComponentFixture<Listado>;
  let http: HttpTestingController;
  let pagina: HTMLElement;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [Listado],
      providers: [provideHttpClient(), provideHttpClientTesting()],
    });
    fixture = TestBed.createComponent(Listado);
    http = TestBed.inject(HttpTestingController);
    pagina = fixture.nativeElement;
    fixture.detectChanges(); // dispara ngOnInit -> primera búsqueda
  });

  afterEach(() => http.verify());

  it('al entrar lista todas las facturas sin filtros', () => {
    const peticion = http.expectOne((r) => r.url.endsWith('/facturas'));
    expect(peticion.request.params.keys()).toEqual([]);
    peticion.flush([factura(1, 'VALIDA'), factura(2, 'OBSERVADA')]);
    fixture.detectChanges();

    expect(pagina.querySelectorAll('tbody tr').length).toBe(2);
    expect(pagina.textContent).toContain('2 factura(s)');
  });

  it('envía los filtros del formulario a la API', () => {
    http.expectOne(() => true).flush([]);

    const select: HTMLSelectElement = pagina.querySelector('select')!;
    select.value = 'OBSERVADA';
    select.dispatchEvent(new Event('change'));
    pagina.querySelector('form')!.dispatchEvent(new Event('submit'));

    const peticion = http.expectOne((r) => r.url.endsWith('/facturas'));
    expect(peticion.request.params.get('estado')).toBe('OBSERVADA');
    peticion.flush([]);
  });

  it('al hacer clic en una fila muestra su detalle', () => {
    http.expectOne(() => true).flush([factura(2, 'OBSERVADA')]);
    fixture.detectChanges();

    (pagina.querySelector('tbody tr') as HTMLElement).click();
    fixture.detectChanges();

    expect(pagina.querySelector('app-factura-detalle')?.textContent).toContain('IGV incorrecto');
  });

  it('muestra el error de la API (por ejemplo, fechas invertidas)', () => {
    http
      .expectOne(() => true)
      .flush(
        { detail: "'desde' no puede ser posterior a 'hasta'" },
        { status: 400, statusText: 'Bad Request' },
      );
    fixture.detectChanges();

    expect(pagina.textContent).toContain("'desde' no puede ser posterior a 'hasta'");
  });
});
