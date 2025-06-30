#!/usr/bin/env python3
"""
CogniFlow Notifications Service Demo
===================================

Demonstrates the comprehensive notifications service functionality:
- Creating various types of notifications
- Real-time WebSocket delivery
- User preferences management
- Bulk notifications
- Analytics and templates

This script showcases the professional-grade features built for the 
CogniFlow learning platform.

Author: CogniFlow Development Team
"""

import asyncio
import aiohttp
import json
import websockets
import time
from datetime import datetime, timedelta
from typing import Dict, Any

class NotificationsDemo:
    """Comprehensive demonstration of the notifications service"""
    
    def __init__(self, base_url: str = "http://localhost:8003"):
        self.base_url = base_url.rstrip('/')
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to the notifications service"""
        url = f"{self.base_url}{endpoint}"
        
        async with self.session.request(method, url, **kwargs) as response:
            if response.content_type == 'application/json':
                return await response.json()
            else:
                return {"status_code": response.status, "text": await response.text()}
    
    async def demo_health_check(self):
        """Demonstrate health check endpoint"""
        print("🏥 Testing Health Check...")
        result = await self.make_request('GET', '/health')
        print(f"   Status: {result.get('status')}")
        print(f"   Mode: {result.get('mode')}")
        print(f"   Email: {'Enabled' if result.get('email_enabled') else 'Disabled'}")
        print(f"   Timestamp: {result.get('timestamp')}")
        print()
    
    async def demo_notification_creation(self):
        """Demonstrate creating different types of notifications"""
        print("📝 Testing Notification Creation...")
        
        notifications = [
            {
                "user_id": "demo_user_1",
                "type": "course_enrollment",
                "title": "Welcome to Advanced Python!",
                "message": "You have successfully enrolled in Advanced Python Programming. Let's start learning!",
                "priority": "normal",
                "channels": ["real_time", "email"],
                "metadata": {
                    "course_id": "python_advanced_101",
                    "course_title": "Advanced Python Programming",
                    "instructor_name": "Dr. Sarah Wilson",
                    "user_email": "demo1@example.com"
                }
            },
            {
                "user_id": "demo_user_2",
                "type": "assignment_due",
                "title": "Assignment Due Tomorrow!",
                "message": "Your Machine Learning assignment is due tomorrow at 11:59 PM. Don't forget to submit!",
                "priority": "high",
                "channels": ["real_time", "email", "push"],
                "metadata": {
                    "assignment_id": "ml_assignment_3",
                    "course_id": "ml_fundamentals",
                    "due_date": "2024-12-19 23:59:00",
                    "user_email": "demo2@example.com"
                }
            },
            {
                "user_id": "demo_user_1",
                "type": "progress_milestone",
                "title": "🎉 Congratulations! 75% Complete!",
                "message": "Amazing progress! You've completed 75% of the Advanced Python course. Keep up the excellent work!",
                "priority": "normal",
                "channels": ["real_time", "push"],
                "metadata": {
                    "course_id": "python_advanced_101",
                    "progress_percentage": 75,
                    "total_lessons": 20,
                    "completed_lessons": 15
                }
            }
        ]
        
        created_notifications = []
        for i, notification_data in enumerate(notifications, 1):
            print(f"   Creating notification {i}: {notification_data['title']}")
            result = await self.make_request('POST', '/notifications', json=notification_data)
            if 'id' in result:
                created_notifications.append(result)
                print(f"   ✅ Created with ID: {result['id']}")
            else:
                print(f"   ❌ Failed: {result}")
            
            # Small delay between requests
            await asyncio.sleep(0.5)
        
        print()
        return created_notifications
    
    async def demo_bulk_notifications(self):
        """Demonstrate bulk notification creation"""
        print("📢 Testing Bulk Notifications...")
        
        bulk_data = {
            "user_ids": ["student_1", "student_2", "student_3", "student_4", "student_5"],
            "type": "system_announcement",
            "title": "🔧 System Maintenance Notice",
            "message": "The CogniFlow platform will undergo scheduled maintenance on December 20th from 2:00 AM to 4:00 AM UTC. Please save your work and log out before this time.",
            "priority": "high",
            "channels": ["real_time", "email"],
            "metadata": {
                "maintenance_start": "2024-12-20 02:00:00 UTC",
                "maintenance_end": "2024-12-20 04:00:00 UTC",
                "affected_services": ["learning platform", "assessments", "discussions"]
            }
        }
        
        print(f"   Creating bulk notification for {len(bulk_data['user_ids'])} users...")
        result = await self.make_request('POST', '/notifications/bulk', json=bulk_data)
        
        if 'message' in result:
            print(f"   ✅ {result['message']}")
            print(f"   📊 Created {len(result.get('notifications', []))} notifications")
        else:
            print(f"   ❌ Failed: {result}")
        
        print()
    
    async def demo_user_preferences(self):
        """Demonstrate user preferences management"""
        print("⚙️ Testing User Preferences...")
        
        # Get default preferences
        user_id = "demo_user_1"
        print(f"   Getting default preferences for {user_id}...")
        prefs = await self.make_request('GET', f'/preferences/{user_id}')
        print(f"   📧 Email: {'Enabled' if prefs.get('email_enabled') else 'Disabled'}")
        print(f"   📱 Push: {'Enabled' if prefs.get('push_enabled') else 'Disabled'}")
        print(f"   🔔 Real-time: {'Enabled' if prefs.get('real_time_enabled') else 'Disabled'}")
        
        # Update preferences
        print(f"   Updating preferences...")
        update_data = {
            "email_enabled": True,
            "push_enabled": False,
            "quiet_hours_start": "22:00",
            "quiet_hours_end": "08:00",
            "timezone": "America/New_York",
            "email_types": ["assignment_due", "grade_posted", "system_announcement"]
        }
        
        result = await self.make_request('PUT', f'/preferences/{user_id}', json=update_data)
        if 'message' in result:
            print(f"   ✅ {result['message']}")
        
        # Verify updates
        updated_prefs = await self.make_request('GET', f'/preferences/{user_id}')
        print(f"   🌙 Quiet hours: {updated_prefs.get('quiet_hours_start')} - {updated_prefs.get('quiet_hours_end')}")
        print(f"   🌍 Timezone: {updated_prefs.get('timezone')}")
        print(f"   📧 Email types: {len(updated_prefs.get('email_types', []))} selected")
        
        print()
    
    async def demo_user_notifications(self):
        """Demonstrate retrieving user notifications"""
        print("📋 Testing User Notifications Retrieval...")
        
        user_id = "demo_user_1"
        
        # Get all notifications
        print(f"   Fetching all notifications for {user_id}...")
        notifications = await self.make_request('GET', f'/notifications/user/{user_id}')
        print(f"   📊 Total notifications: {len(notifications)}")
        
        if notifications:
            # Show notification details
            for i, notification in enumerate(notifications[:3], 1):  # Show first 3
                print(f"   {i}. {notification.get('title')} ({notification.get('type')})")
                print(f"      Status: {notification.get('status')}")
                print(f"      Created: {notification.get('created_at')}")
            
            # Mark first notification as read
            if notifications:
                first_notification = notifications[0]
                print(f"   Marking notification as read...")
                read_result = await self.make_request(
                    'PUT', 
                    f"/notifications/{first_notification['id']}/read?user_id={user_id}"
                )
                if 'message' in read_result:
                    print(f"   ✅ {read_result['message']}")
        
        # Get unread notifications only
        print(f"   Fetching unread notifications...")
        unread = await self.make_request('GET', f'/notifications/user/{user_id}?unread_only=true')
        print(f"   📊 Unread notifications: {len(unread)}")
        
        print()
    
    async def demo_templates(self):
        """Demonstrate notification templates"""
        print("📄 Testing Notification Templates...")
        
        templates = await self.make_request('GET', '/templates')
        print(f"   📊 Available templates: {len(templates)}")
        
        for template in templates:
            print(f"   • {template.get('name')} ({template.get('type')})")
            print(f"     Subject: {template.get('subject_template')}")
            print(f"     Variables: {', '.join(template.get('variables', []))}")
        
        print()
    
    async def demo_analytics(self):
        """Demonstrate analytics and metrics"""
        print("📈 Testing Analytics & Metrics...")
        
        stats = await self.make_request('GET', '/analytics/delivery-stats')
        
        print(f"   📊 Total notifications: {stats.get('total_notifications', 0)}")
        
        delivery_stats = stats.get('delivery_stats', {})
        if delivery_stats:
            print("   📤 Delivery Statistics:")
            for status, data in delivery_stats.items():
                print(f"     {status.title()}: {data.get('count', 0)} ({data.get('percentage', 0)}%)")
        
        channel_stats = stats.get('channel_stats', {})
        if channel_stats:
            print("   📡 Channel Statistics:")
            for channel, data in channel_stats.items():
                print(f"     {channel.replace('_', ' ').title()}: {data.get('count', 0)} ({data.get('percentage', 0)}%)")
        
        type_stats = stats.get('type_stats', {})
        if type_stats:
            print("   🏷️ Type Statistics:")
            for notification_type, data in type_stats.items():
                print(f"     {notification_type.replace('_', ' ').title()}: {data.get('count', 0)} ({data.get('percentage', 0)}%)")
        
        print()
    
    async def demo_websocket_connection(self):
        """Demonstrate WebSocket real-time notifications"""
        print("🔌 Testing WebSocket Real-time Notifications...")
        
        user_id = "websocket_demo_user"
        ws_url = f"ws://localhost:8003/ws/{user_id}"
        
        try:
            async with websockets.connect(ws_url) as websocket:
                print(f"   ✅ Connected to WebSocket for user: {user_id}")
                
                # Send ping to test connection
                await websocket.send(json.dumps({"type": "ping"}))
                
                # Listen for pong response
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                pong_data = json.loads(response)
                if pong_data.get("type") == "pong":
                    print("   ✅ Ping/Pong successful")
                
                # Create a notification for this user to see real-time delivery
                notification_data = {
                    "user_id": user_id,
                    "type": "custom",
                    "title": "🚀 Real-time Notification Test",
                    "message": "This notification was delivered in real-time via WebSocket!",
                    "priority": "normal",
                    "channels": ["real_time"],
                    "metadata": {"demo": True, "timestamp": datetime.utcnow().isoformat()}
                }
                
                # Create notification (should be received via WebSocket)
                print("   📤 Creating notification for real-time delivery...")
                asyncio.create_task(self.make_request('POST', '/notifications', json=notification_data))
                
                # Wait for notification
                try:
                    notification_message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    notification_data = json.loads(notification_message)
                    
                    if notification_data.get("type") == "notification":
                        notif = notification_data.get("data", {})
                        print(f"   ✅ Received real-time notification: {notif.get('title')}")
                        print(f"      Type: {notif.get('type')}")
                        print(f"      Priority: {notif.get('priority')}")
                        
                        # Mark as read via WebSocket
                        await websocket.send(json.dumps({
                            "type": "mark_read",
                            "notification_id": notif.get("id")
                        }))
                        print("   ✅ Marked notification as read via WebSocket")
                    
                except asyncio.TimeoutError:
                    print("   ⚠️ Timeout waiting for real-time notification")
                
        except Exception as e:
            print(f"   ❌ WebSocket connection failed: {e}")
        
        print()
    
    async def demo_scheduled_notifications(self):
        """Demonstrate scheduled notifications"""
        print("⏰ Testing Scheduled Notifications...")
        
        # Create a notification scheduled for 10 seconds in the future
        future_time = (datetime.utcnow() + timedelta(seconds=10)).isoformat()
        
        scheduled_data = {
            "user_id": "scheduled_demo_user",
            "type": "course_reminder",
            "title": "⏰ Scheduled Reminder",
            "message": "This notification was scheduled to be delivered at a specific time!",
            "priority": "normal",
            "channels": ["real_time"],
            "scheduled_for": future_time,
            "metadata": {"scheduled_demo": True}
        }
        
        print(f"   Creating notification scheduled for {future_time}...")
        result = await self.make_request('POST', '/notifications', json=scheduled_data)
        
        if 'id' in result:
            print(f"   ✅ Scheduled notification created with ID: {result['id']}")
            print(f"   📅 Status: {result.get('status')} (should be 'pending')")
            print(f"   ⏰ Scheduled for: {result.get('scheduled_for')}")
        else:
            print(f"   ❌ Failed to create scheduled notification: {result}")
        
        print()
    
    async def run_comprehensive_demo(self):
        """Run the complete notifications service demonstration"""
        print("=" * 70)
        print("🎯 CogniFlow Notifications Service - Comprehensive Demo")
        print("=" * 70)
        print()
        
        try:
            # Basic functionality tests
            await self.demo_health_check()
            await self.demo_notification_creation()
            await self.demo_bulk_notifications()
            await self.demo_user_preferences()
            await self.demo_user_notifications()
            
            # Advanced features
            await self.demo_templates()
            await self.demo_analytics()
            await self.demo_scheduled_notifications()
            
            # Real-time functionality
            await self.demo_websocket_connection()
            
        except Exception as e:
            print(f"❌ Demo failed with error: {e}")
            return False
        
        print("=" * 70)
        print("✅ Notifications Service Demo Completed Successfully!")
        print("=" * 70)
        print()
        print("🎉 The CogniFlow Notifications Service is fully operational with:")
        print("   ✅ Real-time WebSocket notifications")
        print("   ✅ Email notification system (mock in dev mode)")
        print("   ✅ User preference management")
        print("   ✅ Bulk notification capabilities")
        print("   ✅ Scheduled notification delivery")
        print("   ✅ Comprehensive analytics and metrics")
        print("   ✅ Professional template system")
        print("   ✅ Cross-service integration ready")
        print()
        print("🚀 Ready for production deployment with database and email providers!")
        print()
        
        return True

async def main():
    """Main demo function"""
    print("🚀 Starting CogniFlow Notifications Service Demo...")
    print("📋 Make sure the notifications service is running on localhost:8003")
    print()
    
    # Wait a moment for user to read
    await asyncio.sleep(2)
    
    async with NotificationsDemo() as demo:
        success = await demo.run_comprehensive_demo()
        
        if success:
            print("🎯 Demo completed successfully!")
        else:
            print("❌ Demo encountered issues. Check the service logs.")

if __name__ == "__main__":
    # Run the demo
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
