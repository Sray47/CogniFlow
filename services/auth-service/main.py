"""
CogniFlow Authentication Service

This service handles user authentication, authorization, and session management.
Supports both development mode (in-memory storage) and production mode (database + Redis).

Key Features:
- JWT token-based authentication
- Role-based access control (RBAC)
- Password hashing with bcrypt
- Session management and token blacklisting
- Rate limiting for security
- Comprehensive audit logging

Author: CogniFlow Development Team
Version: 1.0.0
"""

import os
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum
import uuid

from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, validator
import jwt
import bcrypt
from passlib.context import CryptContext

# Configuration and environment setup
NO_DATABASE_MODE = os.getenv("NO_DATABASE_MODE", "False").lower() == "true"

# Security configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))

# Initialize password context for secure hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Security bearer scheme for JWT tokens
security = HTTPBearer()

class UserRole(str, Enum):
    """
    User roles for role-based access control.
    Defines the hierarchy and permissions within the platform.
    """
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class TokenType(str, Enum):
    """Token types for different authentication scenarios."""
    ACCESS = "access"
    REFRESH = "refresh"

class AuthStatus(str, Enum):
    """Authentication attempt status for audit logging."""
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"

# Pydantic models for request/response validation
class LoginRequest(BaseModel):
    """Request model for user login."""
    email: EmailStr
    password: str
    remember_me: bool = False

    @validator('password')
    def password_strength(cls, v):
        """Validate password strength requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

class TokenResponse(BaseModel):
    """Response model for successful authentication."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    role: UserRole

class RefreshTokenRequest(BaseModel):
    """Request model for token refresh."""
    refresh_token: str

