"""
Configuration Management for CogniFlow Authentication Service

This module provides centralized configuration management for the authentication
service, supporting both development and production environments with proper
validation and security considerations.

Features:
- Environment-based configuration
- Security parameter validation
- Database connection settings
- JWT token configuration
- Rate limiting parameters
- Audit logging configuration

Author: CogniFlow Development Team
Version: 1.0.0
"""

import os
from typing import Optional, List
from pydantic import BaseSettings, validator, Field
from enum import Enum

class Environment(str, Enum):
    """Supported deployment environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class LogLevel(str, Enum):
    """Supported logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class AuthenticationConfig(BaseSettings):
    """
    Authentication service configuration with validation.
    
    This class manages all configuration parameters for the authentication
    service, providing validation and type safety for critical security
    parameters.
    """
    
    # Environment configuration
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    debug: bool = Field(default=True)
    
    # Service configuration
    service_name: str = Field(default="CogniFlow Authentication Service")
    service_version: str = Field(default="1.0.0")
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8003, ge=1024, le=65535)
    
    # Database mode configuration
    no_database_mode: bool = Field(default=True)
    
    # JWT Token configuration
    jwt_secret_key: str = Field(min_length=32)
    jwt_algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30, ge=5, le=1440)
    refresh_token_expire_days: int = Field(default=7, ge=1, le=30)
    
    # Password security configuration
    bcrypt_rounds: int = Field(default=12, ge=10, le=16)
    password_min_length: int = Field(default=8, ge=8, le=128)
    password_require_uppercase: bool = Field(default=True)
    password_require_lowercase: bool = Field(default=True)
    password_require_digits: bool = Field(default=True)
    password_require_special: bool = Field(default=False)
    
    # Rate limiting configuration
    rate_limit_attempts: int = Field(default=5, ge=1, le=100)
    rate_limit_window_minutes: int = Field(default=15, ge=1, le=60)
    account_lockout_duration_minutes: int = Field(default=30, ge=5, le=1440)
    
    # Session management
    max_active_sessions_per_user: int = Field(default=5, ge=1, le=20)
    session_cleanup_interval_minutes: int = Field(default=60, ge=10, le=1440)
    
    # Database configuration (production mode)
    database_url: Optional[str] = Field(default=None)
    database_pool_size: int = Field(default=5, ge=1, le=20)
    database_max_overflow: int = Field(default=10, ge=0, le=50)
    database_pool_timeout: int = Field(default=30, ge=5, le=300)
    
    # Redis configuration (production mode)
    redis_url: Optional[str] = Field(default=None)
    redis_max_connections: int = Field(default=10, ge=1, le=100)
    redis_socket_timeout: int = Field(default=5, ge=1, le=30)
    
    # CORS configuration
    cors_origins: List[str] = Field(default=["http://localhost:3000"])
    cors_allow_credentials: bool = Field(default=True)
    
    # Logging configuration
    log_level: LogLevel = Field(default=LogLevel.INFO)
    log_format: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    audit_log_retention_days: int = Field(default=90, ge=1, le=365)
    
    # Security headers configuration
    enable_security_headers: bool = Field(default=True)
    enable_rate_limiting: bool = Field(default=True)
    enable_audit_logging: bool = Field(default=True)
    
    # Monitoring and health check configuration
    health_check_timeout: int = Field(default=5, ge=1, le=30)
    metrics_enabled: bool = Field(default=True)
    
    class Config:
        """Pydantic configuration for environment variable loading."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        # Environment variable mappings
        fields = {
            "environment": "ENVIRONMENT",
            "debug": "DEBUG",
            "service_name": "SERVICE_NAME",
            "service_version": "SERVICE_VERSION",
            "host": "HOST",
            "port": "PORT",
            "no_database_mode": "NO_DATABASE_MODE",
            "jwt_secret_key": "JWT_SECRET_KEY",
            "jwt_algorithm": "JWT_ALGORITHM",
            "access_token_expire_minutes": "ACCESS_TOKEN_EXPIRE_MINUTES",
            "refresh_token_expire_days": "REFRESH_TOKEN_EXPIRE_DAYS",
            "bcrypt_rounds": "BCRYPT_ROUNDS",
            "password_min_length": "PASSWORD_MIN_LENGTH",
            "password_require_uppercase": "PASSWORD_REQUIRE_UPPERCASE",
            "password_require_lowercase": "PASSWORD_REQUIRE_LOWERCASE",
            "password_require_digits": "PASSWORD_REQUIRE_DIGITS",
            "password_require_special": "PASSWORD_REQUIRE_SPECIAL",
            "rate_limit_attempts": "RATE_LIMIT_ATTEMPTS",
            "rate_limit_window_minutes": "RATE_LIMIT_WINDOW_MINUTES",
            "account_lockout_duration_minutes": "ACCOUNT_LOCKOUT_DURATION_MINUTES",
            "max_active_sessions_per_user": "MAX_ACTIVE_SESSIONS_PER_USER",
            "session_cleanup_interval_minutes": "SESSION_CLEANUP_INTERVAL_MINUTES",
            "database_url": "DATABASE_URL",
            "database_pool_size": "DATABASE_POOL_SIZE",
            "database_max_overflow": "DATABASE_MAX_OVERFLOW",
            "database_pool_timeout": "DATABASE_POOL_TIMEOUT",
            "redis_url": "REDIS_URL",
            "redis_max_connections": "REDIS_MAX_CONNECTIONS",
            "redis_socket_timeout": "REDIS_SOCKET_TIMEOUT",
            "cors_origins": "CORS_ORIGINS",
            "cors_allow_credentials": "CORS_ALLOW_CREDENTIALS",
            "log_level": "LOG_LEVEL",
            "log_format": "LOG_FORMAT",
            "audit_log_retention_days": "AUDIT_LOG_RETENTION_DAYS",
            "enable_security_headers": "ENABLE_SECURITY_HEADERS",
            "enable_rate_limiting": "ENABLE_RATE_LIMITING",
            "enable_audit_logging": "ENABLE_AUDIT_LOGGING",
            "health_check_timeout": "HEALTH_CHECK_TIMEOUT",
            "metrics_enabled": "METRICS_ENABLED"
        }
    
    @validator("jwt_secret_key")
    def validate_jwt_secret_key(cls, v, values):
        """
        Validate JWT secret key security requirements.
        
        In production, the secret key should be:
        - At least 32 characters long
        - Cryptographically random
        - Stored securely (environment variables, secrets manager)
        """
        if len(v) < 32:
            raise ValueError("JWT secret key must be at least 32 characters long")
        
        # In production, warn about default/weak keys
        if values.get("environment") == Environment.PRODUCTION:
            weak_keys = [
                "your-secret-key-change-in-production",
                "dev-secret-key-change-in-production",
                "default-secret-key",
                "secret-key"
            ]
            if v in weak_keys:
                raise ValueError("Production environment requires a strong, unique JWT secret key")
        
        return v
    
    @validator("cors_origins")
    def validate_cors_origins(cls, v, values):
        """
        Validate CORS origins configuration.
        
        In production, CORS origins should be restricted to specific domains
        rather than allowing all origins (*).
        """
        if values.get("environment") == Environment.PRODUCTION:
            if "*" in v or "http://localhost:3000" in v:
                raise ValueError(
                    "Production environment should not allow localhost or wildcard CORS origins"
                )
        return v
    
    @validator("database_url")
    def validate_database_url(cls, v, values):
        """
        Validate database URL for production mode.
        
        When not in no-database mode, a valid database URL is required
        for production environments.
        """
        no_db_mode = values.get("no_database_mode", True)
        environment = values.get("environment", Environment.DEVELOPMENT)
        
        if not no_db_mode and environment == Environment.PRODUCTION and not v:
            raise ValueError("Database URL is required for production mode")
        
        return v
    
    @validator("redis_url")
    def validate_redis_url(cls, v, values):
        """
        Validate Redis URL for production mode.
        
        When not in no-database mode, Redis URL is recommended
        for production environments for session management and caching.
        """
        no_db_mode = values.get("no_database_mode", True)
        environment = values.get("environment", Environment.PRODUCTION)
        
        if not no_db_mode and environment == Environment.PRODUCTION and not v:
            # Redis is recommended but not strictly required
            # Log a warning in actual implementation
            pass
        
        return v
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEVELOPMENT
    
    def get_database_config(self) -> dict:
        """
        Get database configuration dictionary.
        
        Returns database configuration suitable for SQLAlchemy
        engine creation in production mode.
        """
        if self.no_database_mode or not self.database_url:
            return {}
        
        return {
            "url": self.database_url,
            "pool_size": self.database_pool_size,
            "max_overflow": self.database_max_overflow,
            "pool_timeout": self.database_pool_timeout,
            "pool_pre_ping": True,  # Validate connections before use
            "echo": self.debug and not self.is_production()
        }
    
    def get_redis_config(self) -> dict:
        """
        Get Redis configuration dictionary.
        
        Returns Redis configuration suitable for redis-py
        client creation in production mode.
        """
        if self.no_database_mode or not self.redis_url:
            return {}
        
        return {
            "url": self.redis_url,
            "max_connections": self.redis_max_connections,
            "socket_timeout": self.redis_socket_timeout,
            "socket_connect_timeout": self.redis_socket_timeout,
            "retry_on_timeout": True,
            "decode_responses": True
        }
    
    def get_cors_config(self) -> dict:
        """
        Get CORS configuration dictionary.
        
        Returns CORS configuration suitable for FastAPI
        CORSMiddleware configuration.
        """
        return {
            "allow_origins": self.cors_origins,
            "allow_credentials": self.cors_allow_credentials,
            "allow_methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["*"]
        }

# Create global configuration instance
def get_config() -> AuthenticationConfig:
    """
    Get the global configuration instance.
    
    This function creates and returns a singleton configuration instance
    that can be used throughout the application.
    
    Returns:
        AuthenticationConfig: The global configuration instance
    """
    return AuthenticationConfig()

# For backwards compatibility and easier imports
config = get_config()

# Example usage in production deployment:
"""
Production environment variables example:

export ENVIRONMENT=production
export DEBUG=false
export JWT_SECRET_KEY=$(openssl rand -base64 32)
export ACCESS_TOKEN_EXPIRE_MINUTES=15
export REFRESH_TOKEN_EXPIRE_DAYS=30
export BCRYPT_ROUNDS=14
export NO_DATABASE_MODE=false
export DATABASE_URL=postgresql://user:password@localhost:5432/cogniflow
export REDIS_URL=redis://localhost:6379/0
export CORS_ORIGINS=["https://cogniflow.com","https://app.cogniflow.com"]
export RATE_LIMIT_ATTEMPTS=3
export RATE_LIMIT_WINDOW_MINUTES=5
export ENABLE_SECURITY_HEADERS=true
export ENABLE_RATE_LIMITING=true
export ENABLE_AUDIT_LOGGING=true
export LOG_LEVEL=INFO
"""
