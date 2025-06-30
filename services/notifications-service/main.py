"""
CogniFlow Notifications Service
=================================

A comprehensive notifications service providing:
- Real-time notifications via WebSockets
- Email notifications with templates
- Push notifications (web/mobile)
- Reminder systems for courses and deadlines
- User notification preferences
- Delivery tracking and analytics

Development Mode: Uses in-memory storage for rapid prototyping
Production Mode: Redis queues, PostgreSQL, email services (commented)

Author: CogniFlow Development Team
"""

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import List, Dict, Optional, Any, Set
from datetime import datetime, timedelta
from enum import Enum
import json
import os
import asyncio
import uuid
import logging
from dataclasses import dataclass, asdict, field
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Production imports (commented for no-db mode)
# from sqlalchemy import create_engine, Column, String, DateTime, Boolean, Text, Integer, ForeignKey
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy.orm import sessionmaker, Session, relationship
# from redis import Redis
# import celery
# from jinja2 import Template

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CogniFlow Notifications Service",
    description="Professional notifications service with real-time delivery, email, and reminder systems",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment configuration
NO_DATABASE_MODE = os.getenv('NO_DATABASE_MODE', 'true').lower() == 'true'
EMAIL_ENABLED = os.getenv('EMAIL_ENABLED', 'false').lower() == 'true'
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')

# ============================================================================
# DATA MODELS
# ============================================================================

class NotificationType(str, Enum):
    SYSTEM = "system"
    COURSE = "course"
    ASSIGNMENT = "assignment"
    REMINDER = "reminder"
    ACHIEVEMENT = "achievement"
    MESSAGE = "message"
    CUSTOM = "custom"

class NotificationPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class DeliveryChannel(str, Enum):
    REAL_TIME = "real_time"
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"

class NotificationStatus(str, Enum):
    UNREAD = "unread"
    READ = "read"
    DELIVERED = "delivered"
    FAILED = "failed"

@dataclass
class Notification:
    id: str
    user_id: str
    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    channels: List[DeliveryChannel] = field(default_factory=lambda: [DeliveryChannel.REAL_TIME])
    status: NotificationStatus = NotificationStatus.UNREAD
    created_at: datetime = field(default_factory=datetime.utcnow)
    delivered_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UserPreferences:
    user_id: str
    enabled_channels: List[DeliveryChannel] = field(default_factory=lambda: [DeliveryChannel.REAL_TIME, DeliveryChannel.EMAIL])
    quiet_hours: Optional[Dict[str, str]] = None
    mute_types: List[NotificationType] = field(default_factory=list)
    last_updated: datetime = field(default_factory=datetime.utcnow)

@dataclass
class NotificationTemplate:
    id: str
    name: str
    subject: str
    body: str
    type: NotificationType
    created_at: datetime = field(default_factory=datetime.utcnow)

# Pydantic models for API
class NotificationCreate(BaseModel):
    user_id: str
    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    channels: List[DeliveryChannel] = [DeliveryChannel.REAL_TIME]
    metadata: Optional[Dict[str, Any]] = None

class NotificationResponse(BaseModel):
    id: str
    user_id: str
    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority
    channels: List[DeliveryChannel]
    status: NotificationStatus
    created_at: datetime
    delivered_at: Optional[datetime]
    read_at: Optional[datetime]
    metadata: Optional[Dict[str, Any]]

class PreferencesUpdate(BaseModel):
    enabled_channels: Optional[List[DeliveryChannel]] = None
    quiet_hours: Optional[Dict[str, str]] = None
    mute_types: Optional[List[NotificationType]] = None

class BulkNotificationCreate(BaseModel):
    user_ids: List[str]
    type: NotificationType
    title: str
    message: str
    priority: NotificationPriority = NotificationPriority.NORMAL
    channels: List[DeliveryChannel] = [DeliveryChannel.REAL_TIME]
    metadata: Optional[Dict[str, Any]] = None

# ============================================================================
# IN-MEMORY STORAGE (Development Mode)
# ============================================================================

