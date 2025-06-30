"""
Test suite for CogniFlow Authentication Service

This module contains comprehensive tests for the authentication service,
covering all security scenarios, edge cases, and production considerations.

Test Categories:
- Authentication flow testing
- Token validation and refresh
- Role-based access control
- Rate limiting and security
- Audit logging verification
- Error handling and edge cases

Author: CogniFlow Development Team
Version: 1.0.0
"""

import pytest
import asyncio
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import jwt

# Import the authentication service
from main import app, auth_service, auth_store, SECRET_KEY, ALGORITHM

# Initialize test client
client = TestClient(app)

class TestAuthenticationFlow:
    """Test suite for basic authentication flow."""
    
    def test_successful_login(self):
        """Test successful user login with valid credentials."""
        response = client.post("/login", json={
            "email": "admin@cogniflow.com",
            "password": "admin123",
            "remember_me": False
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["user_id"] is not None
        assert data["role"] == "admin"
        assert data["expires_in"] > 0
        
        # Verify token is valid JWT
        token_payload = jwt.decode(data["access_token"], SECRET_KEY, algorithms=[ALGORITHM])
        assert token_payload["type"] == "access"
        assert token_payload["email"] == "admin@cogniflow.com"
    
    def test_invalid_credentials(self):
        """Test login with invalid credentials."""
        response = client.post("/login", json={
            "email": "admin@cogniflow.com",
            "password": "wrongpassword",
            "remember_me": False
        })
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_nonexistent_user(self):
        """Test login with non-existent user email."""
        response = client.post("/login", json={
            "email": "nonexistent@cogniflow.com",
            "password": "password123",
            "remember_me": False
        })
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_password_validation(self):
        """Test password strength validation."""
        response = client.post("/login", json={
            "email": "admin@cogniflow.com",
            "password": "weak",  # Too short
            "remember_me": False
        })
        
        assert response.status_code == 422
        assert "Password must be at least 8 characters long" in str(response.json())

class TestTokenManagement:
    """Test suite for JWT token management."""
    
    def setup_method(self):
        """Set up test data for each test method."""
        # Get a valid token for testing
        login_response = client.post("/login", json={
            "email": "admin@cogniflow.com",
            "password": "admin123"
        })
        self.token_data = login_response.json()
        self.access_token = self.token_data["access_token"]
        self.refresh_token = self.token_data["refresh_token"]
        self.headers = {"Authorization": f"Bearer {self.access_token}"}
    
    def test_token_refresh(self):
        """Test successful token refresh."""
        response = client.post("/refresh", json={
            "refresh_token": self.refresh_token
        })
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify new tokens are different
        assert data["access_token"] != self.access_token
        assert data["refresh_token"] != self.refresh_token
        
        # Verify old refresh token is blacklisted
        assert self.refresh_token in auth_store.blacklisted_tokens
    
    def test_invalid_refresh_token(self):
        """Test refresh with invalid token."""
        response = client.post("/refresh", json={
            "refresh_token": "invalid_token"
        })
        
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]
    
    def test_expired_token_access(self):
        """Test access with expired token."""
        # Create an expired token
        expired_payload = {
            "sub": "user123",
            "email": "test@example.com",
            "role": "student",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
            "type": "access"
        }
        expired_token = jwt.encode(expired_payload, SECRET_KEY, algorithm=ALGORITHM)
        
        response = client.get("/me", headers={
            "Authorization": f"Bearer {expired_token}"
        })
        
        assert response.status_code == 401
        assert "Token has expired" in response.json()["detail"]
    
    def test_get_current_user(self):
        """Test retrieving current user information."""
        response = client.get("/me", headers=self.headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["email"] == "admin@cogniflow.com"
        assert data["role"] == "admin"
        assert data["is_active"] is True
    
    def test_logout(self):
        """Test user logout functionality."""
        response = client.post("/logout", headers=self.headers)
        
        assert response.status_code == 200
        assert "Successfully logged out" in response.json()["message"]
        
        # Verify token is blacklisted
        assert self.access_token in auth_store.blacklisted_tokens
        
        # Verify token can't be used after logout
        response = client.get("/me", headers=self.headers)
        assert response.status_code == 401

class TestRoleBasedAccess:
    """Test suite for role-based access control."""
    
    def setup_method(self):
        """Set up tokens for different user roles."""
        # Admin token
        admin_response = client.post("/login", json={
            "email": "admin@cogniflow.com",
            "password": "admin123"
        })
        self.admin_headers = {
            "Authorization": f"Bearer {admin_response.json()['access_token']}"
        }
        
        # Student token
        student_response = client.post("/login", json={
            "email": "student@cogniflow.com",
            "password": "student123"
        })
        self.student_headers = {
            "Authorization": f"Bearer {student_response.json()['access_token']}"
        }
    
    def test_admin_access_audit_logs(self):
        """Test admin access to audit logs."""
        response = client.get("/admin/audit-logs", headers=self.admin_headers)
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_student_access_denied_audit_logs(self):
        """Test student access denied to admin endpoints."""
        response = client.get("/admin/audit-logs", headers=self.student_headers)
        
        assert response.status_code == 403
        assert "Insufficient permissions" in response.json()["detail"]
    
    def test_admin_access_active_sessions(self):
        """Test admin access to active sessions."""
        response = client.get("/admin/active-sessions", headers=self.admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "total_sessions" in data
        assert "sessions" in data

class TestSecurityFeatures:
    """Test suite for security features."""
    
    def test_rate_limiting(self):
        """Test rate limiting for login attempts."""
        # Clear any existing rate limit data
        auth_store.rate_limit_attempts.clear()
        
        # Make multiple failed login attempts
        for i in range(6):  # Exceed the limit of 5
            response = client.post("/login", json={
                "email": "admin@cogniflow.com",
                "password": "wrongpassword"
            })
            
            if i < 5:
                assert response.status_code == 401  # Invalid credentials
            else:
                assert response.status_code == 429  # Rate limited
                assert "Too many login attempts" in response.json()["detail"]
    
    def test_account_lockout(self):
        """Test account lockout after failed attempts."""
        # Reset failed attempts
        auth_store.users["admin@cogniflow.com"]["failed_attempts"] = 0
        auth_store.users["admin@cogniflow.com"]["locked_until"] = None
        
        # Make 5 failed attempts to trigger lockout
        for i in range(5):
            client.post("/login", json={
                "email": "admin@cogniflow.com",
                "password": "wrongpassword"
            })
        
        # Verify account is locked
        user_data = auth_store.users["admin@cogniflow.com"]
        assert user_data["failed_attempts"] == 5
        assert user_data["locked_until"] is not None
        
        # Attempt login with correct password should fail due to lockout
        response = client.post("/login", json={
            "email": "admin@cogniflow.com",
            "password": "admin123"
        })
        assert response.status_code == 423
        assert "Account is temporarily locked" in response.json()["detail"]
    
    def test_token_blacklisting(self):
        """Test token blacklisting functionality."""
        # Login to get a token
        login_response = client.post("/login", json={
            "email": "admin@cogniflow.com",
            "password": "admin123"
        })
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Use token successfully
        response = client.get("/me", headers=headers)
        assert response.status_code == 200
        
        # Logout to blacklist token
        client.post("/logout", headers=headers)
        
        # Try to use blacklisted token
        response = client.get("/me", headers=headers)
        assert response.status_code == 401
        assert "Token has been revoked" in response.json()["detail"]

class TestAuditLogging:
    """Test suite for audit logging functionality."""
    
    def test_successful_login_logged(self):
        """Test that successful logins are logged."""
        initial_log_count = len(auth_store.audit_logs)
        
        client.post("/login", json={
            "email": "admin@cogniflow.com",
            "password": "admin123"
        })
        
        # Verify log entry was created
        assert len(auth_store.audit_logs) > initial_log_count
        
        # Find the login log entry
        login_log = next(
            (log for log in auth_store.audit_logs 
             if log.action == "login" and log.status.value == "success"),
            None
        )
        assert login_log is not None
        assert login_log.email == "admin@cogniflow.com"
    
    def test_failed_login_logged(self):
        """Test that failed logins are logged."""
        initial_log_count = len(auth_store.audit_logs)
        
        client.post("/login", json={
            "email": "admin@cogniflow.com",
            "password": "wrongpassword"
        })
        
        # Verify log entry was created
        assert len(auth_store.audit_logs) > initial_log_count
        
        # Find the failed login log entry
        failed_log = next(
            (log for log in auth_store.audit_logs 
             if log.action == "login" and log.status.value == "failed"),
            None
        )
        assert failed_log is not None
        assert failed_log.email == "admin@cogniflow.com"
        assert failed_log.details["reason"] == "invalid_password"
    
    def test_logout_logged(self):
        """Test that logout events are logged."""
        # Login first
        login_response = client.post("/login", json={
            "email": "admin@cogniflow.com",
            "password": "admin123"
        })
        headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}
        
        initial_log_count = len(auth_store.audit_logs)
        
        # Logout
        client.post("/logout", headers=headers)
        
        # Verify logout was logged
        assert len(auth_store.audit_logs) > initial_log_count
        
        logout_log = next(
            (log for log in auth_store.audit_logs 
             if log.action == "logout" and log.status.value == "success"),
            None
        )
        assert logout_log is not None

class TestErrorHandling:
    """Test suite for error handling scenarios."""
    
    def test_malformed_token(self):
        """Test handling of malformed JWT tokens."""
        response = client.get("/me", headers={
            "Authorization": "Bearer malformed.token.here"
        })
        
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]
    
    def test_missing_authorization_header(self):
        """Test handling of missing authorization header."""
        response = client.get("/me")
        
        assert response.status_code == 403
        assert "Not authenticated" in str(response.json())
    
    def test_invalid_email_format(self):
        """Test handling of invalid email format in login."""
        response = client.post("/login", json={
            "email": "invalid-email",
            "password": "password123"
        })
        
        assert response.status_code == 422
        assert "value is not a valid email address" in str(response.json())

class TestHealthEndpoint:
    """Test suite for service health endpoint."""
    
    def test_health_check(self):
        """Test service health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["service"] == "CogniFlow Authentication Service"
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert data["mode"] == "development"
        assert "statistics" in data

# Integration test for complete authentication flow
class TestIntegrationFlow:
    """Integration tests for complete authentication workflows."""
    
    def test_complete_auth_flow(self):
        """Test complete authentication flow from login to logout."""
        # Step 1: Login
        login_response = client.post("/login", json={
            "email": "instructor@cogniflow.com",
            "password": "instructor123"
        })
        assert login_response.status_code == 200
        
        tokens = login_response.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        
        # Step 2: Access protected resource
        me_response = client.get("/me", headers=headers)
        assert me_response.status_code == 200
        assert me_response.json()["role"] == "instructor"
        
        # Step 3: Refresh token
        refresh_response = client.post("/refresh", json={
            "refresh_token": tokens["refresh_token"]
        })
        assert refresh_response.status_code == 200
        
        new_tokens = refresh_response.json()
        new_headers = {"Authorization": f"Bearer {new_tokens['access_token']}"}
        
        # Step 4: Use new token
        me_response_new = client.get("/me", headers=new_headers)
        assert me_response_new.status_code == 200
        
        # Step 5: Logout
        logout_response = client.post("/logout", headers=new_headers)
        assert logout_response.status_code == 200
        
        # Step 6: Verify token is invalidated
        me_response_after_logout = client.get("/me", headers=new_headers)
        assert me_response_after_logout.status_code == 401

if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
