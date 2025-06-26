# 🔐 CogniFlow Authentication Service

A comprehensive, enterprise-grade authentication and authorization service for the CogniFlow learning platform. This service provides secure JWT-based authentication, role-based access control (RBAC), session management, and comprehensive security auditing.

## 🚀 Features

### Core Authentication
- **JWT Token Authentication**: Secure access and refresh token implementation
- **Password Security**: bcrypt hashing with configurable rounds
- **Rate Limiting**: IP-based brute force protection
- **Account Lockout**: Automatic lockout after failed attempts
- **Session Management**: Comprehensive session tracking and management

### Authorization & Access Control
- **Role-Based Access Control (RBAC)**: Student, Instructor, Admin, Super Admin roles
- **Hierarchical Permissions**: Role-based permission inheritance
- **Protected Endpoints**: Secure route protection with middleware
- **Cross-Service Authentication**: Token validation for other microservices

### Security & Monitoring
- **Comprehensive Audit Logging**: All authentication events tracked
- **Security Event Classification**: Risk-level assessment for events
- **IP Tracking**: Client IP monitoring and suspicious activity detection
- **User Agent Analysis**: Device and browser tracking
- **Token Blacklisting**: Secure token invalidation on logout

### Development & Production Modes
- **No-Database Mode**: In-memory storage for rapid development
- **Production Ready**: PostgreSQL and Redis integration (commented)
- **Environment Configuration**: Flexible configuration via environment variables
- **Health Checks**: Container orchestration health endpoints

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │◄──►│  Authentication │    │   Other         │
│                 │    │    Service      │◄──►│  Microservices  │
│   Port: 8000    │    │   Port: 8005    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                    ┌─────────────────┐    ┌─────────────────┐
                    │   PostgreSQL    │    │      Redis      │
                    │  (Production)   │    │   (Sessions)    │
                    │   Port: 5432    │    │   Port: 6379    │
                    └─────────────────┘    └─────────────────┘
```

## 📊 API Endpoints

### Public Endpoints
- `POST /login` - User authentication with email/password
- `POST /refresh` - Refresh access tokens using refresh token
- `GET /health` - Service health check

### Protected Endpoints
- `POST /logout` - Logout and invalidate session (requires auth)
- `GET /me` - Get current user profile (requires auth)
- `PUT /change-password` - Change user password (requires auth)

### Admin Endpoints
- `GET /admin/audit-logs` - Retrieve security audit logs (admin only)
- `GET /admin/active-sessions` - View active user sessions (admin only)

## 🔧 Configuration

### Environment Variables

```bash
# Security Configuration
NO_DATABASE_MODE=true                    # Development mode toggle
JWT_SECRET_KEY=your-secret-key-here     # JWT signing key (REQUIRED)
ACCESS_TOKEN_EXPIRE_MINUTES=30          # Access token expiration
REFRESH_TOKEN_EXPIRE_DAYS=7             # Refresh token expiration

# Rate Limiting & Security
MAX_LOGIN_ATTEMPTS=5                    # Max failed login attempts
LOCKOUT_DURATION_MINUTES=15            # Account lockout duration

# Production Database (when NO_DATABASE_MODE=false)
DATABASE_URL=postgresql://user:pass@host:port/db
REDIS_URL=redis://host:port/db
```

### Sample Users (Development Mode)

For testing in development mode, the service creates these sample users:

```bash
# Admin User
Email: admin@cogniflow.com
Password: admin123
Role: admin

# Instructor User  
Email: instructor@cogniflow.com
Password: instructor123
Role: instructor

# Student User
Email: student@cogniflow.com
Password: student123
Role: student
```

## 🚀 Quick Start

### Development Mode (No Database)

```bash
# Set environment variables
export NO_DATABASE_MODE=true
export JWT_SECRET_KEY=dev-secret-key

# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn main:app --reload --port 8005
```

### Docker Development

```bash
# Build and run with docker-compose
docker-compose -f docker-compose.no-db.yml up authentication-service
```

### Production Mode

```bash
# Set production environment variables
export NO_DATABASE_MODE=false
export DATABASE_URL=postgresql://user:pass@host:port/cogniflow
export REDIS_URL=redis://host:port/2
export JWT_SECRET_KEY=your-production-secret-key

