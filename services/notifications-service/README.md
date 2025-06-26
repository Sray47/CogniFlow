# CogniFlow Notifications Service

A professional, production-ready notifications microservice for real-time, email, and push notifications, supporting both in-memory (no-db) and production (database/queue) modes.

## Features
- Real-time notifications via WebSocket
- Email notifications (template-based)
- Push notification stubs (future mobile/web)
- Reminder and scheduled notifications
- User notification preferences (channels, quiet hours, mute types)
- Delivery tracking and analytics
- Bulk notification support
- In-memory mode for development, production-ready code (commented)

## API Endpoints
- `POST /notifications` – Create notification
- `POST /notifications/bulk` – Bulk notifications
- `GET /notifications/user/{user_id}` – Get user notifications
- `PUT /notifications/{id}/read` – Mark as read
- `GET /preferences/{user_id}` – Get preferences
- `PUT /preferences/{user_id}` – Update preferences
- `GET /templates` – List templates
- `GET /analytics/delivery-stats` – Delivery analytics
- `WS /ws/{user_id}` – Real-time WebSocket

## Development Mode
- In-memory store for notifications, preferences, templates
- Print emails to console
- All delivery and analytics in Python data structures

## Production Mode (Commented)
- SQLAlchemy models for notifications, preferences, templates
- Redis/Celery for async delivery
- SMTP for real email
- Jinja2 for templating

## Usage
- See `/docs` for full OpenAPI documentation
- WebSocket endpoint: `/ws/{user_id}`
- Email delivery: prints to console in dev, uses SMTP in prod

## Example Notification Payload
```json
{
  "user_id": "user-123",
  "type": "course",
  "title": "New Lesson Available!",
  "message": "Check out the new lesson in your course.",
  "priority": "normal",
  "channels": ["real_time", "email"]
}
```

## Extending
- Add new notification types or channels by extending enums and delivery logic
- For production, uncomment and configure SQLAlchemy/Redis/Celery/SMTP code

---
*Part of the CogniFlow platform. See main README for architecture and roadmap.*