# --- In-Memory Notification Store (Dev Mode) ---
if NO_DATABASE_MODE:
    class InMemoryNotificationStore:
        """
        In-memory notification, preferences, and template store for development mode.
        Production implementation would use PostgreSQL for persistence and Redis for pub/sub and delivery queues.
        """
        def __init__(self):
            self.notifications = []
            self.preferences = {}
            self.templates = []
            self._init_sample_data()

        def _init_sample_data(self):
            # Optionally add sample notification templates or preferences
            pass

        def add_notification(self, notif):
            self.notifications.append(notif)

        def get_user_notifications(self, user_id, limit=50, unread_only=False):
            notifs = [n for n in self.notifications if n.user_id == user_id]
            if unread_only:
                notifs = [n for n in notifs if n.status == NotificationStatus.UNREAD]
            return notifs[:limit]

        def mark_as_read(self, notification_id, user_id):
            for n in self.notifications:
                if n.id == notification_id and n.user_id == user_id:
                    n.status = NotificationStatus.READ
                    return True
            return False

        def get_preferences(self, user_id):
            return self.preferences.get(user_id)

        def update_preferences(self, user_id, update):
            prefs = self.preferences.setdefault(user_id, UserPreferences())
            # Update logic here
            return prefs

        def get_templates(self):
            return self.templates

    notification_store = InMemoryNotificationStore()
