import { Component, inject, signal } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';

import { FacturasService } from './facturas/facturas.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink, RouterLinkActive],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  /** null = comprobando, true = API viva, false = no responde */
  protected readonly apiConectada = signal<boolean | null>(null);

  constructor() {
    inject(FacturasService)
      .salud()
      .subscribe({
        next: () => this.apiConectada.set(true),
        error: () => this.apiConectada.set(false),
      });
  }
}
