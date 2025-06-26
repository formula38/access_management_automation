#!/usr/bin/env python3
"""
Simplified test API for Data Access Management System
This version doesn't require external dependencies for basic testing.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import logging
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Data Access Management API (Test Version)",
    description="Simplified API for testing without external dependencies",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for testing
access_requests = []
access_policies = []
audit_logs = []

def log_audit_event(user_email: str, action: str, resource: str, details: Dict[str, Any] = None):
    """Log audit event"""
    audit_log = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "user_email": user_email,
        "action": action,
        "resource": resource,
        "details": details or {}
    }
    audit_logs.append(audit_log)
    logger.info(f"Audit: {action} by {user_email} on {resource}")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Data Access Management API (Test Version)",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "api": "healthy",
            "database": "healthy (in-memory)",
            "ai_service": "simulated"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/access-requests")
async def create_access_request(request: Dict[str, Any]):
    """Create a new access request"""
    try:
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Simulate AI analysis
        ai_analysis = {
            "risk_score": 35,  # Simulated risk score
            "risk_factors": ["Standard access request"],
            "recommendations": ["Consider shorter duration if possible"],
            "suggested_access_level": request.get("access_level", "read_only"),
            "additional_approvers": [],
            "compliance_notes": ["Request appears compliant"]
        }
        
        # Create access request object
        access_request = {
            "id": request_id,
            "requester_email": request.get("requester_email"),
            "resource": request.get("resource"),
            "service_type": request.get("service_type"),
            "access_level": request.get("access_level"),
            "justification": request.get("justification"),
            "requested_duration": request.get("requested_duration"),
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "ai_risk_score": ai_analysis["risk_score"],
            "ai_suggestions": ai_analysis["recommendations"]
        }
        
        # Store request
        access_requests.append(access_request)
        
        # Log audit event
        log_audit_event(
            user_email=request.get("requester_email"),
            action="access_request_created",
            resource=request.get("resource"),
            details={"request_id": request_id}
        )
        
        logger.info(f"Access request created: {request_id}")
        return access_request
        
    except Exception as e:
        logger.error(f"Error creating access request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/access-requests")
async def get_access_requests():
    """Get all access requests"""
    return access_requests

@app.get("/api/access-requests/{request_id}")
async def get_access_request(request_id: str):
    """Get specific access request"""
    for request in access_requests:
        if request["id"] == request_id:
            return request
    raise HTTPException(status_code=404, detail="Access request not found")

@app.put("/api/access-requests/{request_id}/approve")
async def approve_access_request(request_id: str, approver_email: str):
    """Approve an access request"""
    try:
        request = None
        for req in access_requests:
            if req["id"] == request_id:
                request = req
                break
        
        if not request:
            raise HTTPException(status_code=404, detail="Access request not found")
        
        if request["status"] != "pending":
            raise HTTPException(status_code=400, detail="Request is not pending")
        
        # Update request status
        request["status"] = "approved"
        request["approved_by"] = approver_email
        request["approved_at"] = datetime.utcnow().isoformat()
        
        # Simulate provisioning
        provisioning_result = {
            "success": True,
            "message": f"Access provisioned for {request['service_type']}",
            "provisioned_at": datetime.utcnow().isoformat()
        }
        
        # Log audit event
        log_audit_event(
            user_email=approver_email,
            action="access_request_approved",
            resource=request["resource"],
            details={"request_id": request_id, "provisioning_result": provisioning_result}
        )
        
        return {
            "message": "Access request approved",
            "request_id": request_id,
            "provisioning_result": provisioning_result
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
            if req["id"] == request_id:
                request = req
                break
        
        if not request:
            raise HTTPException(status_code=404, detail="Access request not found")
        
        if request["status"] != "pending":
            raise HTTPException(status_code=400, detail="Request is not pending")
        
        # Update request status
        request["status"] = "rejected"
        request["rejected_by"] = rejector_email
        request["rejected_at"] = datetime.utcnow().isoformat()
        request["rejection_reason"] = reason
        
        # Log audit event
        log_audit_event(
            user_email=rejector_email,
            action="access_request_rejected",
            resource=request["resource"],
            details={"request_id": request_id, "reason": reason}
        )
        
        return {"message": "Access request rejected", "request_id": request_id}
        
    except Exception as e:
        logger.error(f"Error rejecting access request: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/policies")
async def create_access_policy(policy: Dict[str, Any]):
    """Create a new access policy"""
    try:
        policy_id = str(uuid.uuid4())
        
        access_policy = {
            "id": policy_id,
            "resource": policy.get("resource"),
            "resource_type": policy.get("resource_type"),
            "roles": policy.get("roles", []),
            "access_duration": policy.get("access_duration"),
            "description": policy.get("description"),
            "created_by": policy.get("created_by"),
            "created_at": datetime.utcnow().isoformat()
        }
        
        access_policies.append(access_policy)
        
        # Log audit event
        log_audit_event(
            user_email=policy.get("created_by", "system"),
            action="policy_created",
            resource=policy.get("resource"),
            details={"policy_id": policy_id}
        )
        
        logger.info(f"Access policy created: {policy_id}")
        return access_policy
        
    except Exception as e:
        logger.error(f"Error creating access policy: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/policies")
async def get_access_policies():
    """Get all access policies"""
    return access_policies

@app.get("/api/audit-logs")
async def get_audit_logs():
    """Get audit logs"""
    return audit_logs

@app.post("/api/ai/analyze")
async def analyze_request_with_ai(request_data: Dict[str, Any]):
    """Simulate AI analysis"""
    try:
        request = request_data.get("request", {})
        user_context = request_data.get("user_context", {})
        
        # Simulate AI analysis based on request data
        risk_score = 30  # Default low risk
        
        if request.get("access_level") == "admin":
            risk_score = 75
        elif request.get("access_level") == "read_write":
            risk_score = 50
        
        if "finance" in request.get("resource", "").lower():
            risk_score += 20
        
        analysis = {
            "risk_score": min(risk_score, 100),
            "risk_factors": ["Simulated analysis"],
            "recommendations": ["Consider least privilege access"],
            "suggested_access_level": request.get("access_level", "read_only"),
            "additional_approvers": [],
            "compliance_notes": ["Simulated compliance check"]
        }
        
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
            "service_type": "cloudsql",
            "description": "PostgreSQL database containing sales data",
            "data_sensitivity": "internal"
        },
        {
            "id": "marketing-dashboard",
            "name": "Marketing Dashboard",
            "service_type": "looker_studio",
            "description": "Marketing performance dashboard",
            "data_sensitivity": "internal"
        },
        {
            "id": "finance-db",
            "name": "Finance Database",
            "service_type": "cloudsql",
            "description": "Financial data and reports",
            "data_sensitivity": "confidential"
        }
    ]
    return resources

@app.get("/api/metrics")
async def get_system_metrics():
    """Get system metrics"""
    total_requests = len(access_requests)
    pending_requests = len([r for r in access_requests if r["status"] == "pending"])
    approved_requests = len([r for r in access_requests if r["status"] == "approved"])
    rejected_requests = len([r for r in access_requests if r["status"] == "rejected"])
    
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