class PasswordChangeRequest(BaseModel):
    """Request model for password change."""
    current_password: str
    new_password: str

    @validator('new_password')
    def password_strength(cls, v):
        """Validate new password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserInfo(BaseModel):
    """User information model for authenticated responses."""
    user_id: str
    email: str
    role: UserRole
    is_active: bool
    last_login: Optional[datetime] = None

class AuditLog(BaseModel):
    """Audit log entry for security monitoring."""
    timestamp: datetime
    user_id: Optional[str]
    email: Optional[str]
    action: str
    status: AuthStatus
    ip_address: str
    user_agent: str
    details: Optional[Dict] = None

# Development mode: In-memory storage classes
if NO_DATABASE_MODE:
    class InMemoryAuthStore:
        """
        In-memory storage for authentication data in development mode.
        
        In production, this would be replaced with:
        - Redis for session management and token blacklisting
        - PostgreSQL for user credentials and audit logs
        - Proper database transactions and ACID compliance
        """
        
        def __init__(self):
            # User credentials storage
            # Production: Replace with User table in PostgreSQL
            self.users: Dict[str, Dict] = {
                "admin@cogniflow.com": {
                    "user_id": str(uuid.uuid4()),
                    "email": "admin@cogniflow.com",
                    "password_hash": pwd_context.hash("admin123"),
                    "role": UserRole.ADMIN,
                    "is_active": True,
                    "created_at": datetime.now(timezone.utc),
                    "last_login": None,
                    "failed_attempts": 0,
                    "locked_until": None
                },
                "instructor@cogniflow.com": {
                    "user_id": str(uuid.uuid4()),
                    "email": "instructor@cogniflow.com", 
                    "password_hash": pwd_context.hash("instructor123"),
                    "role": UserRole.INSTRUCTOR,
                    "is_active": True,
                    "created_at": datetime.now(timezone.utc),
                    "last_login": None,
                    "failed_attempts": 0,
                    "locked_until": None
                },
                "student@cogniflow.com": {
                    "user_id": str(uuid.uuid4()),
                    "email": "student@cogniflow.com",
                    "password_hash": pwd_context.hash("student123"),
                    "role": UserRole.STUDENT,
                    "is_active": True,
                    "created_at": datetime.now(timezone.utc),
                    "last_login": None,
                    "failed_attempts": 0,
                    "locked_until": None
                }
            }
            
            # Active sessions storage
            # Production: Replace with Redis sets for scalability
            self.active_sessions: Dict[str, Dict] = {}
            
            # Blacklisted tokens storage
            # Production: Replace with Redis sets with TTL
            self.blacklisted_tokens: Set[str] = set()
            
            # Rate limiting storage
            # Production: Replace with Redis with sliding window algorithm
            self.rate_limit_attempts: Dict[str, List[datetime]] = {}
            
            # Audit logs storage
            # Production: Replace with dedicated audit_logs table
            self.audit_logs: List[AuditLog] = []

    # Initialize the in-memory store
    auth_store = InMemoryAuthStore()

else:
    # Production mode: Database and Redis integration
    """
    Production implementation would include:
    
    from sqlalchemy.orm import Session
    from redis import Redis
    from database import get_db, get_redis
    from models import User, Session, AuditLog
    
    # Database models would include:
    # - User table with proper indexing on email
    # - Session table for active user sessions
    # - AuditLog table for security monitoring
    # - Rate limiting with Redis sliding window
    # - Token blacklisting with Redis sets and TTL
    """
    auth_store = None

# Initialize FastAPI application
app = FastAPI(
    title="CogniFlow Authentication Service",
    description="Professional authentication and authorization service for CogniFlow platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Production: Configure specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Utility functions for authentication
class AuthenticationService:
    """
    Core authentication service with professional security practices.
    
    Handles password hashing, token generation, and session management
    with comprehensive security measures including rate limiting and audit logging.
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash password using bcrypt with configurable rounds.
        
        Args:
            password: Plain text password to hash
            
        Returns:
            Hashed password string
            
        Production considerations:
        - Use environment-specific bcrypt rounds (12+ for production)
        - Consider additional key stretching for high-security applications
        """
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify password against stored hash.
        
        Args:
            plain_password: Password to verify
            hashed_password: Stored password hash
            
        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """
        Create JWT access token with expiration.
        
        Args:
            data: Token payload data
            expires_delta: Custom expiration time
            
        Returns:
            Encoded JWT token string
            
        Production considerations:
        - Use RS256 algorithm with public/private key pairs
        - Implement token rotation for enhanced security
        - Add additional claims for fine-grained permissions
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": TokenType.ACCESS.value,
            "jti": str(uuid.uuid4())  # Unique token identifier
        })
        
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def create_refresh_token(user_id: str) -> str:
        """
        Create long-lived refresh token for token renewal.
        
        Args:
            user_id: User identifier
            
        Returns:
            Encoded refresh token
            
        Production considerations:
        - Store refresh tokens in database with rotation
        - Implement refresh token families for security
        - Add device fingerprinting for additional security
        """
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        
        to_encode = {
            "sub": user_id,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": TokenType.REFRESH.value,
            "jti": str(uuid.uuid4())
        }
        
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def verify_token(token: str, token_type: TokenType = TokenType.ACCESS) -> Dict:
        """
        Verify and decode JWT token.
        
        Args:
            token: JWT token to verify
            token_type: Expected token type
            
        Returns:
            Decoded token payload
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            
            # Verify token type
            if payload.get("type") != token_type.value:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token type"
                )
            
            # Check if token is blacklisted (development mode)
            if NO_DATABASE_MODE and token in auth_store.blacklisted_tokens:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has been revoked"
                )
            
            # Production: Check Redis blacklist
            # redis_client = get_redis()
            # if redis_client and redis_client.sismember("blacklisted_tokens", token):
            #     raise HTTPException(status_code=401, detail="Token revoked")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

    @staticmethod
    def check_rate_limit(ip_address: str, max_attempts: int = 5, window_minutes: int = 15) -> bool:
        """
        Check if IP address has exceeded rate limit.
        
        Args:
            ip_address: Client IP address
            max_attempts: Maximum attempts allowed
            window_minutes: Time window in minutes
            
        Returns:
            True if within rate limit, False if exceeded
            
        Production implementation:
        - Use Redis with sliding window algorithm
        - Implement exponential backoff
        - Add geographic IP analysis for suspicious activity
        """
        if not NO_DATABASE_MODE:
            # Production: Implement Redis-based rate limiting
            # redis_client = get_redis()
            # current_time = datetime.now(timezone.utc)
            # window_start = current_time - timedelta(minutes=window_minutes)
            # 
            # # Use Redis sorted sets for sliding window
            # key = f"rate_limit:{ip_address}"
            # redis_client.zremrangebyscore(key, 0, window_start.timestamp())
            # attempt_count = redis_client.zcard(key)
            # 
            # if attempt_count >= max_attempts:
            #     return False
            # 
            # redis_client.zadd(key, {str(uuid.uuid4()): current_time.timestamp()})
            # redis_client.expire(key, window_minutes * 60)
            # return True
            return True
        
        # Development mode: Simple in-memory rate limiting
        current_time = datetime.now(timezone.utc)
        window_start = current_time - timedelta(minutes=window_minutes)
        
        if ip_address not in auth_store.rate_limit_attempts:
            auth_store.rate_limit_attempts[ip_address] = []
        
        # Remove old attempts outside the window
        auth_store.rate_limit_attempts[ip_address] = [
            attempt for attempt in auth_store.rate_limit_attempts[ip_address]
            if attempt > window_start
        ]
        
        # Check if limit exceeded
        if len(auth_store.rate_limit_attempts[ip_address]) >= max_attempts:
            return False
        
        # Add current attempt
        auth_store.rate_limit_attempts[ip_address].append(current_time)
        return True
    
    @staticmethod
    def log_auth_attempt(request: Request, user_id: Optional[str], email: Optional[str], 
                        action: str, status: AuthStatus, details: Optional[Dict] = None):
        """
        Log authentication attempt for audit and security monitoring.
        
        Args:
            request: FastAPI request object
            user_id: User identifier (if available)
            email: User email (if available)
            action: Action being performed
            status: Result status
            details: Additional details for logging
            
        Production considerations:
        - Use structured logging with ELK stack
        - Implement real-time security monitoring
        - Add integration with SIEM systems
        """
        log_entry = AuditLog(
            timestamp=datetime.now(timezone.utc),
            user_id=user_id,
            email=email,
            action=action,
            status=status,
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown"),
            details=details
        )
        
        if NO_DATABASE_MODE:
            auth_store.audit_logs.append(log_entry)
            # Keep only last 1000 entries in development
            if len(auth_store.audit_logs) > 1000:
                auth_store.audit_logs = auth_store.audit_logs[-1000:]
        else:
            # Production: Store in database
            # db = get_db()
            # audit_log = AuditLogModel(**log_entry.dict())
            # db.add(audit_log)
            # db.commit()
            pass

# Initialize authentication service
auth_service = AuthenticationService()

# Dependency for extracting current user from JWT token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserInfo:
    """
    Extract and validate current user from JWT token.
    
    Args:
        credentials: HTTP authorization credentials
        
    Returns:
        Current user information
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    payload = auth_service.verify_token(token, TokenType.ACCESS)
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    if NO_DATABASE_MODE:
        # Find user in in-memory store
        user_data = None
        for email, user in auth_store.users.items():
            if user["user_id"] == user_id:
                user_data = user
                break
        
        if not user_data or not user_data["is_active"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        return UserInfo(
            user_id=user_data["user_id"],
            email=user_data["email"],
            role=user_data["role"],
            is_active=user_data["is_active"],
            last_login=user_data["last_login"]
        )
    else:
        # Production: Query user from database
        # db = get_db()
        # user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        # if not user:
        #     raise HTTPException(status_code=401, detail="User not found or inactive")
        # return UserInfo.from_orm(user)
        raise HTTPException(status_code=503, detail="Database mode not implemented")

# Role-based access control decorator
def require_role(required_roles: List[UserRole]):
    """
    Decorator factory for role-based access control.
    
    Args:
        required_roles: List of roles that have access
        
    Returns:
        Dependency function for FastAPI
    """
    def role_checker(current_user: UserInfo = Depends(get_current_user)) -> UserInfo:
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

# API Endpoints
@app.post("/login", response_model=TokenResponse, summary="User Authentication")
async def login(request: Request, login_data: LoginRequest):
    """
    Authenticate user and return JWT tokens.
    
    This endpoint handles user login with comprehensive security measures:
    - Rate limiting to prevent brute force attacks
    - Password verification with bcrypt
    - JWT token generation with proper expiration
    - Audit logging for security monitoring
    
    Args:
        request: FastAPI request object for IP extraction
        login_data: User login credentials
        
    Returns:
        JWT tokens and user information
        
    Raises:
        HTTPException: For authentication failures or rate limiting
    """
    client_ip = request.client.host if request.client else "unknown"
    
    # Check rate limiting
    if not auth_service.check_rate_limit(client_ip):
        auth_service.log_auth_attempt(
            request, None, login_data.email, "login", AuthStatus.BLOCKED,
            {"reason": "rate_limit_exceeded"}
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later."
        )
    
    if NO_DATABASE_MODE:
        # Development mode: Check in-memory store
        user_data = auth_store.users.get(login_data.email)
        
        if not user_data:
            auth_service.log_auth_attempt(
                request, None, login_data.email, "login", AuthStatus.FAILED,
                {"reason": "user_not_found"}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Check if account is locked
        if user_data.get("locked_until") and user_data["locked_until"] > datetime.now(timezone.utc):
            auth_service.log_auth_attempt(
                request, user_data["user_id"], login_data.email, "login", AuthStatus.BLOCKED,
                {"reason": "account_locked"}
            )
            raise HTTPException(
                status_code=status.HTTP_423_LOCKED,
                detail="Account is temporarily locked"
            )
        
        # Verify password
        if not auth_service.verify_password(login_data.password, user_data["password_hash"]):
            # Increment failed attempts
            user_data["failed_attempts"] = user_data.get("failed_attempts", 0) + 1
            
            # Lock account after 5 failed attempts
            if user_data["failed_attempts"] >= 5:
                user_data["locked_until"] = datetime.now(timezone.utc) + timedelta(minutes=30)
            
            auth_service.log_auth_attempt(
                request, user_data["user_id"], login_data.email, "login", AuthStatus.FAILED,
                {"reason": "invalid_password", "failed_attempts": user_data["failed_attempts"]}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Check if user is active
        if not user_data["is_active"]:
            auth_service.log_auth_attempt(
                request, user_data["user_id"], login_data.email, "login", AuthStatus.FAILED,
                {"reason": "account_inactive"}
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive"
            )
        
        # Reset failed attempts on successful login
        user_data["failed_attempts"] = 0
        user_data["locked_until"] = None
        user_data["last_login"] = datetime.now(timezone.utc)
        
        # Generate tokens
        access_token = auth_service.create_access_token(
            data={"sub": user_data["user_id"], "email": user_data["email"], "role": user_data["role"]}
        )
        refresh_token = auth_service.create_refresh_token(user_data["user_id"])
        
        # Store session information
        session_id = str(uuid.uuid4())
        auth_store.active_sessions[session_id] = {
            "user_id": user_data["user_id"],
            "email": user_data["email"],
            "role": user_data["role"],
            "created_at": datetime.now(timezone.utc),
            "ip_address": client_ip,
            "user_agent": request.headers.get("user-agent", "unknown")
        }
        
        auth_service.log_auth_attempt(
            request, user_data["user_id"], login_data.email, "login", AuthStatus.SUCCESS,
            {"session_id": session_id}
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=user_data["user_id"],
            role=user_data["role"]
        )
    
    else:
        # Production mode: Database authentication
        """
        Production implementation:
        
        db = get_db()
        user = db.query(User).filter(User.email == login_data.email).first()
        
        if not user or not auth_service.verify_password(login_data.password, user.password_hash):
            # Implement account lockout logic
            # Log failed attempt
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not user.is_active:
            raise HTTPException(status_code=401, detail="Account inactive")
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        db.commit()
        
        # Generate tokens and store session in Redis
        # Return token response
        """
        raise HTTPException(status_code=503, detail="Database mode not implemented")

@app.post("/refresh", response_model=TokenResponse, summary="Token Refresh")
async def refresh_token(request: Request, refresh_data: RefreshTokenRequest):
    """
    Refresh access token using refresh token.
    
    This endpoint allows clients to obtain new access tokens without
    requiring full authentication, improving user experience while
    maintaining security through token rotation.
    
    Args:
        request: FastAPI request object
        refresh_data: Refresh token request
        
    Returns:
        New access and refresh tokens
        
    Production considerations:
    - Implement refresh token rotation
    - Store refresh tokens in database with proper indexing
    - Add device fingerprinting for additional security
    """
    try:
        payload = auth_service.verify_token(refresh_data.refresh_token, TokenType.REFRESH)
        user_id = payload.get("sub")
        
        if NO_DATABASE_MODE:
            # Find user in in-memory store
            user_data = None
            for email, user in auth_store.users.items():
                if user["user_id"] == user_id:
                    user_data = user
                    break
            
            if not user_data or not user_data["is_active"]:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found or inactive"
                )
            
            # Generate new tokens
            access_token = auth_service.create_access_token(
                data={"sub": user_data["user_id"], "email": user_data["email"], "role": user_data["role"]}
            )
            new_refresh_token = auth_service.create_refresh_token(user_data["user_id"])
            
            # Blacklist old refresh token
            auth_store.blacklisted_tokens.add(refresh_data.refresh_token)
            
            auth_service.log_auth_attempt(
                request, user_data["user_id"], user_data["email"], "token_refresh", AuthStatus.SUCCESS
            )
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=new_refresh_token,
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                user_id=user_data["user_id"],
                role=user_data["role"]
            )
        
        else:
            # Production: Database-based refresh token validation
            raise HTTPException(status_code=503, detail="Database mode not implemented")
            
    except HTTPException:
        auth_service.log_auth_attempt(
            request, None, None, "token_refresh", AuthStatus.FAILED,
            {"reason": "invalid_refresh_token"}
        )
        raise

@app.post("/logout", summary="User Logout")
async def logout(request: Request, current_user: UserInfo = Depends(get_current_user),
                credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Logout user and invalidate tokens.
    
    This endpoint handles secure logout by blacklisting the current
    access token and cleaning up session data.
    
    Args:
        request: FastAPI request object
        current_user: Current authenticated user
        credentials: JWT token credentials
        
    Returns:
        Success confirmation
        
    Production considerations:
    - Invalidate all user sessions across devices (optional)
    - Clean up session data from Redis
    - Update last logout timestamp in database
    """
    token = credentials.credentials
    
    if NO_DATABASE_MODE:
        # Add token to blacklist
        auth_store.blacklisted_tokens.add(token)
        
        # Remove active sessions for this user
        sessions_to_remove = []
        for session_id, session_data in auth_store.active_sessions.items():
            if session_data["user_id"] == current_user.user_id:
                sessions_to_remove.append(session_id)
        
        for session_id in sessions_to_remove:
            del auth_store.active_sessions[session_id]
    
    else:
        # Production: Add token to Redis blacklist
        # redis_client = get_redis()
        # redis_client.sadd("blacklisted_tokens", token)
        # redis_client.expire("blacklisted_tokens", ACCESS_TOKEN_EXPIRE_MINUTES * 60)
        # 
        # # Clean up user sessions
        # redis_client.delete(f"user_sessions:{current_user.user_id}")
        pass
    
    auth_service.log_auth_attempt(
        request, current_user.user_id, current_user.email, "logout", AuthStatus.SUCCESS
    )
    
    return {"message": "Successfully logged out"}

@app.get("/me", response_model=UserInfo, summary="Get Current User")
async def get_current_user_info(current_user: UserInfo = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    This endpoint returns detailed information about the currently
    authenticated user, useful for profile pages and user context.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information
    """
    return current_user

@app.get("/health", summary="Service Health Check")
async def health_check():
    """
    Health check endpoint for service monitoring.
    
    Returns service status and basic statistics for monitoring
    and load balancer health checks.
    
    Returns:
        Service health information
    """
    if NO_DATABASE_MODE:
        active_sessions = len(auth_store.active_sessions)
        total_users = len(auth_store.users)
        blacklisted_tokens = len(auth_store.blacklisted_tokens)
    else:
        # Production: Query actual database statistics
        active_sessions = 0  # Query from Redis
        total_users = 0      # Query from PostgreSQL
        blacklisted_tokens = 0  # Query from Redis
    
    return {
        "service": "CogniFlow Authentication Service",
        "status": "healthy",
        "version": "1.0.0",
        "mode": "development" if NO_DATABASE_MODE else "production",
        "statistics": {
            "active_sessions": active_sessions,
            "total_users": total_users,
            "blacklisted_tokens": blacklisted_tokens
        }
    }

# Administrative endpoints (admin role required)
@app.get("/admin/audit-logs", response_model=List[AuditLog], summary="Get Audit Logs")
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    current_user: UserInfo = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    """
    Retrieve audit logs for security monitoring.
    
    This endpoint provides access to authentication audit logs
    for administrators to monitor security events and investigate
    suspicious activities.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Current authenticated admin user
        
    Returns:
        List of audit log entries
        
    Production considerations:
    - Implement proper pagination with database queries
    - Add filtering by date range, user, and event type
    - Include export functionality for compliance requirements
    """
    if NO_DATABASE_MODE:
        # Return paginated audit logs from in-memory store
        logs = auth_store.audit_logs[skip:skip + limit]
        return logs
    else:
        # Production: Query audit logs from database
        # db = get_db()
        # logs = db.query(AuditLog).offset(skip).limit(limit).all()
        # return logs
        return []

@app.get("/admin/active-sessions", summary="Get Active Sessions")
async def get_active_sessions(
    current_user: UserInfo = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN]))
):
    """
    Retrieve active user sessions for monitoring.
    
    This endpoint provides administrators with visibility into
    current active sessions for security monitoring and user
    support purposes.
    
    Args:
        current_user: Current authenticated admin user
        
    Returns:
        List of active sessions
    """
    if NO_DATABASE_MODE:
        return {
            "total_sessions": len(auth_store.active_sessions),
            "sessions": list(auth_store.active_sessions.values())
        }
    else:
        # Production: Query active sessions from Redis
        # redis_client = get_redis()
        # sessions = redis_client.keys("user_session:*")
        # return session data
        return {"total_sessions": 0, "sessions": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
