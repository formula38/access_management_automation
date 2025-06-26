import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: `
    <mat-toolbar color="primary">
      <span>Data Access Management System</span>
      <span style="flex: 1 1 auto;"></span>
      <button mat-button routerLink="/access-request">New Request</button>
      <button mat-button routerLink="/requests">Access Requests</button>
    </mat-toolbar>
    
    <div style="padding: 20px;">
      <router-outlet></router-outlet>
    </div>
  `,
  styles: [`
    :host {
      display: block;
      height: 100vh;
    }
    
    mat-toolbar {
      margin-bottom: 20px;
    }
  `]
})
export class AppComponent {
  title = 'Data Access Management System';
} 