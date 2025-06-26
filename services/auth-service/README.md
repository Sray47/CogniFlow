# CogniFlow Authentication Service

## Overview

The CogniFlow Authentication Service is a professional, production-ready authentication and authorization service built with FastAPI. It provides comprehensive security features including JWT token management, role-based access control, rate limiting, audit logging, and session management.

## Features

### Core Authentication
- **JWT Token Authentication**: Industry-standard JSON Web Tokens with configurable expiration
- **Password Security**: bcrypt hashing with configurable rounds for optimal security
- **Token Refresh**: Secure token refresh mechanism without requiring re-authentication
- **Multi-Role Support**: Student, Instructor, Admin, and Super Admin roles

### Security Features
- **Rate Limiting**: Configurable rate limiting to prevent brute force attacks
- **Account Lockout**: Automatic account lockout after failed login attempts
- **Token Blacklisting**: Secure token invalidation on logout
- **Session Management**: Track and manage active user sessions
- **Audit Logging**: Comprehensive logging of all authentication events

### Development & Production Modes
- **No-Database Mode**: In-memory storage for development and testing
- **Production Mode**: Full database integration with PostgreSQL and Redis
- **Professional Code Structure**: Clean, documented, and maintainable codebase

## API Endpoints

### Authentication Endpoints

#### POST /login
Authenticate user and return JWT tokens.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "userpassword",
  "remember_me": false
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "role": "student"
}
```

#### POST /refresh
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### POST /logout
Logout user and invalidate tokens.

**Headers:**
```
Authorization: Bearer <access_token>
```

#### GET /me
Get current authenticated user information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "user@example.com",
  "role": "student",
  "is_active": true,
  "last_login": "2025-06-18T13:30:00Z"
}
```

### Administrative Endpoints

#### GET /admin/audit-logs
Get authentication audit logs (Admin/Super Admin only).

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100)

#### GET /admin/active-sessions
Get active user sessions (Admin/Super Admin only).

### Health Check

#### GET /health
Service health check with statistics.

**Response:**
```json
{
  "service": "CogniFlow Authentication Service",
  "status": "healthy",
  "version": "1.0.0",
  "mode": "development",
  "statistics": {
    "active_sessions": 5,
    "total_users": 3,
    "blacklisted_tokens": 2
  }
}
```

## Configuration

The service uses environment variables for configuration. Key settings include:

### Security Configuration
- `JWT_SECRET_KEY`: Secret key for JWT token signing (min 32 characters)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Access token expiration (default: 30)
- `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token expiration (default: 7)
- `BCRYPT_ROUNDS`: Password hashing rounds (default: 12)

### Rate Limiting
- `RATE_LIMIT_ATTEMPTS`: Max login attempts (default: 5)
- `RATE_LIMIT_WINDOW_MINUTES`: Rate limit window (default: 15)

### Database Mode
- `NO_DATABASE_MODE`: Enable/disable database mode (default: true)
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string

## Default Users (Development Mode)

For development and testing, the service includes three default users:

1. **Admin User**
   - Email: `admin@cogniflow.com`
   - Password: `admin123`
   - Role: Admin

2. **Instructor User**
   - Email: `instructor@cogniflow.com`
   - Password: `instructor123`
   - Role: Instructor

3. **Student User**
   - Email: `student@cogniflow.com`
   - Password: `student123`
   - Role: Student

## Security Features

### Password Requirements
- Minimum 8 characters
- At least one uppercase letter (configurable)
- At least one lowercase letter (configurable)
- At least one digit (configurable)
- Special characters (optional, configurable)

### Rate Limiting
- Maximum 5 login attempts per IP within 15 minutes
- Account lockout after 5 failed attempts for 30 minutes
- Sliding window algorithm for fair usage

### Token Security
- JWT tokens with configurable expiration
- Refresh token rotation on use
- Token blacklisting on logout
- Unique token identifiers (JTI) for tracking

### Audit Logging
All authentication events are logged with:
- Timestamp and user information
- IP address and user agent
- Action type and result status
- Additional context and details

## Development Setup

### Prerequisites
- Python 3.11+
- Docker and Docker Compose (recommended)

### Local Development
1. Navigate to the auth service directory:
   ```bash
   cd services/auth-service
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set environment variables:
   ```bash
   export NO_DATABASE_MODE=true
   export JWT_SECRET_KEY=your-development-secret-key-min-32-chars
   ```

4. Run the service:
   ```bash
   uvicorn main:app --reload --port 8003
   ```

