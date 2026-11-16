import { Routes } from '@angular/router';

// loadComponent = carga diferida (lazy): el código de cada pantalla se descarga
// solo cuando el usuario entra a ella, así la primera carga es más liviana.
export const routes: Routes = [
  { path: '', pathMatch: 'full', redirectTo: 'subir' },
  {
    path: 'subir',
    title: 'Subir factura',
    loadComponent: () => import('./paginas/subir/subir').then((m) => m.Subir),
  },
  {
    path: 'facturas',
    title: 'Facturas',
    loadComponent: () => import('./paginas/listado/listado').then((m) => m.Listado),
  },
  {
    path: 'resumen',
    title: 'Resumen',
    loadComponent: () => import('./paginas/resumen/resumen').then((m) => m.Resumen),
  },
  { path: '**', redirectTo: 'subir' },
];
