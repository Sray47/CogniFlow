# services/users-service/models.py
import os
NO_DATABASE_MODE = os.getenv("NO_DATABASE_MODE", "False").lower() == "true"

if NO_DATABASE_MODE:
    # --- DEVELOPMENT MODE: Use Pydantic models only ---
    from pydantic import BaseModel, EmailStr
    from enum import Enum as PyEnum
    import datetime
    from typing import Optional # Added Optional

    class UserRole(PyEnum):
        STUDENT = "student"
        INSTRUCTOR = "instructor"
        ADMIN = "admin"

    class UserStatus(PyEnum):
        ACTIVE = "active"
        INACTIVE = "inactive"
        PENDING = "pending"
        SUSPENDED = "suspended"

    class User(BaseModel):
        id: str
        username: str
        email: EmailStr
        full_name: str
        role: UserRole = UserRole.STUDENT
        status: UserStatus = UserStatus.PENDING
        password_hash: str
        created_at: datetime.datetime
        updated_at: datetime.datetime
        last_login: Optional[datetime.datetime] = None # Changed to Optional
        email_verified: bool = False
        learning_style_preferences: dict = {}
        timezone: str = 'UTC'
        preferred_difficulty_level: int = 1

    class UserProfile(BaseModel):
        id: str
        user_id: str
        avatar_url: Optional[str] = None # Assuming avatar_url can also be None
        bio: Optional[str] = None # Assuming bio can also be None
        date_of_birth: Optional[datetime.datetime] = None # Changed to Optional
        occupation: Optional[str] = None # Assuming occupation can also be None
        education_level: Optional[str] = None # Assuming education_level can also be None
        interests: list = []
        goals: list = []
        working_memory_capacity: int = 7
        attention_span_minutes: int = 25
        optimal_study_time: Optional[str] = None # Assuming optimal_study_time can also be None
        created_at: Optional[datetime.datetime] = None # Changed to Optional
        updated_at: Optional[datetime.datetime] = None # Changed to Optional

    class UserStats(BaseModel):
        id: Optional[str] = None # Changed to Optional
        user_id: str
        total_courses_enrolled: int = 0
        total_courses_completed: int = 0
        total_learning_time_minutes: int = 0
        current_streak_days: int = 0
        longest_streak_days: int = 0
        total_points: int = 0
        average_cognitive_load: Optional[str] = None # Changed to Optional
        preferred_learning_pace: Optional[str] = None # Changed to Optional
        optimal_session_duration_minutes: Optional[int] = None # Changed to Optional
        last_updated: Optional[datetime.datetime] = None # Changed to Optional

else:
    # --- PRODUCTION MODE: Use SQLAlchemy models ---
    # Uncomment this block and comment out the dev mode block above for production
    from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ARRAY, JSON
    from sqlalchemy.dialects.postgresql import UUID, ENUM
    from sqlalchemy.sql import func
    from database import Base
    import uuid
    from enum import Enum as PyEnum

    class UserRole(PyEnum):
        STUDENT = "student"
        INSTRUCTOR = "instructor"
        ADMIN = "admin"

    class UserStatus(PyEnum):
        ACTIVE = "active"
        INACTIVE = "inactive"
        PENDING = "pending"
        SUSPENDED = "suspended"

    class User(Base):
        __tablename__ = "users"
        
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        username = Column(String(50), unique=True, nullable=False)
        email = Column(String(255), unique=True, nullable=False)
        full_name = Column(String(255), nullable=False)
        role = Column(ENUM(UserRole), default=UserRole.STUDENT)
        status = Column(ENUM(UserStatus), default=UserStatus.PENDING)
        password_hash = Column(String(255), nullable=False)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
        last_login = Column(DateTime(timezone=True), nullable=True)
        email_verified = Column(Boolean, default=False)
        learning_style_preferences = Column(JSON, default={})
        timezone = Column(String(50), default='UTC')
        preferred_difficulty_level = Column(Integer, default=1)

    class UserProfile(Base):
        __tablename__ = "user_profiles"
        
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        user_id = Column(UUID(as_uuid=True), nullable=False)  # Foreign key
        avatar_url = Column(String(500), nullable=True)
        bio = Column(Text, nullable=True)
        date_of_birth = Column(DateTime, nullable=True)
        occupation = Column(String(255), nullable=True)
        education_level = Column(String(100), nullable=True)
        interests = Column(ARRAY(Text), nullable=True)
        goals = Column(ARRAY(Text), nullable=True)
        working_memory_capacity = Column(Integer, default=7)
        attention_span_minutes = Column(Integer, default=25)
        optimal_study_time = Column(String(50), nullable=True)
        created_at = Column(DateTime(timezone=True), server_default=func.now())
        updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    class UserStats(Base):
        __tablename__ = "user_stats"
        
        id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
        user_id = Column(UUID(as_uuid=True), unique=True, nullable=False)
        total_courses_enrolled = Column(Integer, default=0)
        total_courses_completed = Column(Integer, default=0)
        total_learning_time_minutes = Column(Integer, default=0)
        current_streak_days = Column(Integer, default=0)
        longest_streak_days = Column(Integer, default=0)
        total_points = Column(Integer, default=0)
        average_cognitive_load = Column(String)  # Using String instead of DECIMAL for simplicity
        preferred_learning_pace = Column(String(20), nullable=True)
        optimal_session_duration_minutes = Column(Integer, nullable=True)
        last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

# ---
# HOW TO USE:
# - For development without a database, set NO_DATABASE_MODE=true in your environment.
# - For production, set NO_DATABASE_MODE=false (or unset it) and uncomment the production code above.
# ---