### Docker Development
Use the no-database docker-compose configuration:
```bash
docker-compose -f docker-compose.no-db.yml up auth-service
```

## Production Deployment

### Environment Configuration
For production deployment, configure the following environment variables:

```bash
# Environment
export ENVIRONMENT=production
export DEBUG=false

# Security
export JWT_SECRET_KEY=$(openssl rand -base64 32)
export ACCESS_TOKEN_EXPIRE_MINUTES=15
export REFRESH_TOKEN_EXPIRE_DAYS=30
export BCRYPT_ROUNDS=14

# Database
export NO_DATABASE_MODE=false
export DATABASE_URL=postgresql://user:password@localhost:5432/cogniflow
export REDIS_URL=redis://localhost:6379/0

# CORS
export CORS_ORIGINS='["https://cogniflow.com","https://app.cogniflow.com"]'

# Rate Limiting
export RATE_LIMIT_ATTEMPTS=3
export RATE_LIMIT_WINDOW_MINUTES=5

# Security Features
export ENABLE_SECURITY_HEADERS=true
export ENABLE_RATE_LIMITING=true
export ENABLE_AUDIT_LOGGING=true
```

### Production Database Schema
When deploying in production mode, ensure the following database tables exist:

1. **users** - User account information
2. **user_sessions** - Active user sessions
3. **audit_logs** - Authentication audit trail
4. **blacklisted_tokens** - Invalidated JWT tokens

### Redis Configuration
Redis is used in production for:
- Session management and storage
- Token blacklisting with TTL
- Rate limiting with sliding windows
- Caching frequently accessed data

## Testing

Run the comprehensive test suite:

```bash
cd services/auth-service
python -m pytest test_auth.py -v
```

Test categories include:
- Authentication flow testing
- Token validation and refresh
- Role-based access control
- Rate limiting and security
- Audit logging verification
- Error handling scenarios

## API Documentation

When the service is running, access the interactive API documentation:
- **Swagger UI**: http://localhost:8003/docs
- **ReDoc**: http://localhost:8003/redoc

## Integration with Other Services

### API Gateway Integration
The authentication service integrates with the API Gateway at `/api/auth/*` routes.

### Frontend Integration
Frontend applications should:
1. Store JWT tokens securely (httpOnly cookies recommended)
2. Include Authorization header: `Bearer <access_token>`
3. Implement token refresh logic
4. Handle authentication errors gracefully

### Other Microservices
Other services can validate JWT tokens by:
1. Verifying token signature with shared secret
2. Checking token expiration
3. Validating user permissions for specific actions
4. Checking token blacklist (in production)

## Monitoring and Observability

### Health Checks
The `/health` endpoint provides service status and statistics for:
- Load balancer health checks
- Container orchestration platforms
- Monitoring systems

### Audit Logs
Authentication events are logged for:
- Security monitoring and compliance
- User behavior analysis
- Incident investigation
- Performance monitoring

### Metrics (Production)
Production deployments should include:
- Authentication success/failure rates
- Token refresh frequency
- Rate limiting triggers
- Session duration statistics

## Security Considerations

### Production Security Checklist
- [ ] Use strong, unique JWT secret key
- [ ] Configure appropriate token expiration times
- [ ] Restrict CORS origins to specific domains
- [ ] Enable all security headers
- [ ] Use HTTPS for all communications
- [ ] Implement proper secret management
- [ ] Set up security monitoring and alerting
- [ ] Regular security audits and penetration testing

### Compliance Considerations
The authentication service supports:
- GDPR compliance through audit logging
- SOC 2 compliance through access controls
- HIPAA compliance through encryption and audit trails
- Industry standard security practices

## Troubleshooting

### Common Issues

1. **Token validation errors**
   - Check JWT secret key configuration
   - Verify token expiration settings
   - Ensure clock synchronization between services

2. **Rate limiting issues**
   - Adjust rate limiting parameters
   - Check client IP detection
   - Review proxy configurations

3. **Database connection errors**
   - Verify database URL and credentials
   - Check network connectivity
   - Review connection pool settings

### Debug Mode
Enable debug mode for development:
```bash
export DEBUG=true
export LOG_LEVEL=DEBUG
```

## Contributing

When contributing to the authentication service:

1. Follow the established code structure and patterns
2. Add comprehensive tests for new features
3. Update documentation for API changes
4. Ensure production-ready code with proper error handling
5. Include security considerations in all changes

## License

This authentication service is part of the CogniFlow platform and follows the project's MIT license terms.
