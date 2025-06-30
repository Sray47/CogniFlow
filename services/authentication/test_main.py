# services/authentication/test_main.py

"""
Test suite for the CogniFlow Authentication Service

This test suite covers the core authentication functionality including:
- User login and logout
- Token generation and verification
- Role-based access control
- Security event logging
- Rate limiting
- Session management

Run tests with: pytest test_main.py -v
"""

import pytest
import json
from fastapi.testclient import TestClient
from main import app, users, user_sessions, audit_logs, blacklisted_tokens, rate_limit_tracking
from main import UserRole, hash_password, User
import datetime
from datetime import timezone

# Create test client
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_data():
    """Set up test data before each test and clean up after"""
    # Clear all in-memory data
    users.clear()
    user_sessions.clear()
    audit_logs.clear()
    blacklisted_tokens.clear()
    rate_limit_tracking.clear()
    
    # Add test users
    test_users = [
        User(
            id="test-admin",
            email="admin@test.com",
            password_hash=hash_password("admin123"),
            full_name="Test Administrator",
            role=UserRole.ADMIN
        ),
        User(
            id="test-instructor",
            email="instructor@test.com",
            password_hash=hash_password("instructor123"),
            full_name="Test Instructor",
            role=UserRole.INSTRUCTOR
        ),
        User(
            id="test-student",
            email="student@test.com",
            password_hash=hash_password("student123"),
            full_name="Test Student",
            role=UserRole.STUDENT
        )
    ]
    users.extend(test_users)
    
    yield
    
    # Cleanup after test
    users.clear()
    user_sessions.clear()
    audit_logs.clear()
    blacklisted_tokens.clear()
    rate_limit_tracking.clear()


class TestHealthCheck:
    """Test service health and status endpoints"""
    
    def test_root_endpoint(self):
        """Test the root endpoint returns service information"""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "CogniFlow Authentication Service"
        assert data["status"] == "operational"
        assert "security_features" in data
        assert data["mode"] == "development"
    
    def test_health_check(self):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "authentication-service"


class TestAuthentication:
    """Test user authentication functionality"""
    
    def test_successful_login(self):
        """Test successful user login"""
        login_data = {
            "email": "student@test.com",
            "password": "student123"
        }
        
        response = client.post("/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user_id"] == "test-student"
        assert data["user_role"] == "student"
        assert "session_id" in data
        
        # Verify session was created
        assert len(user_sessions) == 1
        session = user_sessions[0]
        assert session.user_id == "test-student"
        assert session.status.value == "active"
        
        # Verify audit log entry
        assert len(audit_logs) == 1
        log_entry = audit_logs[0]
        assert log_entry.event_type.value == "login_success"
        assert log_entry.user_id == "test-student"
    
    def test_invalid_email_login(self):
        """Test login with invalid email"""
        login_data = {
            "email": "nonexistent@test.com",
            "password": "password123"
        }
        
        response = client.post("/login", json=login_data)
        assert response.status_code == 401
        
        data = response.json()
        assert "Invalid email or password" in data["detail"]
        
        # Verify audit log entry for failed login
        assert len(audit_logs) == 1
        log_entry = audit_logs[0]
        assert log_entry.event_type.value == "login_failure"
        assert log_entry.details["reason"] == "user_not_found"
    
    def test_invalid_password_login(self):
        """Test login with invalid password"""
        login_data = {
            "email": "student@test.com",
            "password": "wrongpassword"
        }
        
        response = client.post("/login", json=login_data)
        assert response.status_code == 401
        
        data = response.json()
        assert "Invalid email or password" in data["detail"]
        
        # Check that failed attempts counter increased
        user = next(u for u in users if u.email == "student@test.com")
        assert user.failed_login_attempts == 1
        
        # Verify audit log entry
        assert len(audit_logs) == 1
        log_entry = audit_logs[0]
        assert log_entry.event_type.value == "login_failure"
        assert log_entry.details["reason"] == "invalid_password"
    
    def test_account_lockout(self):
        """Test account lockout after multiple failed attempts"""
        login_data = {
            "email": "student@test.com",
            "password": "wrongpassword"
        }
        
        # Attempt login 5 times with wrong password
        for i in range(5):
            response = client.post("/login", json=login_data)
            assert response.status_code == 401
        
        # Check that user is locked out
        user = next(u for u in users if u.email == "student@test.com")
        assert user.failed_login_attempts == 5
        assert user.account_locked_until is not None
        assert user.account_locked_until > datetime.datetime.now(timezone.utc)
        
        # Try to login with correct password - should still fail due to lockout
        correct_login_data = {
            "email": "student@test.com",
            "password": "student123"
        }
        response = client.post("/login", json=correct_login_data)
        assert response.status_code == 423  # Locked status
        assert "temporarily locked" in response.json()["detail"]


