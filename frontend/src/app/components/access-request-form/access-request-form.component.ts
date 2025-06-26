import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatSnackBar } from '@angular/material/snack-bar';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-access-request-form',
  template: `
    <mat-card>
      <mat-card-header>
        <mat-card-title>Access Request Form</mat-card-title>
        <mat-card-subtitle>Request access to Cloud SQL and Looker Studio resources</mat-card-subtitle>
      </mat-card-header>
      
      <mat-card-content>
        <form [formGroup]="accessRequestForm" (ngSubmit)="onSubmit()">
          <mat-form-field appearance="outline" style="width: 100%; margin-bottom: 16px;">
            <mat-label>Requester Email</mat-label>
            <input matInput formControlName="requesterEmail" placeholder="Enter your email">
            <mat-error *ngIf="accessRequestForm.get('requesterEmail')?.hasError('required')">
              Email is required
            </mat-error>
            <mat-error *ngIf="accessRequestForm.get('requesterEmail')?.hasError('email')">
              Please enter a valid email
            </mat-error>
          </mat-form-field>

          <mat-form-field appearance="outline" style="width: 100%; margin-bottom: 16px;">
            <mat-label>Resource</mat-label>
            <mat-select formControlName="resource">
              <mat-option value="sales-db">Sales Database</mat-option>
              <mat-option value="marketing-dashboard">Marketing Dashboard</mat-option>
              <mat-option value="finance-db">Finance Database</mat-option>
            </mat-select>
            <mat-error *ngIf="accessRequestForm.get('resource')?.hasError('required')">
              Resource is required
            </mat-error>
          </mat-form-field>

          <mat-form-field appearance="outline" style="width: 100%; margin-bottom: 16px;">
            <mat-label>Service Type</mat-label>
            <mat-select formControlName="serviceType">
              <mat-option value="cloudsql">Cloud SQL</mat-option>
              <mat-option value="looker_studio">Looker Studio</mat-option>
            </mat-select>
            <mat-error *ngIf="accessRequestForm.get('serviceType')?.hasError('required')">
              Service type is required
            </mat-error>
          </mat-form-field>

          <mat-form-field appearance="outline" style="width: 100%; margin-bottom: 16px;">
            <mat-label>Access Level</mat-label>
            <mat-select formControlName="accessLevel">
              <mat-option value="read_only">Read Only</mat-option>
              <mat-option value="read_write">Read/Write</mat-option>
              <mat-option value="admin">Admin</mat-option>
            </mat-select>
            <mat-error *ngIf="accessRequestForm.get('accessLevel')?.hasError('required')">
              Access level is required
            </mat-error>
          </mat-form-field>

          <mat-form-field appearance="outline" style="width: 100%; margin-bottom: 16px;">
            <mat-label>Requested Duration</mat-label>
            <mat-select formControlName="requestedDuration">
              <mat-option value="7d">7 days</mat-option>
              <mat-option value="30d">30 days</mat-option>
              <mat-option value="90d">90 days</mat-option>
              <mat-option value="180d">180 days</mat-option>
              <mat-option value="365d">365 days</mat-option>
            </mat-select>
            <mat-error *ngIf="accessRequestForm.get('requestedDuration')?.hasError('required')">
              Duration is required
            </mat-error>
          </mat-form-field>

          <mat-form-field appearance="outline" style="width: 100%; margin-bottom: 16px;">
            <mat-label>Justification</mat-label>
            <textarea matInput formControlName="justification" rows="4" 
                      placeholder="Please provide a business justification for this access request"></textarea>
            <mat-error *ngIf="accessRequestForm.get('justification')?.hasError('required')">
              Justification is required
            </mat-error>
          </mat-form-field>

          <div style="display: flex; gap: 16px; justify-content: flex-end;">
            <button mat-button type="button" (click)="resetForm()">Reset</button>
            <button mat-raised-button color="primary" type="submit" 
                    [disabled]="!accessRequestForm.valid || isSubmitting">
              <mat-spinner diameter="20" *ngIf="isSubmitting"></mat-spinner>
              {{ isSubmitting ? 'Submitting...' : 'Submit Request' }}
            </button>
          </div>
        </form>
      </mat-card-content>
    </mat-card>
  `,
  styles: [`
    mat-card {
      max-width: 600px;
      margin: 0 auto;
    }
    
    mat-card-header {
      margin-bottom: 24px;
    }
    
    .mat-mdc-form-field {
      margin-bottom: 16px;
    }
    
    button[type="submit"] {
      min-width: 120px;
    }
    
    mat-spinner {
      margin-right: 8px;
    }
  `]
})
export class AccessRequestFormComponent implements OnInit {
  accessRequestForm: FormGroup;
  isSubmitting = false;

  constructor(
    private fb: FormBuilder,
    private snackBar: MatSnackBar,
    private http: HttpClient
  ) {
    this.accessRequestForm = this.fb.group({
      requesterEmail: ['', [Validators.required, Validators.email]],
      resource: ['', Validators.required],
      serviceType: ['', Validators.required],
      accessLevel: ['', Validators.required],
      requestedDuration: ['', Validators.required],
      justification: ['', [Validators.required, Validators.minLength(10)]]
    });
  }

  ngOnInit(): void {
    // Initialize form with default values
    this.accessRequestForm.patchValue({
      serviceType: 'cloudsql',
      accessLevel: 'read_only',
      requestedDuration: '30d'
    });
  }

  onSubmit(): void {
    if (this.accessRequestForm.valid) {
      this.isSubmitting = true;
      const formValue = this.accessRequestForm.value;
      // Map form fields to backend API fields
      const payload = {
        requester_email: formValue.requesterEmail,
        resource: formValue.resource,
        service_type: formValue.serviceType,
        access_level: formValue.accessLevel,
        requested_duration: formValue.requestedDuration,
        justification: formValue.justification
      };
      this.http.post('http://localhost:8000/api/access-requests', payload).subscribe({
        next: (response) => {
          this.snackBar.open('Access request submitted successfully!', 'Close', {
            duration: 3000,
            horizontalPosition: 'center',
            verticalPosition: 'top'
          });
          this.isSubmitting = false;
          this.resetForm();
        },
        error: (error) => {
          this.snackBar.open('Failed to submit access request.', 'Close', {
            duration: 3000,
            horizontalPosition: 'center',
            verticalPosition: 'top'
          });
          this.isSubmitting = false;
        }
      });
    }
  }

  resetForm(): void {
    this.accessRequestForm.reset();
    this.accessRequestForm.patchValue({
      serviceType: 'cloudsql',
      accessLevel: 'read_only',
      requestedDuration: '30d'
    });
  }
} 