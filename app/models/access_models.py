from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator, model_validator
from pydantic.types import UUID4
import uuid


class DataSensitivity(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class AccessLevel(str, Enum):
    READ_ONLY = "read_only"
    READ_WRITE = "read_write"
    ADMIN = "admin"


class RequestStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    REVOKED = "revoked"


class ServiceType(str, Enum):
    CLOUDSQL = "cloudsql"
    LOOKER_STUDIO = "looker_studio"
    BIGQUERY = "bigquery"


class ApprovalType(str, Enum):
    USER = "user"
    ROLE = "role"
    MANAGER = "manager"
    DATA_OWNER = "data_owner"


class TimeRestriction(BaseModel):
    start_time: str = Field(..., description="Start time in HH:MM format")
    end_time: str = Field(..., description="End time in HH:MM format")
    timezone: str = Field(default="UTC", description="Timezone")
    days_of_week: List[str] = Field(default=["monday", "tuesday", "wednesday", "thursday", "friday"])

    @validator('start_time', 'end_time')
    def validate_time_format(cls, v):
        try:
            datetime.strptime(v, "%H:%M")
            return v
        except ValueError:
            raise ValueError("Time must be in HH:MM format")


class AccessCondition(BaseModel):
    department: Optional[str] = None
    data_sensitivity: Optional[DataSensitivity] = None
    location: Optional[str] = None
    job_level: Optional[str] = None
    contract_type: Optional[str] = None
    security_clearance: Optional[str] = None
    time_restrictions: Optional[TimeRestriction] = None
    ip_restrictions: Optional[List[str]] = None
    mfa_required: bool = False
    justification_required: bool = False


class Approver(BaseModel):
    type: ApprovalType
    value: str = Field(..., description="User email, role name, etc.")
    order: int = Field(..., description="Approval order (1 = first)")


class ApprovalWorkflow(BaseModel):
    approval_required: bool = True
    approvers: Optional[List[Approver]] = None
    auto_approve_conditions: Optional[List[Dict[str, Any]]] = None
    escalation: Optional[Dict[str, Any]] = None


class AuditSettings(BaseModel):
    enabled: bool = True
    log_level: str = Field(default="detailed", description="basic, detailed, verbose")
    retention_days: int = 365
    alerts: Optional[List[Dict[str, Any]]] = None


class ComplianceSettings(BaseModel):
    regulations: Optional[List[str]] = None
    data_classification: Optional[DataSensitivity] = None
    encryption_required: bool = True
    access_logging_required: bool = True


class NotificationSettings(BaseModel):
    access_granted: Optional[Dict[str, Any]] = None
    access_revoked: Optional[Dict[str, Any]] = None
    access_expiring: Optional[Dict[str, Any]] = None


class ServiceConfig(BaseModel):
    instance: Optional[str] = None
    database: Optional[str] = None
    dashboard_id: Optional[str] = None
    gcp_iam_bindings: Optional[List[Dict[str, Any]]] = None


class AccessPolicy(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    resource: str = Field(..., description="Resource identifier")
    resource_type: ServiceType
    roles: List[Dict[str, Any]] = Field(..., description="Array of roles")
    approval_workflow: Optional[ApprovalWorkflow] = None
    access_duration: str = Field(..., description="How long access lasts")
    access_duration_options: Optional[List[str]] = None
    renewal: Optional[Dict[str, Any]] = None
    audit: Optional[AuditSettings] = None
    compliance: Optional[ComplianceSettings] = None
    notifications: Optional[NotificationSettings] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None
    enabled: bool = True
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('access_duration')
    def validate_duration_format(cls, v):
        valid_suffixes = ['d', 'w', 'm', 'y']
        if not any(v.endswith(suffix) for suffix in valid_suffixes):
            raise ValueError("Duration must end with d (days), w (weeks), m (months), or y (years)")
        return v


class AccessRequest(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    requester_email: str = Field(..., description="Email of the person requesting access")
    resource: str = Field(..., description="Resource they want access to")
    service_type: ServiceType
    access_level: AccessLevel
    justification: str = Field(..., description="Business justification for access")
    requested_duration: str = Field(..., description="How long access is needed")
    status: RequestStatus = RequestStatus.PENDING
    approvers: List[str] = Field(default_factory=list)
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    rejected_by: Optional[str] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    ai_risk_score: Optional[float] = None
    ai_suggestions: Optional[List[str]] = None

    @validator('requested_duration')
    def validate_duration_format(cls, v):
        valid_suffixes = ['d', 'w', 'm', 'y']
        if not any(v.endswith(suffix) for suffix in valid_suffixes):
            raise ValueError("Duration must end with d (days), w (weeks), m (months), or y (years)")
        return v

    @model_validator(mode='after')
    def set_expires_at(self):
        if self.approved_at and self.requested_duration:
            duration_str = self.requested_duration
            duration_value = int(duration_str[:-1])
            duration_unit = duration_str[-1]
            
            if duration_unit == 'd':
                delta = timedelta(days=duration_value)
            elif duration_unit == 'w':
                delta = timedelta(weeks=duration_value)
            elif duration_unit == 'm':
                delta = timedelta(days=duration_value * 30)
            elif duration_unit == 'y':
                delta = timedelta(days=duration_value * 365)
            else:
                raise ValueError("Invalid duration unit")
            
            self.expires_at = self.approved_at + delta
        return self


class AuditLog(BaseModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_email: str
    action: str = Field(..., description="Action performed")
    resource: str
    service_type: ServiceType
    details: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None


class PolicyMetadata(BaseModel):
    version: str = "1.0"
    schema_version: str = "2024-01-01"
    organization: Optional[str] = None
    contact: Optional[str] = None


class AccessPolicyCollection(BaseModel):
    access_policies: List[AccessPolicy]
    metadata: Optional[PolicyMetadata] = None 