else:
    # --- Production-ready code (PostgreSQL/Redis) ---
    # class ProductionNotificationStore:
    #     """
    #     Production-ready notification store using PostgreSQL and Redis.
    #     - Use SQLAlchemy ORM for notification/preferences/template models
    #     - Use Redis for pub/sub and delivery queues
    #     - Implement proper transactional logic and error handling
    #     """
    #     def __init__(self, db: Session, redis_client):
    #         self.db = db
    #         self.redis = redis_client
    #     ...
    # notification_store = ProductionNotificationStore(...)
    pass

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.get("/health", summary="Service Health Check")
def health_check():
    """Health check endpoint for container orchestration and monitoring."""
    return {
        "status": "healthy",
        "service": "notifications-service",
        "mode": "development" if NO_DATABASE_MODE else "production",
        "email_enabled": EMAIL_ENABLED,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/notifications", response_model=NotificationResponse, summary="Create Notification")
def create_notification(data: NotificationCreate):
    """Create a new notification for a user. In dev mode, stores in memory. In prod, persists to DB/queue."""
    notif = Notification(
        id=str(uuid.uuid4()),
        user_id=data.user_id,
        type=data.type,
        title=data.title,
        message=data.message,
        priority=data.priority,
        channels=data.channels,
        metadata=data.metadata or {}
    )
    notification_store.add_notification(notif)
    logger.info(f"Notification created for user {notif.user_id}: {notif.title}")
    # TODO: Deliver via real-time/email/push as needed
    return NotificationResponse(**asdict(notif))

@app.post("/notifications/bulk", summary="Create Bulk Notifications")
def create_bulk_notifications(data: BulkNotificationCreate):
    """Create notifications for multiple users in bulk."""
    created = []
    for user_id in data.user_ids:
        notif = Notification(
            id=str(uuid.uuid4()),
            user_id=user_id,
            type=data.type,
            title=data.title,
            message=data.message,
            priority=data.priority,
            channels=data.channels,
            metadata=data.metadata or {}
        )
        notification_store.add_notification(notif)
        created.append(NotificationResponse(**asdict(notif)))
    logger.info(f"Bulk notifications created for users: {data.user_ids}")
    return {"created": created, "count": len(created)}

@app.get("/notifications/user/{user_id}", response_model=List[NotificationResponse], summary="Get User Notifications")
def get_user_notifications(user_id: str, limit: int = 50, unread_only: bool = False):
    """Get notifications for a user, optionally filtering for unread only."""
    notifs = notification_store.get_user_notifications(user_id, limit, unread_only)
    return [NotificationResponse(**asdict(n)) for n in notifs]

@app.put("/notifications/{notification_id}/read", summary="Mark Notification as Read")
def mark_notification_as_read(notification_id: str, user_id: str):
    """Mark a notification as read for a user."""
    if notification_store.mark_as_read(notification_id, user_id):
        logger.info(f"Notification {notification_id} marked as read by user {user_id}")
        return {"status": "success"}
    raise HTTPException(status_code=404, detail="Notification not found or not owned by user")

@app.get("/preferences/{user_id}", response_model=UserPreferences, summary="Get Notification Preferences")
def get_preferences(user_id: str):
    """Get notification preferences for a user."""
    return notification_store.get_preferences(user_id)

@app.put("/preferences/{user_id}", response_model=UserPreferences, summary="Update Notification Preferences")
def update_preferences(user_id: str, update: PreferencesUpdate):
    """Update notification preferences for a user."""
    return notification_store.update_preferences(user_id, update)

@app.get("/templates", response_model=List[NotificationTemplate], summary="Get Notification Templates")
def get_templates():
    """List all available notification templates."""
    return notification_store.get_templates()

@app.get("/analytics/delivery-stats", summary="Get Delivery Analytics")
def get_delivery_stats():
    """Get analytics on notification delivery and read status."""
    total = len(notification_store.notifications)
    delivered = sum(1 for n in notification_store.notifications.values() if n.status == NotificationStatus.DELIVERED)
    read = sum(1 for n in notification_store.notifications.values() if n.status == NotificationStatus.READ)
    unread = sum(1 for n in notification_store.notifications.values() if n.status == NotificationStatus.UNREAD)
    # Expand: add per-type, per-channel stats
    per_type = {}
    for n in notification_store.notifications.values():
        per_type.setdefault(n.type, {"total": 0, "read": 0, "delivered": 0, "unread": 0})
        per_type[n.type]["total"] += 1
        if n.status == NotificationStatus.READ:
            per_type[n.type]["read"] += 1
        if n.status == NotificationStatus.DELIVERED:
            per_type[n.type]["delivered"] += 1
        if n.status == NotificationStatus.UNREAD:
            per_type[n.type]["unread"] += 1
    return {
        "total": total,
        "delivered": delivered,
        "read": read,
        "unread": unread,
        "per_type": per_type
    }

# ============================================================================
# REAL-TIME NOTIFICATIONS (WebSocket)
# ============================================================================
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.setdefault(user_id, set()).add(websocket)
        logger.info(f"WebSocket connected for user {user_id}")

    def disconnect(self, user_id: str, websocket: WebSocket):
        conns = self.active_connections.get(user_id, set())
        if websocket in conns:
            conns.remove(websocket)
            logger.info(f"WebSocket disconnected for user {user_id}")

    async def send_personal_message(self, user_id: str, message: dict):
        for ws in self.active_connections.get(user_id, set()):
            await ws.send_json(message)

connection_manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await connection_manager.connect(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # Example: mark notification as read via WebSocket
            if data.get("action") == "mark_read":
                notif_id = data.get("notification_id")
                if notif_id and notification_store.mark_as_read(notif_id, user_id):
                    await websocket.send_json({"status": "read", "notification_id": notif_id})
    except WebSocketDisconnect:
        connection_manager.disconnect(user_id, websocket)

# ============================================================================
# EMAIL DELIVERY (Development: print, Production: SMTP)
# ============================================================================
def send_email_notification(user_email: str, subject: str, body: str):
    if not EMAIL_ENABLED:
        print(f"[DEV EMAIL] To: {user_email}\nSubject: {subject}\n{body}")
        return True
    # Production: Use SMTP (commented)
    """
    import smtplib
    from email.mime.text import MIMEText
    msg = MIMEText(body, 'html')
    msg['Subject'] = subject
    msg['From'] = SMTP_USERNAME
    msg['To'] = user_email
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, [user_email], msg.as_string())
    """
    return True

# ============================================================================
# BACKGROUND TASKS & SCHEDULED NOTIFICATIONS
# ============================================================================

async def process_scheduled_notifications():
    """Background task to process scheduled notifications (stub for dev, prod-ready in comments)."""
    while True:
        try:
            current_time = datetime.utcnow()
            for notification in notification_store.notifications.values():
                # Example: check for scheduled delivery (extend Notification if needed)
                if hasattr(notification, 'scheduled_for') and notification.status == NotificationStatus.UNREAD:
                    if notification.scheduled_for and notification.scheduled_for <= current_time:
                        # Dev: mark as delivered
                        notification.status = NotificationStatus.DELIVERED
                        notification.delivered_at = current_time
                        print(f"[DEV SCHEDULED DELIVERY] Notification {notification.id} delivered to {notification.user_id}")
                        # Production: deliver via async queue (uncomment and implement)
                        # await deliver_notification(notification)
            await asyncio.sleep(60)  # Check every minute
        except Exception as e:
            logger.error(f"Error processing scheduled notifications: {str(e)}")
            await asyncio.sleep(60)

# Start background task
@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    logger.info("Starting CogniFlow Notifications Service")
    logger.info(f"Mode: {'No-Database' if NO_DATABASE_MODE else 'Database'}")
    logger.info(f"Email: {'Enabled' if EMAIL_ENABLED else 'Disabled'}")
    
    # Start background task for scheduled notifications
    asyncio.create_task(process_scheduled_notifications())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)

# Push notification stub (future)
def send_push_notification(user_id: str, title: str, message: str):
    """Stub for push notification delivery (web/mobile)."""
    # Production: Integrate with FCM/APNs or web push
    print(f"[DEV PUSH] To: {user_id} | {title}: {message}")
    # Uncomment and implement for production
    # pass
    return True

# Reminder/scheduled notification stub (future)
def schedule_reminder_notification(user_id: str, title: str, message: str, when: datetime):
    """Stub for scheduling a reminder notification."""
    print(f"[DEV REMINDER] To: {user_id} at {when} | {title}: {message}")
    # Production: Store in DB/queue and deliver at 'when'
    # pass
    return True