# Run with production settings
uvicorn main:app --host 0.0.0.0 --port 8005
```

## 🔐 Security Features

### Password Security
- **bcrypt Hashing**: Industry-standard password hashing
- **Salt Generation**: Unique salt for each password
- **Configurable Rounds**: Adjustable computational cost

### JWT Token Security
- **HS256 Algorithm**: Secure HMAC-based signing
- **Token Rotation**: Refresh token mechanism
- **Token Blacklisting**: Secure logout implementation
- **Expiration Management**: Configurable token lifetimes

### Rate Limiting
- **IP-Based Limiting**: Per-IP address attempt tracking
- **Sliding Window**: Time-based attempt counting
- **Automatic Lockout**: Account protection after max attempts

### Audit Logging
- **Comprehensive Events**: All auth events logged
- **Risk Assessment**: Event risk level classification
- **IP Tracking**: Client IP address logging
- **User Agent Analysis**: Browser/device identification

## 🧪 Testing

### Manual Testing

```bash
# Test login
curl -X POST http://localhost:8005/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@cogniflow.com",
    "password": "student123"
  }'

# Test protected endpoint
curl -X GET http://localhost:8005/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Test logout
curl -X POST http://localhost:8005/logout \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Integration with Other Services

```python
# Example: Verify JWT token in other microservices
import jwt
import requests

def verify_auth_token(token: str):
    try:
        payload = jwt.decode(
            token, 
            JWT_SECRET_KEY, 
            algorithms=["HS256"]
        )
        return payload.get("user_id"), payload.get("role")
    except jwt.InvalidTokenError:
        return None, None

# Or use the authentication service directly
def validate_user(token: str):
    response = requests.get(
        "http://authentication-service:8005/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    return response.json() if response.status_code == 200 else None
```

## 📈 Monitoring & Analytics

### Health Monitoring
- **Health Check Endpoint**: `/health` for container orchestration
- **Service Status**: Real-time service status reporting
- **Performance Metrics**: Response time and throughput tracking

### Security Monitoring
- **Failed Login Tracking**: Brute force attempt detection
- **Suspicious Activity**: Anomaly detection and alerting
- **Audit Log Analysis**: Security event pattern analysis

### Session Analytics
- **Active Session Tracking**: Real-time session monitoring
- **Session Duration Analysis**: User engagement metrics
- **Device/Browser Analytics**: Client platform statistics

## 🚀 Production Deployment

### Database Setup

```sql
-- PostgreSQL tables (auto-created in production mode)
-- Users table with security fields
-- User sessions with device tracking
-- Audit logs with event classification
-- Blacklisted tokens for secure logout
```

### Redis Configuration

```bash
# Redis databases for different purposes
# Database 2: Authentication sessions
# Database 3: Rate limiting data
# Database 4: Blacklisted tokens
```

### Environment Security

```bash
# Use strong JWT secret keys in production
JWT_SECRET_KEY=$(openssl rand -base64 64)

# Configure appropriate token expiration
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# Set up proper database connections
DATABASE_URL=postgresql://auth_user:strong_password@db:5432/cogniflow
REDIS_URL=redis://redis:6379/2
```

## 🔧 Development Notes

### Adding New Roles
1. Update `UserRole` enum in `main.py`
2. Modify role hierarchy in `require_role()` function
3. Update sample users in startup event
4. Test role-based access control

### Extending Authentication
1. Add new endpoints following existing patterns
2. Use `get_current_user()` dependency for protection
3. Use `require_role()` for role-based access
4. Always log security events with `log_security_event()`

### Security Considerations
- Never log passwords or tokens in plaintext
- Always use HTTPS in production
- Regularly rotate JWT secret keys
- Monitor audit logs for suspicious patterns
- Implement proper CORS policies

## 📚 API Documentation

When running the service, visit:
- **Interactive Docs**: http://localhost:8005/docs
- **OpenAPI Schema**: http://localhost:8005/openapi.json
- **ReDoc**: http://localhost:8005/redoc

---

*Part of the CogniFlow Learning Platform - Professional, Scalable, Secure*
