from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Any
import logging
import os
from datetime import datetime
import json

from app.models.access_models import (
    AccessRequest, AccessPolicy, AuditLog, 
    ServiceType, AccessLevel, RequestStatus
)
from app.services.ai_service import AIService
from app.services.gcp_service import GCPService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Data Access Management API",
    description="AI-powered data access management system for GCP services",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize services
ai_service = AIService(
    ollama_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
)

gcp_service = GCPService(
    project_id=os.getenv("GCP_PROJECT_ID", "demo-project"),
    service_account_path=os.getenv("GCP_SERVICE_ACCOUNT_PATH")
)

# Load access policies from JSON file at startup
try:
    with open("access_policies.json", "r") as f:
        loaded_policies = json.load(f)
        for policy in loaded_policies:
            access_policies.append(AccessPolicy(**policy))
            ai_service.store_policy_embedding(policy.get("id", policy.get("name", "")), json.dumps(policy))
    logger.info(f"Loaded and embedded {len(loaded_policies)} access policies from access_policies.json")
except Exception as e:
    logger.warning(f"Could not load or embed access policies: {e}")

# In-memory storage for testing (replace with database in production)
access_requests: List[AccessRequest] = []
access_policies: List[AccessPolicy] = []
audit_logs: List[AuditLog] = []

