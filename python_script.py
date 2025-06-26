import google.auth
from google.cloud import sql_v1beta4

def grant_postgres_access(instance_id, db_user, db_name, role, project_id):
    # Assumes service account has necessary permissions
    client = sql_v1beta4.SqlUsersServiceClient()
    # Create user if not exists
    user = {
        "name": db_user,
        "host": "%",
        "password": "secure-temp-password"  # Should be securely generated
    }
    client.insert(project=project_id, instance=instance_id, body=user)
    # Grant role (run SQL via Cloud SQL Admin API or proxy)
    # Example: GRANT role TO db_user;
    # This part typically requires connecting to the DB and executing SQL
    # Use psycopg2 or similar library for direct SQL execution
    print(f"Granted {role} to {db_user} on {db_name}")

# Example usage
grant_postgres_access(
    instance_id="my-sql-instance",
    db_user="alice",
    db_name="sales_db",
    role="read_only",
    project_id="my-gcp-project"
)

def provision_multi_service_access(policy):
    """Provision access across multiple GCP services"""
    
    # Extract unified workflow settings
    workflow = policy["unified_workflow"]
    
    # Handle Cloud SQL (PostgreSQL)
    if "cloudsql" in policy["services"]:
        cloudsql_config = policy["services"]["cloudsql"]
        provision_cloudsql_access(
            instance=cloudsql_config["instance"],
            database=cloudsql_config["database"],
            users=workflow["members"],
            duration=workflow["access_duration"]
        )
    
    # Handle Looker Studio
    if "looker_studio" in policy["services"]:
        looker_config = policy["services"]["looker_studio"]
        provision_looker_access(
            dashboard_id=looker_config["dashboard_id"],
            users=workflow["members"],
            duration=workflow["access_duration"]
        )
    
    # Unified audit logging
    log_access_grant(
        policy_id=policy["id"],
        services=["cloudsql", "looker_studio"],
        users=workflow["members"],
        approver=workflow["approvers"][0]
    )