class TestTokenOperations:
    """Test JWT token operations"""
    
    def test_token_refresh(self):
        """Test refresh token functionality"""
        # First, login to get tokens
        login_data = {
            "email": "student@test.com",
            "password": "student123"
        }
        login_response = client.post("/login", json=login_data)
        tokens = login_response.json()
        
        # Use refresh token to get new access token
        refresh_data = {
            "refresh_token": tokens["refresh_token"]
        }
        response = client.post("/refresh", json=refresh_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert data["refresh_token"] == tokens["refresh_token"]  # Same refresh token
        assert data["user_id"] == "test-student"
        
        # Verify new access token is different
        assert data["access_token"] != tokens["access_token"]
        
        # Verify audit log for token refresh
        refresh_logs = [log for log in audit_logs if log.event_type.value == "token_refresh"]
        assert len(refresh_logs) == 1
    
    def test_invalid_refresh_token(self):
        """Test refresh with invalid token"""
        refresh_data = {
            "refresh_token": "invalid.token.here"
        }
        response = client.post("/refresh", json=refresh_data)
        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]
    
    def test_logout_invalidates_tokens(self):
        """Test that logout properly invalidates tokens"""
        # Login first
        login_data = {
            "email": "student@test.com",
            "password": "student123"
        }
        login_response = client.post("/login", json=login_data)
        tokens = login_response.json()
        access_token = tokens["access_token"]
        
        # Verify we can access protected endpoint
        headers = {"Authorization": f"Bearer {access_token}"}
        me_response = client.get("/me", headers=headers)
        assert me_response.status_code == 200
        
        # Logout
        logout_response = client.post("/logout", headers=headers)
        assert logout_response.status_code == 200
        assert "Successfully logged out" in logout_response.json()["message"]
        
        # Verify token is now blacklisted and can't access protected endpoints
        me_response_after_logout = client.get("/me", headers=headers)
        assert me_response_after_logout.status_code == 401
        
        # Verify tokens are in blacklist
        assert access_token in blacklisted_tokens


class TestProtectedEndpoints:
    """Test protected endpoints and authorization"""
    
    def test_get_current_user(self):
        """Test getting current user profile"""
        # Login first
        login_data = {
            "email": "instructor@test.com",
            "password": "instructor123"
        }
        login_response = client.post("/login", json=login_data)
        access_token = login_response.json()["access_token"]
        
        # Get user profile
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/me", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["user_id"] == "test-instructor"
        assert data["email"] == "instructor@test.com"
        assert data["full_name"] == "Test Instructor"
        assert data["role"] == "instructor"
        assert data["is_active"] is True
    
    def test_unauthorized_access(self):
        """Test accessing protected endpoint without token"""
        response = client.get("/me")
        assert response.status_code == 401
        assert "Authentication credentials required" in response.json()["detail"]
    
    def test_invalid_token_access(self):
        """Test accessing protected endpoint with invalid token"""
        headers = {"Authorization": "Bearer invalid.token.here"}
        response = client.get("/me", headers=headers)
        assert response.status_code == 401
        assert "Invalid authentication credentials" in response.json()["detail"]


class TestRoleBasedAccess:
    """Test role-based access control"""
    
    def test_admin_access_to_audit_logs(self):
        """Test that admin can access audit logs"""
        # Login as admin
        login_data = {
            "email": "admin@test.com",
            "password": "admin123"
        }
        login_response = client.post("/login", json=login_data)
        access_token = login_response.json()["access_token"]
        
        # Access audit logs
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/admin/audit-logs", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "audit_logs" in data
        assert "total_count" in data
        assert len(data["audit_logs"]) >= 1  # Should have login event
    
    def test_student_cannot_access_admin_endpoints(self):
        """Test that student cannot access admin-only endpoints"""
        # Login as student
        login_data = {
            "email": "student@test.com",
            "password": "student123"
        }
        login_response = client.post("/login", json=login_data)
        access_token = login_response.json()["access_token"]
        
        # Try to access admin endpoint
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/admin/audit-logs", headers=headers)
        assert response.status_code == 403
        assert "Insufficient privileges" in response.json()["detail"]
    
    def test_admin_access_to_active_sessions(self):
        """Test admin access to active sessions endpoint"""
        # Login as admin
        login_data = {
            "email": "admin@test.com",
            "password": "admin123"
        }
        login_response = client.post("/login", json=login_data)
        access_token = login_response.json()["access_token"]
        
        # Access active sessions
        headers = {"Authorization": f"Bearer {access_token}"}
        response = client.get("/admin/active-sessions", headers=headers)
        assert response.status_code == 200
        
        data = response.json()
        assert "active_sessions" in data
        assert "total_count" in data
        assert len(data["active_sessions"]) >= 1  # Should have admin session


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limiting_blocks_requests(self):
        """Test that rate limiting blocks excessive requests from same IP"""
        login_data = {
            "email": "nonexistent@test.com",
            "password": "wrongpassword"
        }
        
        # Make 5 failed login attempts (should trigger rate limiting)
        for i in range(5):
            response = client.post("/login", json=login_data)
            assert response.status_code == 401
        
        # 6th attempt should be rate limited
        response = client.post("/login", json=login_data)
        assert response.status_code == 429
        assert "Too many login attempts" in response.json()["detail"]


class TestSecurityLogging:
    """Test security event logging"""
    
    def test_security_events_are_logged(self):
        """Test that security events are properly logged"""
        # Clear audit logs
        audit_logs.clear()
        
        # Perform various operations that should be logged
        login_data = {
            "email": "student@test.com",
            "password": "student123"
        }
        
        # Successful login
        login_response = client.post("/login", json=login_data)
        access_token = login_response.json()["access_token"]
        
        # Logout
        headers = {"Authorization": f"Bearer {access_token}"}
        client.post("/logout", headers=headers)
        
        # Check audit logs
        assert len(audit_logs) >= 2
        
        # Find login and logout events
        login_events = [log for log in audit_logs if log.event_type.value == "login_success"]
        logout_events = [log for log in audit_logs if log.event_type.value == "logout"]
        
        assert len(login_events) == 1
        assert len(logout_events) == 1
        
        # Verify log details
        login_log = login_events[0]
        assert login_log.user_id == "test-student"
        assert login_log.ip_address is not None
        assert login_log.user_agent is not None
        assert "session_id" in login_log.details


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
