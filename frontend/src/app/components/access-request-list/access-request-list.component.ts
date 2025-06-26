import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-access-request-list',
  template: `
    <h2>Access Requests</h2>
    <table mat-table [dataSource]="requests" class="mat-elevation-z8" *ngIf="requests">
      <ng-container matColumnDef="id">
        <th mat-header-cell *matHeaderCellDef> ID </th>
        <td mat-cell *matCellDef="let req"> {{req.id}} </td>
      </ng-container>
      <ng-container matColumnDef="requester_email">
        <th mat-header-cell *matHeaderCellDef> Requester </th>
        <td mat-cell *matCellDef="let req"> {{req.requester_email}} </td>
      </ng-container>
      <ng-container matColumnDef="resource">
        <th mat-header-cell *matHeaderCellDef> Resource </th>
        <td mat-cell *matCellDef="let req"> {{req.resource}} </td>
      </ng-container>
      <ng-container matColumnDef="service_type">
        <th mat-header-cell *matHeaderCellDef> Service </th>
        <td mat-cell *matCellDef="let req"> {{req.service_type}} </td>
      </ng-container>
      <ng-container matColumnDef="access_level">
        <th mat-header-cell *matHeaderCellDef> Level </th>
        <td mat-cell *matCellDef="let req"> {{req.access_level}} </td>
      </ng-container>
      <ng-container matColumnDef="status">
        <th mat-header-cell *matHeaderCellDef> Status </th>
        <td mat-cell *matCellDef="let req"> {{req.status}} </td>
      </ng-container>
      <ng-container matColumnDef="actions">
        <th mat-header-cell *matHeaderCellDef> Actions </th>
        <td mat-cell *matCellDef="let req">
          <button mat-button color="primary" (click)="approve(req)" *ngIf="req.status === 'pending'">Approve</button>
          <button mat-button color="warn" (click)="reject(req)" *ngIf="req.status === 'pending'">Reject</button>
        </td>
      </ng-container>
      <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
      <tr mat-row *matRowDef="let row; columns: displayedColumns;"></tr>
    </table>
  `,
  styles: [`
    table {
      width: 100%;
      margin-top: 20px;
    }
    th.mat-header-cell, td.mat-cell {
      padding: 8px;
    }
  `]
})
export class AccessRequestListComponent implements OnInit {
  requests: any[] = [];
  displayedColumns: string[] = ['id', 'requester_email', 'resource', 'service_type', 'access_level', 'status', 'actions'];

  constructor(private http: HttpClient, private snackBar: MatSnackBar) {}

  ngOnInit() {
    this.loadRequests();
  }

  loadRequests() {
    this.http.get<any[]>('/api/access-requests').subscribe(
      data => this.requests = data,
      err => this.snackBar.open('Failed to load requests', 'Close', { duration: 3000 })
    );
  }

  approve(req: any) {
    const approver_email = prompt('Enter your email to approve:');
    if (!approver_email) return;
    this.http.put(`/api/access-requests/${req.id}/approve?approver_email=${encodeURIComponent(approver_email)}`, {}).subscribe(
      () => {
        this.snackBar.open('Request approved', 'Close', { duration: 2000 });
        this.loadRequests();
      },
      err => this.snackBar.open('Failed to approve', 'Close', { duration: 3000 })
    );
  }

  reject(req: any) {
    const rejector_email = prompt('Enter your email to reject:');
    if (!rejector_email) return;
    const reason = prompt('Enter rejection reason:');
    if (!reason) return;
    this.http.put(`/api/access-requests/${req.id}/reject?rejector_email=${encodeURIComponent(rejector_email)}&reason=${encodeURIComponent(reason)}`, {}).subscribe(
      () => {
        this.snackBar.open('Request rejected', 'Close', { duration: 2000 });
        this.loadRequests();
      },
      err => this.snackBar.open('Failed to reject', 'Close', { duration: 3000 })
    );
  }
} 