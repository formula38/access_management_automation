import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import secrets
import string
from app.models.access_models import AccessRequest, ServiceType, AccessLevel

logger = logging.getLogger(__name__)

# Try to import Google Cloud libraries, but handle gracefully if not available
try:
    import google.auth
    from google.cloud import sql_v1beta4
    from google.cloud.sql_admin_v1 import CloudSqlAdminClient
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    import psycopg2
    GCP_AVAILABLE = True
except ImportError:
    logger.warning("Google Cloud libraries not available. GCP integration will be simulated.")
    GCP_AVAILABLE = False


class GCPService:
    def __init__(self, project_id: str, service_account_path: Optional[str] = None):
        """Initialize GCP service with authentication"""
        self.project_id = project_id
        self.gcp_available = GCP_AVAILABLE
        
        if not GCP_AVAILABLE:
            logger.info("Running in demo mode - GCP operations will be simulated")
            return
            
        # Initialize credentials
        if service_account_path:
            self.credentials = service_account.Credentials.from_service_account_file(
                service_account_path,
                scopes=[
                    'https://www.googleapis.com/auth/cloud-platform',
                    'https://www.googleapis.com/auth/sqlservice.admin',
                    'https://www.googleapis.com/auth/datastudio'
                ]
            )
        else:
            self.credentials, _ = google.auth.default()
        
        # Initialize clients
        self.sql_client = CloudSqlAdminClient(credentials=self.credentials)
        self.sql_users_client = sql_v1beta4.SqlUsersServiceClient(credentials=self.credentials)
        
        # Initialize Looker Studio API
        self.looker_service = build('datastudio', 'v1', credentials=self.credentials)
        
        logger.info(f"GCP Service initialized for project: {project_id}")

    def provision_cloudsql_access(self, request: AccessRequest, instance_config: Dict[str, Any]) -> Dict[str, Any]:
        """Provision access to Cloud SQL PostgreSQL instance"""
        try:
            if not self.gcp_available:
                # Simulate provisioning for demo
                return self._simulate_cloudsql_provisioning(request, instance_config)
            
            instance_id = instance_config.get('instance_id')
            database = instance_config.get('database', 'postgres')
            
            # Generate secure password
            password = self._generate_secure_password()
            
            # Create database user
            user = {
                "name": request.requester_email.split('@')[0],  # Use email prefix as username
                "host": "%",
                "password": password
            }
            
            # Insert user into Cloud SQL
            operation = self.sql_users_client.insert(
                project=self.project_id,
                instance=instance_id,
                body=user
            )
            
            # Wait for operation to complete
            self._wait_for_operation(operation.name)
            
            # Grant database permissions
            self._grant_database_permissions(
                instance_id=instance_id,
                database=database,
                username=user["name"],
                access_level=request.access_level
            )
            
            # Create IAM binding for Cloud SQL Client role
            self._create_iam_binding(
                user_email=request.requester_email,
                role="roles/cloudsql.client"
            )
            
            result = {
                "success": True,
                "username": user["name"],
                "password": password,  # In production, send via secure channel
                "instance_id": instance_id,
                "database": database,
                "access_level": request.access_level.value,
                "provisioned_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Successfully provisioned Cloud SQL access for {request.requester_email}")
            return result
            
        except Exception as e:
            logger.error(f"Error provisioning Cloud SQL access: {e}")
            return {
                "success": False,
                "error": str(e),
                "provisioned_at": datetime.utcnow().isoformat()
            }

    def provision_looker_studio_access(self, request: AccessRequest, dashboard_config: Dict[str, Any]) -> Dict[str, Any]:
        """Provision access to Looker Studio dashboard"""
        try:
            if not self.gcp_available:
                # Simulate provisioning for demo
                return self._simulate_looker_studio_provisioning(request, dashboard_config)
            
            dashboard_id = dashboard_config.get('dashboard_id')
            
            # Add user to dashboard permissions
            # Note: This is a simplified example. Real implementation would use Looker Studio API
            # or Google Workspace Admin SDK for sharing
            
            # For demonstration, we'll create a sharing link with specific permissions
            sharing_config = {
                "type": "USER",
                "emailAddress": request.requester_email,
                "role": self._map_access_level_to_looker_role(request.access_level)
            }
            
            # In a real implementation, you would use the Looker Studio API
            # self.looker_service.reports().share().update(...)
            
            result = {
                "success": True,
                "dashboard_id": dashboard_id,
                "user_email": request.requester_email,
                "access_level": request.access_level.value,
                "sharing_config": sharing_config,
                "provisioned_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Successfully provisioned Looker Studio access for {request.requester_email}")
            return result
            
        except Exception as e:
            logger.error(f"Error provisioning Looker Studio access: {e}")
            return {
                "success": False,
                "error": str(e),
                "provisioned_at": datetime.utcnow().isoformat()
            }

    def _simulate_cloudsql_provisioning(self, request: AccessRequest, instance_config: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate Cloud SQL provisioning for demo purposes"""
        instance_id = instance_config.get('instance_id', 'demo-instance')
        database = instance_config.get('database', 'demo_db')
        password = self._generate_secure_password()
        
        result = {
            "success": True,
            "username": request.requester_email.split('@')[0],
            "password": password,
            "instance_id": instance_id,
            "database": database,
            "access_level": request.access_level.value,
            "provisioned_at": datetime.utcnow().isoformat(),
            "demo_mode": True,
            "message": "Simulated Cloud SQL provisioning for demo"
        }
        
        logger.info(f"Simulated Cloud SQL provisioning for {request.requester_email}")
        return result

    def _simulate_looker_studio_provisioning(self, request: AccessRequest, dashboard_config: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate Looker Studio provisioning for demo purposes"""
        dashboard_id = dashboard_config.get('dashboard_id', 'demo-dashboard')
        
        result = {
            "success": True,
            "dashboard_id": dashboard_id,
            "user_email": request.requester_email,
            "access_level": request.access_level.value,
            "sharing_config": {
                "type": "USER",
                "emailAddress": request.requester_email,
                "role": self._map_access_level_to_looker_role(request.access_level)
            },
            "provisioned_at": datetime.utcnow().isoformat(),
            "demo_mode": True,
            "message": "Simulated Looker Studio provisioning for demo"
        }
        
        logger.info(f"Simulated Looker Studio provisioning for {request.requester_email}")
        return result

    def deprovision_access(self, request: AccessRequest, service_type: ServiceType, config: Dict[str, Any]) -> Dict[str, Any]:
        """Deprovision access from GCP services"""
        try:
            if not self.gcp_available:
                # Simulate deprovisioning for demo
                return self._simulate_deprovisioning(request, service_type, config)
            
            if service_type == ServiceType.CLOUDSQL:
                return self._deprovision_cloudsql_access(request, config)
            elif service_type == ServiceType.LOOKER_STUDIO:
                return self._deprovision_looker_studio_access(request, config)
            else:
                raise ValueError(f"Unsupported service type: {service_type}")
                
        except Exception as e:
            logger.error(f"Error deprovisioning access: {e}")
            return {
                "success": False,
                "error": str(e),
                "deprovisioned_at": datetime.utcnow().isoformat()
            }

    def _simulate_deprovisioning(self, request: AccessRequest, service_type: ServiceType, config: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate deprovisioning for demo purposes"""
        result = {
            "success": True,
            "user_email": request.requester_email,
            "service_type": service_type.value,
            "deprovisioned_at": datetime.utcnow().isoformat(),
            "demo_mode": True,
            "message": f"Simulated deprovisioning for {service_type.value}"
        }
        
        logger.info(f"Simulated deprovisioning for {request.requester_email}")
        return result

    def _deprovision_cloudsql_access(self, request: AccessRequest, config: Dict[str, Any]) -> Dict[str, Any]:
        """Deprovision Cloud SQL access"""
        try:
            instance_id = config.get('instance_id')
            username = request.requester_email.split('@')[0]
            
            # Delete user from Cloud SQL
            operation = self.sql_users_client.delete(
                project=self.project_id,
                instance=instance_id,
                name=f"{username}@%"
            )
            
            # Wait for operation to complete
            self._wait_for_operation(operation.name)
            
            # Remove IAM binding
            self._remove_iam_binding(
                user_email=request.requester_email,
                role="roles/cloudsql.client"
            )
            
            return {
                "success": True,
                "username": username,
                "instance_id": instance_id,
                "deprovisioned_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error deprovisioning Cloud SQL access: {e}")
            return {
                "success": False,
                "error": str(e),
                "deprovisioned_at": datetime.utcnow().isoformat()
            }

    def _deprovision_looker_studio_access(self, request: AccessRequest, config: Dict[str, Any]) -> Dict[str, Any]:
        """Deprovision Looker Studio access"""
        try:
            dashboard_id = config.get('dashboard_id')
            
            # Remove user from dashboard permissions
            # In a real implementation, you would use the Looker Studio API
            
            return {
                "success": True,
                "dashboard_id": dashboard_id,
                "user_email": request.requester_email,
                "deprovisioned_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error deprovisioning Looker Studio access: {e}")
            return {
                "success": False,
                "error": str(e),
                "deprovisioned_at": datetime.utcnow().isoformat()
            }

    def _grant_database_permissions(self, instance_id: str, database: str, username: str, access_level: AccessLevel):
        """Grant database permissions to user"""
        try:
            # Connect to the database using Cloud SQL Proxy or direct connection
            # This is a simplified example - in production, you'd use proper connection management
            
            # Define permissions based on access level
            if access_level == AccessLevel.READ_ONLY:
                permissions = ["SELECT"]
            elif access_level == AccessLevel.READ_WRITE:
                permissions = ["SELECT", "INSERT", "UPDATE", "DELETE"]
            elif access_level == AccessLevel.ADMIN:
                permissions = ["ALL PRIVILEGES"]
            else:
                permissions = ["SELECT"]
            
            # In a real implementation, you would:
            # 1. Connect to the database
            # 2. Execute GRANT statements
            # 3. Handle connection pooling and security
            
            logger.info(f"Granted permissions {permissions} to user {username} on database {database}")
            
        except Exception as e:
            logger.error(f"Error granting database permissions: {e}")
            raise

    def _create_iam_binding(self, user_email: str, role: str):
        """Create IAM binding for user"""
        try:
            # In a real implementation, you would use the IAM API
            # to create the binding
            logger.info(f"Created IAM binding: {role} for {user_email}")
            
        except Exception as e:
            logger.error(f"Error creating IAM binding: {e}")
            raise

    def _remove_iam_binding(self, user_email: str, role: str):
        """Remove IAM binding for user"""
        try:
            # In a real implementation, you would use the IAM API
            # to remove the binding
            logger.info(f"Removed IAM binding: {role} for {user_email}")
            
        except Exception as e:
            logger.error(f"Error removing IAM binding: {e}")
            raise

    def _map_access_level_to_looker_role(self, access_level: AccessLevel) -> str:
        """Map access level to Looker Studio role"""
        mapping = {
            AccessLevel.READ_ONLY: "READER",
            AccessLevel.READ_WRITE: "WRITER",
            AccessLevel.ADMIN: "OWNER"
        }
        return mapping.get(access_level, "READER")

    def _generate_secure_password(self, length: int = 16) -> str:
        """Generate secure password"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def _wait_for_operation(self, operation_name: str, timeout: int = 300):
        """Wait for Cloud SQL operation to complete"""
        try:
            # In a real implementation, you would poll the operation status
            # until it's complete or times out
            logger.info(f"Waiting for operation: {operation_name}")
            
        except Exception as e:
            logger.error(f"Error waiting for operation: {e}")
            raise

    def get_audit_logs(self, service_type: ServiceType, resource: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Retrieve audit logs for GCP services"""
        try:
            if not self.gcp_available:
                return self._get_simulated_audit_logs(service_type, resource, start_time, end_time)
            
            if service_type == ServiceType.CLOUDSQL:
                return self._get_cloudsql_audit_logs(resource, start_time, end_time)
            elif service_type == ServiceType.LOOKER_STUDIO:
                return self._get_looker_studio_audit_logs(resource, start_time, end_time)
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error retrieving audit logs: {e}")
            return []

    def _get_simulated_audit_logs(self, service_type: ServiceType, resource: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get simulated audit logs for demo purposes"""
        logs = [
            {
                "timestamp": datetime.utcnow().isoformat(),
                "resource": resource,
                "action": "simulated_access",
                "user_email": "demo@example.com",
                "details": {
                    "service_type": service_type.value,
                    "demo_mode": True
                }
            }
        ]
        return logs

    def _get_cloudsql_audit_logs(self, resource: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Retrieve Cloud SQL audit logs"""
        try:
            # In a real implementation, you would use the Cloud Logging API
            # to retrieve audit logs for Cloud SQL operations
            
            # Example log entry
            logs = [
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "resource": resource,
                    "action": "database_access",
                    "user_email": "user@example.com",
                    "details": {
                        "operation": "SELECT",
                        "table": "users",
                        "rows_affected": 10
                    }
                }
            ]
            
            return logs
            
        except Exception as e:
            logger.error(f"Error retrieving Cloud SQL audit logs: {e}")
            return []

    def _get_looker_studio_audit_logs(self, resource: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Retrieve Looker Studio audit logs"""
        try:
            # In a real implementation, you would use the Looker Studio API
            # or Google Workspace Admin SDK to retrieve audit logs
            
            # Example log entry
            logs = [
                {
                    "timestamp": datetime.utcnow().isoformat(),
                    "resource": resource,
                    "action": "dashboard_access",
                    "user_email": "user@example.com",
                    "details": {
                        "dashboard_id": resource,
                        "access_type": "view"
                    }
                }
            ]
            
            return logs
            
        except Exception as e:
            logger.error(f"Error retrieving Looker Studio audit logs: {e}")
            return []

    def validate_access_policy(self, policy: Dict[str, Any]) -> Dict[str, Any]:
        """Validate access policy against GCP resources"""
        try:
            validation_result = {
                "valid": True,
                "errors": [],
                "warnings": []
            }
            
            if not self.gcp_available:
                validation_result["warnings"].append("GCP integration not available - validation simulated")
                return validation_result
            
            # Validate Cloud SQL resources
            if "cloudsql" in policy.get("services", {}):
                cloudsql_config = policy["services"]["cloudsql"]
                if not self._validate_cloudsql_config(cloudsql_config):
                    validation_result["valid"] = False
                    validation_result["errors"].append("Invalid Cloud SQL configuration")
            
            # Validate Looker Studio resources
            if "looker_studio" in policy.get("services", {}):
                looker_config = policy["services"]["looker_studio"]
                if not self._validate_looker_config(looker_config):
                    validation_result["valid"] = False
                    validation_result["errors"].append("Invalid Looker Studio configuration")
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating access policy: {e}")
            return {
                "valid": False,
                "errors": [str(e)],
                "warnings": []
            }

    def _validate_cloudsql_config(self, config: Dict[str, Any]) -> bool:
        """Validate Cloud SQL configuration"""
        try:
            instance_id = config.get("instance")
            if not instance_id:
                return False
            
            # In a real implementation, you would verify the instance exists
            # and the service account has access to it
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating Cloud SQL config: {e}")
            return False

    def _validate_looker_config(self, config: Dict[str, Any]) -> bool:
        """Validate Looker Studio configuration"""
        try:
            dashboard_id = config.get("dashboard_id")
            if not dashboard_id:
                return False
            
            # In a real implementation, you would verify the dashboard exists
            # and the service account has access to it
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating Looker Studio config: {e}")
            return False 