import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';

import { App } from './app';

describe('App', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [App],
      providers: [provideRouter([]), provideHttpClient(), provideHttpClientTesting()],
    });
  });

  it('muestra "API conectada" cuando /salud responde', () => {
    const fixture = TestBed.createComponent(App);
    TestBed.inject(HttpTestingController)
      .expectOne((r) => r.url.endsWith('/salud'))
      .flush({ estado: 'ok' });
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('API conectada');
  });

  it('muestra "API sin conexión" si /salud falla', () => {
    const fixture = TestBed.createComponent(App);
    TestBed.inject(HttpTestingController)
      .expectOne((r) => r.url.endsWith('/salud'))
      .error(new ProgressEvent('error'));
    fixture.detectChanges();

    expect(fixture.nativeElement.textContent).toContain('API sin conexión');
  });
});