def log_audit_event(user_email: str, action: str, resource: str, service_type: ServiceType, details: Dict[str, Any] = None):
    """Log audit event"""
    audit_log = AuditLog(
        user_email=user_email,
        action=action,
        resource=resource,
        service_type=service_type,
        details=details or {}
    )
    audit_logs.append(audit_log)
    logger.info(f"Audit: {action} by {user_email} on {resource}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Data Access Management API",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    services_status = {
        "ai_service": "healthy",
        "gcp_service": "healthy",
        "database": "healthy"
    }
    
    # Check AI service
    try:
        # Simple test to check if Ollama is reachable
        services_status["ai_service"] = "healthy"
    except Exception as e:
        services_status["ai_service"] = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy",
        "services": services_status,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/access-requests", response_model=AccessRequest)
async def create_access_request(request: AccessRequest):
    """Create a new access request"""
    try:
        # Add AI analysis
        user_context = {
            "department": "Engineering",
            "role": "Software Engineer",
            "location": "San Francisco"
        }
        
        ai_analysis = ai_service.analyze_access_request(request, user_context)
        request.ai_risk_score = ai_analysis.get("risk_score", 50)
        request.ai_suggestions = ai_analysis.get("recommendations", [])
        
        # Store request
        access_requests.append(request)
        
        # Log audit event
        log_audit_event(
            user_email=request.requester_email,
            action="access_request_created",
            resource=request.resource,
            service_type=request.service_type,
            details={"request_id": str(request.id)}
        )
        
        logger.info(f"Access request created: {request.id}")
        return request
        
    except Exception as e:
        logger.error(f"Error creating access request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/access-requests", response_model=List[AccessRequest])
async def get_access_requests():
    """Get all access requests"""
    return access_requests

@app.get("/api/access-requests/{request_id}", response_model=AccessRequest)
async def get_access_request(request_id: str):
    """Get specific access request"""
    for request in access_requests:
        if str(request.id) == request_id:
            return request
    raise HTTPException(status_code=404, detail="Access request not found")

@app.put("/api/access-requests/{request_id}/approve")
async def approve_access_request(request_id: str, approver_email: str):
    """Approve an access request"""
    try:
        request = None
        for req in access_requests:
            if str(req.id) == request_id:
                request = req
                break
        
        if not request:
            raise HTTPException(status_code=404, detail="Access request not found")
        
        if request.status != RequestStatus.PENDING:
            raise HTTPException(status_code=400, detail="Request is not pending")
        
        # Update request status
        request.status = RequestStatus.APPROVED
        request.approved_by = approver_email
        request.approved_at = datetime.utcnow()
        
        # Provision access
        if request.service_type == ServiceType.CLOUDSQL:
            result = gcp_service.provision_cloudsql_access(
                request, 
                {"instance_id": "demo-instance", "database": "demo_db"}
            )
        elif request.service_type == ServiceType.LOOKER_STUDIO:
            result = gcp_service.provision_looker_studio_access(
                request, 
                {"dashboard_id": "demo-dashboard"}
            )
        else:
            result = {"success": True, "message": "Service not implemented"}
        
        # Log audit event
        log_audit_event(
            user_email=approver_email,
            action="access_request_approved",
            resource=request.resource,
            service_type=request.service_type,
            details={"request_id": str(request.id), "provisioning_result": result}
        )
        
        return {
            "message": "Access request approved",
            "request_id": request_id,
            "provisioning_result": result
        }
        
    except Exception as e:
        logger.error(f"Error approving access request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/access-requests/{request_id}/reject")
async def reject_access_request(request_id: str, rejector_email: str, reason: str):
    """Reject an access request"""
    try:
        request = None
        for req in access_requests:
            if str(req.id) == request_id:
                request = req
                break
        
        if not request:
            raise HTTPException(status_code=404, detail="Access request not found")
        
        if request.status != RequestStatus.PENDING:
            raise HTTPException(status_code=400, detail="Request is not pending")
        
        # Update request status
        request.status = RequestStatus.REJECTED
        request.rejected_by = rejector_email
        request.rejected_at = datetime.utcnow()
        request.rejection_reason = reason
        
        # Log audit event
        log_audit_event(
            user_email=rejector_email,
            action="access_request_rejected",
            resource=request.resource,
            service_type=request.service_type,
            details={"request_id": str(request.id), "reason": reason}
        )
        
        return {"message": "Access request rejected", "request_id": request_id}
        
    except Exception as e:
        logger.error(f"Error rejecting access request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/policies", response_model=AccessPolicy)
async def create_access_policy(policy: AccessPolicy):
    """Create a new access policy"""
    try:
        access_policies.append(policy)
        
        # Initialize AI service with new policies
        ai_service.initialize_vector_db(access_policies)
        
        # Log audit event
        log_audit_event(
            user_email=policy.created_by or "system",
            action="policy_created",
            resource=policy.resource,
            service_type=policy.resource_type,
            details={"policy_id": str(policy.id)}
        )
        
        logger.info(f"Access policy created: {policy.id}")
        return policy
        
    except Exception as e:
        logger.error(f"Error creating access policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/policies", response_model=List[AccessPolicy])
async def get_access_policies():
    """Get all access policies"""
    return access_policies

@app.get("/api/audit-logs", response_model=List[AuditLog])
async def get_audit_logs():
    """Get audit logs"""
    return audit_logs

@app.post("/api/ai/analyze")
async def analyze_request_with_ai(request_data: Dict[str, Any]):
    """Analyze access request using AI"""
    try:
        user_context = request_data.get("user_context", {})
        request = AccessRequest(**request_data.get("request", {}))
        
        analysis = ai_service.analyze_access_request(request, user_context)
        
        return {
            "analysis": analysis,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in AI analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/resources")
async def get_available_resources():
    """Get available resources for access requests"""
    resources = [
        {
            "id": "sales-db",
            "name": "Sales Database",
            "service_type": ServiceType.CLOUDSQL,
            "description": "PostgreSQL database containing sales data",
            "data_sensitivity": "internal"
        },
        {
            "id": "marketing-dashboard",
            "name": "Marketing Dashboard",
            "service_type": ServiceType.LOOKER_STUDIO,
            "description": "Marketing performance dashboard",
            "data_sensitivity": "internal"
        },
        {
            "id": "finance-db",
            "name": "Finance Database",
            "service_type": ServiceType.CLOUDSQL,
            "description": "Financial data and reports",
            "data_sensitivity": "confidential"
        }
    ]
    return resources

@app.get("/api/metrics")
async def get_system_metrics():
    """Get system metrics"""
    total_requests = len(access_requests)
    pending_requests = len([r for r in access_requests if r.status == RequestStatus.PENDING])
    approved_requests = len([r for r in access_requests if r.status == RequestStatus.APPROVED])
    rejected_requests = len([r for r in access_requests if r.status == RequestStatus.REJECTED])
    
    return {
        "total_requests": total_requests,
        "pending_requests": pending_requests,
        "approved_requests": approved_requests,
        "rejected_requests": rejected_requests,
        "total_policies": len(access_policies),
        "total_audit_logs": len(audit_logs),
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 