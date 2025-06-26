#!/usr/bin/env python3
"""
Test script for the Data Access Management API
This script tests the core functionality without requiring Docker or external services.
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test@example.com"

def test_health_check():
    """Test the health check endpoint"""
    print("🔍 Testing health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data['status']}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Is the server running?")
        return False

def test_create_access_request():
    """Test creating an access request"""
    print("\n📝 Testing access request creation...")
    
    request_data = {
        "requester_email": TEST_EMAIL,
        "resource": "sales-db",
        "service_type": "cloudsql",
        "access_level": "read_only",
        "justification": "Need to analyze sales data for quarterly reporting",
        "requested_duration": "30d"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/access-requests",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Access request created: {data['id']}")
            print(f"   Risk score: {data.get('ai_risk_score', 'N/A')}")
            print(f"   AI suggestions: {len(data.get('ai_suggestions', []))} items")
            return data['id']
        else:
            print(f"❌ Failed to create access request: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating access request: {e}")
        return None

def test_get_access_requests():
    """Test retrieving access requests"""
    print("\n📋 Testing access requests retrieval...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/access-requests")
        
        if response.status_code == 200:
            requests_list = response.json()
            print(f"✅ Retrieved {len(requests_list)} access requests")
            for req in requests_list:
                print(f"   - {req['id']}: {req['status']} ({req['requester_email']})")
            return requests_list
        else:
            print(f"❌ Failed to retrieve access requests: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error retrieving access requests: {e}")
        return []

def test_approve_access_request(request_id):
    """Test approving an access request"""
    print(f"\n✅ Testing access request approval for {request_id}...")
    
    try:
        response = requests.put(
            f"{API_BASE_URL}/api/access-requests/{request_id}/approve",
            params={"approver_email": "approver@example.com"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Access request approved: {data['message']}")
            return True
        else:
            print(f"❌ Failed to approve access request: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error approving access request: {e}")
        return False

def test_create_access_policy():
    """Test creating an access policy"""
    print("\n📋 Testing access policy creation...")
    
    policy_data = {
        "resource": "sales-db",
        "resource_type": "cloudsql",
        "roles": [
            {
                "name": "read_only",
                "permissions": ["SELECT"],
                "conditions": [
                    {"department": "sales"},
                    {"data_sensitivity": "internal"}
                ]
            }
        ],
        "access_duration": "30d",
        "description": "Sales team read access to sales database",
        "created_by": "admin@example.com"
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/policies",
            json=policy_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Access policy created: {data['id']}")
            return data['id']
        else:
            print(f"❌ Failed to create access policy: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating access policy: {e}")
        return None

def test_get_audit_logs():
    """Test retrieving audit logs"""
    print("\n📊 Testing audit logs retrieval...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/audit-logs")
        
        if response.status_code == 200:
            logs = response.json()
            print(f"✅ Retrieved {len(logs)} audit logs")
            for log in logs[-3:]:  # Show last 3 logs
                print(f"   - {log['timestamp']}: {log['action']} by {log['user_email']}")
            return logs
        else:
            print(f"❌ Failed to retrieve audit logs: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error retrieving audit logs: {e}")
        return []

def test_get_metrics():
    """Test retrieving system metrics"""
    print("\n📈 Testing system metrics...")
    
    try:
        response = requests.get(f"{API_BASE_URL}/api/metrics")
        
        if response.status_code == 200:
            metrics = response.json()
            print(f"✅ System metrics:")
            print(f"   - Total requests: {metrics['total_requests']}")
            print(f"   - Pending requests: {metrics['pending_requests']}")
            print(f"   - Approved requests: {metrics['approved_requests']}")
            print(f"   - Rejected requests: {metrics['rejected_requests']}")
            print(f"   - Total policies: {metrics['total_policies']}")
            print(f"   - Total audit logs: {metrics['total_audit_logs']}")
            return metrics
        else:
            print(f"❌ Failed to retrieve metrics: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error retrieving metrics: {e}")
        return None

def test_ai_analysis():
    """Test AI analysis endpoint"""
    print("\n🤖 Testing AI analysis...")
    
    analysis_data = {
        "request": {
            "requester_email": TEST_EMAIL,
            "resource": "finance-db",
            "service_type": "cloudsql",
            "access_level": "admin",
            "justification": "Need admin access for financial reporting",
            "requested_duration": "90d"
        },
        "user_context": {
            "department": "Finance",
            "role": "Financial Analyst",
            "location": "New York"
        }
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/ai/analyze",
            json=analysis_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            analysis = data['analysis']
            print(f"✅ AI analysis completed:")
            print(f"   - Risk score: {analysis.get('risk_score', 'N/A')}")
            print(f"   - Risk factors: {len(analysis.get('risk_factors', []))}")
            print(f"   - Recommendations: {len(analysis.get('recommendations', []))}")
            return analysis
        else:
            print(f"❌ Failed to get AI analysis: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error getting AI analysis: {e}")
        return None

def run_all_tests():
    """Run all tests"""
    print("🚀 Starting Data Access Management API Tests")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health_check():
        print("\n❌ Health check failed. Stopping tests.")
        return
    
    # Test 2: Create access request
    request_id = test_create_access_request()
    
    # Test 3: Get access requests
    test_get_access_requests()
    
    # Test 4: Create access policy
    policy_id = test_create_access_policy()
    
    # Test 5: AI analysis
    test_ai_analysis()
    
    # Test 6: Approve access request (if we have one)
    if request_id:
        test_approve_access_request(request_id)
    
    # Test 7: Get audit logs
    test_get_audit_logs()
    
    # Test 8: Get metrics
    test_get_metrics()
    
    print("\n" + "=" * 50)
    print("✅ All tests completed!")

if __name__ == "__main__":
    run_all_tests() 