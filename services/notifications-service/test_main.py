"""
Comprehensive test suite for CogniFlow Notifications Service
===========================================================

Tests cover:
- Notification creation and delivery
- WebSocket real-time notifications  
- Email notifications
- User preferences management
- Bulk notifications
- Templates and analytics
- Error handling and edge cases

Author: CogniFlow Development Team
"""

import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from unittest.mock import patch, AsyncMock

from main import app, notification_store, notification_service, connection_manager
from main import (
    NotificationType, NotificationPriority, DeliveryChannel, 
    NotificationStatus, NotificationCreate, BulkNotificationCreate,
    PreferencesUpdate
)

# Test client
client = TestClient(app)

@pytest.fixture(autouse=True)
def reset_store():
    """Reset in-memory store before each test"""
    notification_store.notifications.clear()
    notification_store.user_notifications.clear()
    notification_store.preferences.clear()
    connection_manager.active_connections.clear()
    yield
    notification_store.notifications.clear()
    notification_store.user_notifications.clear()
    notification_store.preferences.clear()
    connection_manager.active_connections.clear()

class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_check(self):
        """Test basic health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "notifications-service"
        assert data["mode"] == "no-database"

class TestNotificationCreation:
    """Test notification creation and basic functionality"""
    
    def test_create_simple_notification(self):
        """Test creating a basic notification"""
        notification_data = {
            "user_id": "user1",
            "type": "system",
            "title": "Test Notification",
            "message": "This is a test.",
            "priority": "normal",
            "channels": ["real_time"]
        }
        
        response = client.post("/notifications", json=notification_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["user_id"] == "user1"
        assert data["title"] == "Test Notification"
        assert data["status"] == "unread"  # Should be sent immediately
        assert "id" in data
        assert "created_at" in data
    
    def test_create_notification_with_all_fields(self):
        """Test creating notification with all optional fields"""
        future_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        expire_time = (datetime.utcnow() + timedelta(days=7)).isoformat()
        
        notification_data = {
            "user_id": "user456",
            "type": "assignment_due",
            "title": "Assignment Due Soon",
            "message": "Your assignment is due in 24 hours",
            "priority": "high",
            "channels": ["real_time", "email"],
            "metadata": {
                "course_id": "course123",
                "assignment_id": "assign456",
                "user_email": "user@example.com"
            },
            "scheduled_for": future_time,
            "expires_at": expire_time
        }
        
        response = client.post("/notifications", json=notification_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["priority"] == "high"
        assert len(data["channels"]) == 2
        assert "course_id" in data["metadata"]
        assert data["status"] == "pending"  # Should be pending due to scheduling
    
    def test_create_notification_invalid_data(self):
        """Test creating notification with invalid data"""
        notification_data = {
            "user_id": "",  # Empty user_id
            "type": "invalid_type",
            "title": "",  # Empty title
            "message": "Test message"
        }
        
        response = client.post("/notifications", json=notification_data)
        assert response.status_code == 422  # Validation error

class TestBulkNotifications:
    """Test bulk notification creation"""
    
    def test_create_bulk_notifications(self):
        """Test creating notifications for multiple users"""
        bulk_data = {
            "user_ids": ["user1", "user2"],
            "type": "system",
            "title": "Bulk Test",
            "message": "Bulk message.",
            "priority": "normal",
            "channels": ["real_time"]
        }
        
        response = client.post("/notifications/bulk", json=bulk_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["count"] == 2
        
        # Check that all notifications were created
        for notification in data["notifications"]:
            assert notification["type"] == "system"
            assert notification["title"] == "Bulk Test"
            assert notification["user_id"] in ["user1", "user2"]
    
    def test_bulk_notifications_empty_user_list(self):
        """Test bulk notifications with empty user list"""
        bulk_data = {
            "user_ids": [],
            "type": "system",
            "title": "Test",
            "message": "Test message"
        }
        
        response = client.post("/notifications/bulk", json=bulk_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Created 0 notifications"
        assert len(data["notifications"]) == 0

class TestUserNotifications:
    """Test retrieving user notifications"""
    
    @pytest.fixture
    def setup_notifications(self):
        """Create test notifications for a user"""
        user_id = "testuser"
        notifications = []
        
        for i in range(5):
            notification_data = NotificationCreate(
                user_id=user_id,
                type=NotificationType.COURSE_ENROLLMENT,
                title=f"Test Notification {i}",
                message=f"Test message {i}"
            )
            notification = asyncio.run(notification_service.create_notification(notification_data))
            notifications.append(notification)
        
        return user_id, notifications
    
    def test_get_user_notifications(self, setup_notifications):
        """Test retrieving all notifications for a user"""
        user_id, _ = setup_notifications
        
        response = client.get(f"/notifications/user/{user_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 5
        assert all(notification["user_id"] == user_id for notification in data)
    
    def test_get_user_notifications_with_limit(self, setup_notifications):
        """Test retrieving notifications with limit"""
        user_id, _ = setup_notifications
        
        response = client.get(f"/notifications/user/{user_id}?limit=3")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 3
    
    def test_get_unread_notifications_only(self, setup_notifications):
        """Test retrieving only unread notifications"""
        user_id, notifications = setup_notifications
        
        # Mark some notifications as read
        for i in range(2):
            asyncio.run(notification_service.mark_as_read(notifications[i].id, user_id))
        
        response = client.get(f"/notifications/user/{user_id}?unread_only=true")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 3  # Should have 3 unread notifications

class TestNotificationStatus:
    """Test notification status management"""
    
    def test_mark_notification_as_read(self):
        """Test marking notification as read"""
        # Create a notification
        notification_data = {
            "user_id": "user1",
            "type": "system",
            "title": "Read Test",
            "message": "msg",
            "priority": "normal",
            "channels": ["real_time"]
        }
        
        create_response = client.post("/notifications", json=notification_data)
        notification_id = create_response.json()["id"]
        
        # Mark as read
        response = client.put(f"/notifications/{notification_id}/read?user_id=user1")
        assert response.status_code == 200
        assert response.json()["message"] == "Notification marked as read"
        
        # Verify it's marked as read
        user_notifications = client.get("/notifications/user/user1")
        notification = user_notifications.json()[0]
        assert notification["status"] == "read"
        assert notification["read_at"] is not None
    
    def test_mark_nonexistent_notification_as_read(self):
        """Test marking non-existent notification as read"""
        response = client.put("/notifications/nonexistent/read?user_id=user1")
        assert response.status_code == 404
    
    def test_mark_notification_as_read_wrong_user(self):
        """Test marking notification as read with wrong user"""
        # Create a notification for user1
        notification_data = {
            "user_id": "user1",
            "type": "system",
            "title": "Test Notification",
            "message": "Test message"
        }
        
        create_response = client.post("/notifications", json=notification_data)
        notification_id = create_response.json()["id"]
        
        # Try to mark as read with different user
        response = client.put(f"/notifications/{notification_id}/read?user_id=user2")
        assert response.status_code == 404

class TestPreferences:
    """Test user preferences management"""
    
    def test_get_and_update_preferences(self):
        """Test getting and updating user preferences"""
        # Get default
        response = client.get("/preferences/user1")
        assert response.status_code == 200
        prefs = response.json()
        assert "real_time" in prefs["enabled_channels"]
        
        # Update preferences
        update_data = {"enabled_channels": ["email"]}
        response = client.put("/preferences/user1", json=update_data)
        assert response.status_code == 200
        
        # Verify updates
        get_response = client.get("/preferences/user1")
        data = get_response.json()
        assert data["enabled_channels"] == ["email"]

class TestNotificationTemplates:
    """Test notification templates"""
    
    def test_get_templates(self):
        """Test retrieving notification templates"""
        response = client.get("/templates")
        assert response.status_code == 200
        
        templates = response.json()
        assert len(templates) > 0
        
        # Check that default templates exist
        template_types = [template["type"] for template in templates]
        assert "course_enrollment" in template_types
        assert "assignment_due" in template_types
        assert "progress_milestone" in template_types
    
    def test_template_structure(self):
        """Test template data structure"""
        response = client.get("/templates")
        templates = response.json()
        
        for template in templates:
            assert "id" in template
            assert "name" in template
            assert "type" in template
            assert "subject_template" in template
            assert "body_template" in template
            assert "variables" in template
            assert isinstance(template["variables"], list)

class TestAnalytics:
    """Test notification analytics"""
    
    def test_delivery_statistics_empty(self):
        """Test analytics with no notifications"""
        response = client.get("/analytics/delivery-stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_notifications"] == 0
        assert data["delivery_stats"] == {}
        assert data["channel_stats"] == {}
        assert data["type_stats"] == {}
    
    def test_delivery_statistics_with_data(self):
        """Test analytics with notifications"""
        # Create some test notifications
        notifications_data = [
            {
                "user_id": "user1",
                "type": "course_enrollment",
                "title": "Test 1",
                "message": "Message 1",
                "channels": ["real_time"]
            },
            {
                "user_id": "user2", 
                "type": "assignment_due",
                "title": "Test 2",
                "message": "Message 2",
                "channels": ["real_time", "email"]
            },
            {
                "user_id": "user3",
                "type": "course_enrollment", 
                "title": "Test 3",
                "message": "Message 3",
                "channels": ["push"]
            }
        ]
        
        for notification_data in notifications_data:
            client.post("/notifications", json=notification_data)
        
        response = client.get("/analytics/delivery-stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_notifications"] == 3
        
        # Check delivery stats
        assert "sent" in data["delivery_stats"]
        assert data["delivery_stats"]["sent"]["count"] == 3
        
        # Check channel stats
        assert "real_time" in data["channel_stats"]
        assert data["channel_stats"]["real_time"]["count"] == 2
        
        # Check type stats
        assert "course_enrollment" in data["type_stats"]
        assert data["type_stats"]["course_enrollment"]["count"] == 2

class TestWebSocketConnections:
    """Test WebSocket functionality"""
    
    def test_websocket_connection(self):
        """Test WebSocket connection and basic messaging"""
        with client.websocket_connect("/ws/testuser") as websocket:
            # Send ping
            websocket.send_text(json.dumps({"type": "ping"}))
            
            # Should receive pong
            data = websocket.receive_text()
            message = json.loads(data)
            assert message["type"] == "pong"
    
    def test_websocket_mark_read(self):
        """Test marking notification as read via WebSocket"""
        # Create a notification first
        notification_data = {
            "user_id": "wsuser",
            "type": "course_enrollment",
            "title": "WebSocket Test",
            "message": "Test message"
        }
        
        create_response = client.post("/notifications", json=notification_data)
        notification_id = create_response.json()["id"]
        
        with client.websocket_connect("/ws/wsuser") as websocket:
            # Send mark as read request
            websocket.send_text(json.dumps({
                "type": "mark_read",
                "notification_id": notification_id
            }))
            
            # Verify notification is marked as read
            user_notifications = client.get("/notifications/user/wsuser")
            notification = user_notifications.json()[0]
            assert notification["status"] == "read"

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_user_id_in_preferences(self):
        """Test handling of invalid user ID in preferences"""
        response = client.get("/preferences/")
        assert response.status_code == 404
    
    def test_malformed_notification_data(self):
        """Test handling of malformed notification data"""
        # Missing required fields
        response = client.post("/notifications", json={})
        assert response.status_code == 422
        
        # Invalid enum values
        response = client.post("/notifications", json={
            "user_id": "user123",
            "type": "invalid_type",
            "title": "Test",
            "message": "Test message"
        })
        assert response.status_code == 422
    
    def test_nonexistent_notification_operations(self):
        """Test operations on non-existent notifications"""
        # Try to mark non-existent notification as read
        response = client.put("/notifications/nonexistent/read?user_id=user123")
        assert response.status_code == 404
    
    def test_websocket_invalid_message(self):
        """Test WebSocket with invalid message format"""
        with client.websocket_connect("/ws/testuser") as websocket:
            # Send invalid JSON
            websocket.send_text("invalid json")
            # Connection should remain open despite error

class TestScheduledNotifications:
    """Test scheduled notification functionality"""
    
    def test_create_scheduled_notification(self):
        """Test creating a notification scheduled for the future"""
        future_time = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        
        notification_data = {
            "user_id": "user123",
            "type": "course_reminder",
            "title": "Scheduled Reminder",
            "message": "This is a scheduled notification",
            "scheduled_for": future_time
        }
        
        response = client.post("/notifications", json=notification_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "pending"  # Should be pending until scheduled time
        assert data["scheduled_for"] is not None
    
    def test_immediate_delivery_past_schedule(self):
        """Test that notifications scheduled in the past are delivered immediately"""
        past_time = (datetime.utcnow() - timedelta(hours=1)).isoformat()
        
        notification_data = {
            "user_id": "user123",
            "type": "course_reminder",
            "title": "Past Scheduled Notification",
            "message": "This should be delivered immediately",
            "scheduled_for": past_time
        }
        
        response = client.post("/notifications", json=notification_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "sent"  # Should be sent immediately

# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestServiceIntegration:
    """Test integration scenarios with multiple service components"""
    
    def test_end_to_end_notification_flow(self):
        """Test complete notification flow from creation to delivery"""
        user_id = "integration_user"
        
        # 1. Set user preferences
        prefs_data = {
            "email_enabled": True,
            "push_enabled": False,
            "email_types": ["course_enrollment", "assignment_due"]
        }
        client.put(f"/preferences/{user_id}", json=prefs_data)
        
        # 2. Create notification
        notification_data = {
            "user_id": user_id,
            "type": "course_enrollment",
            "title": "Integration Test Course",
            "message": "Welcome to the integration test course!",
            "channels": ["real_time", "email"],
            "metadata": {"user_email": "test@example.com"}
        }
        
        create_response = client.post("/notifications", json=notification_data)
        assert create_response.status_code == 200
        notification_id = create_response.json()["id"]
        
        # 3. Verify notification was created and delivered
        user_notifications = client.get(f"/notifications/user/{user_id}")
        assert len(user_notifications.json()) == 1
        notification = user_notifications.json()[0]
        assert notification["status"] == "sent"
        
        # 4. Mark as read
        read_response = client.put(f"/notifications/{notification_id}/read?user_id={user_id}")
        assert read_response.status_code == 200
        
        # 5. Verify read status
        updated_notifications = client.get(f"/notifications/user/{user_id}")
        updated_notification = updated_notifications.json()[0]
        assert updated_notification["status"] == "read"
        assert updated_notification["read_at"] is not None
    
    def test_bulk_notification_with_preferences(self):
        """Test bulk notifications respecting user preferences"""
        users = ["user1", "user2", "user3"]
        
        # Set different preferences for each user
        client.put("/preferences/user1", json={"email_enabled": True, "push_enabled": False})
        client.put("/preferences/user2", json={"email_enabled": False, "push_enabled": True})
        client.put("/preferences/user3", json={"email_enabled": True, "push_enabled": True})
        
        # Create bulk notification
        bulk_data = {
            "user_ids": users,
            "type": "system_announcement",
            "title": "System Update",
            "message": "The system has been updated",
            "channels": ["real_time", "email", "push"]
        }
        
        response = client.post("/notifications/bulk", json=bulk_data)
        assert response.status_code == 200
        
        # Verify all notifications were created
        data = response.json()
        assert len(data["notifications"]) == 3
        
        # Verify each user received their notification
        for user_id in users:
            user_notifications = client.get(f"/notifications/user/{user_id}")
            assert len(user_notifications.json()) == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
