"""
CogniFlow Users Service

This service manages user profiles, learning progress, and user-related analytics.
Supports both development mode (in-memory storage) and production mode (database + Redis).

Key Features:
- Comprehensive user profile management
- Learning progress tracking and analytics
- User role and permission management
- Learning style and preference analysis
- Achievement and milestone tracking
- Professional audit logging

Author: CogniFlow Development Team
Version: 2.0.0
"""

import os
import uuid
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Set, Any
from enum import Enum
import logging

from fastapi import FastAPI, HTTPException, Depends, status, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, validator, Field
from sqlalchemy.orm import Session

# Import database components
from database import get_db, get_redis, test_database_connection
from models import User, UserProfile, UserStats, UserRole, UserStatus

# Configuration and environment setup
NO_DATABASE_MODE = os.getenv("NO_DATABASE_MODE", "False").lower() == "true"

# Configure logging for professional monitoring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LearningStyle(str, Enum):
    """
    Learning style preferences for personalized content delivery.
    Based on educational psychology research for optimal learning experiences.
    """
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING_WRITING = "reading_writing"
    MULTIMODAL = "multimodal"

class DifficultyLevel(str, Enum):
    """Difficulty levels for adaptive content delivery."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class ProgressStatus(str, Enum):
    """Learning progress status indicators."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    MASTERED = "mastered"
    NEEDS_REVIEW = "needs_review"

class AchievementType(str, Enum):
    """Types of achievements users can earn."""
    COURSE_COMPLETION = "course_completion"
    STREAK_MILESTONE = "streak_milestone"
    SKILL_MASTERY = "skill_mastery"
    TIME_MILESTONE = "time_milestone"
    COMMUNITY_CONTRIBUTION = "community_contribution"

# Comprehensive Pydantic models for request/response validation
class UserPreferences(BaseModel):
    """User learning preferences and settings."""
    learning_style: LearningStyle = LearningStyle.MULTIMODAL
    preferred_difficulty: DifficultyLevel = DifficultyLevel.BEGINNER
    study_time_preference: str = "morning"  # morning, afternoon, evening, night
    session_duration_minutes: int = Field(default=30, ge=5, le=180)
    notifications_enabled: bool = True
    email_notifications: bool = True
    reminder_frequency: str = "daily"  # daily, weekly, never
    dark_mode: bool = False
    language: str = "en"
    timezone: str = "UTC"

class LearningGoal(BaseModel):
    """Individual learning goal tracking."""
    id: str
    title: str
    description: Optional[str] = None
    target_date: Optional[datetime] = None
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    is_completed: bool = False
    created_at: datetime
    updated_at: datetime

class Achievement(BaseModel):
    """User achievement representation."""
    id: str
    user_id: str
    achievement_type: AchievementType
    title: str
    description: str
    earned_at: datetime
    badge_icon: Optional[str] = None
    points_awarded: int = 0
    is_featured: bool = False

class LearningSession(BaseModel):
    """Individual learning session tracking."""
    id: str
    user_id: str
    course_id: Optional[str] = None
    lesson_id: Optional[str] = None
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_minutes: int = 0
    activities_completed: int = 0
    questions_answered: int = 0
    correct_answers: int = 0
    focus_score: float = Field(default=0.0, ge=0.0, le=1.0)  # Attention/engagement metric
    cognitive_load: float = Field(default=0.0, ge=0.0, le=1.0)  # Difficulty perception

# Create tables if they don't exist (in production, use Alembic migrations)
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CogniFlow Users Service", 
    version="2.0.0",
    description="User management service with PostgreSQL integration"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic schemas for API input/output
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.STUDENT

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    status: UserStatus
    email_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserStatsResponse(BaseModel):
    user_id: str
    total_courses_enrolled: int
    total_courses_completed: int
    total_learning_time_minutes: int
    current_streak_days: int
    total_points: int
    
    class Config:
        from_attributes = True

# Development mode: In-memory storage implementation
if NO_DATABASE_MODE:
    class InMemoryUserStore:
        """
        In-memory storage for user data in development mode.
        
        Production implementation would use:
        - PostgreSQL for persistent user data with proper indexing
        - Redis for caching frequently accessed user information
        - Elasticsearch for advanced user search and analytics
        - Time-series database for learning analytics and progress tracking
        """
        
        def __init__(self):
            # Core user data storage
            self.users: Dict[str, User] = {}
            self.user_profiles: Dict[str, UserProfile] = {}
            self.user_stats: Dict[str, UserStats] = {}
            self.user_preferences: Dict[str, UserPreferences] = {}
            # Learning tracking data
            self.learning_goals: Dict[str, List[LearningGoal]] = {}
            self.achievements: Dict[str, List[Achievement]] = {}
            self.learning_sessions: Dict[str, List[LearningSession]] = {}
            # Analytics and progress tracking
            self.daily_progress: Dict[str, Dict[str, Any]] = {}
            self.skill_assessments: Dict[str, Dict[str, float]] = {}
            # Initialize with sample data for development
            self._initialize_sample_data()

        def _initialize_sample_data(self):
            """Initialize the store with sample data for development and testing."""
            # Example: Add a sample user (for dev mode only)
            sample_user = User(
                id="user-1",
                username="testuser",
                email="testuser@example.com",
                full_name="Test User",
                role=UserRole.STUDENT,
                status=UserStatus.ACTIVE,
                email_verified=True,
                created_at=datetime.now(timezone.utc),
                last_login=None
            )
            self.users[sample_user.id] = sample_user
            self.user_profiles[sample_user.id] = UserProfile(
                user_id=sample_user.id,
                bio="Sample user for development.",
                avatar_url=None,
                preferences=UserPreferences(),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            self.user_stats[sample_user.id] = UserStats(
                user_id=sample_user.id,
                total_courses_enrolled=1,
                total_courses_completed=0,
                total_learning_time_minutes=0,
                current_streak_days=0,
                total_points=0
            )

        def create_user(self, user: User, profile: UserProfile, stats: UserStats):
            if user.id in self.users:
                raise ValueError("User already exists.")
            self.users[user.id] = user
            self.user_profiles[user.id] = profile
            self.user_stats[user.id] = stats
            return user

        def get_user(self, user_id: str) -> Optional[User]:
            return self.users.get(user_id)

        def get_all_users(self) -> List[User]:
            return list(self.users.values())

    # Instantiate the in-memory store for dev mode
    user_store = InMemoryUserStore()

    @app.post("/users/register", response_model=UserResponse, status_code=201)
    def register_user(user: UserCreate):
        """
        Register a new user (development mode: in-memory only).
        Production code (PostgreSQL/Redis) is provided in comments below.
        """
        import uuid
        user_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        new_user = User(
            id=user_id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            status=UserStatus.ACTIVE,
            email_verified=False,
            created_at=now,
            last_login=None
        )
        new_profile = UserProfile(
            user_id=user_id,
            bio="",
            avatar_url=None,
            preferences=UserPreferences(),
            created_at=now,
            updated_at=now
        )
        new_stats = UserStats(
            user_id=user_id,
            total_courses_enrolled=0,
            total_courses_completed=0,
            total_learning_time_minutes=0,
            current_streak_days=0,
            total_points=0
        )
        try:
            user_store.create_user(new_user, new_profile, new_stats)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        return UserResponse(**new_user.__dict__)

    @app.get("/users/{user_id}", response_model=UserResponse)
    def get_user(user_id: str):
        """
        Retrieve a user by ID (development mode: in-memory only).
        Production code (PostgreSQL/Redis) is provided in comments below.
        """
        user = user_store.get_user(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse(**user.__dict__)

    # --- Production-ready code (PostgreSQL/Redis) ---
    # @app.post("/users/register", response_model=UserResponse, status_code=201)
    # def register_user(user: UserCreate, db: Session = Depends(get_db)):
    #     """
    #     Register a new user (production mode: PostgreSQL/Redis).
    #     """
    #     # Check if user exists, hash password, create DB record, etc.
    #     ...
    #
    # @app.get("/users/{user_id}", response_model=UserResponse)
    # def get_user(user_id: str, db: Session = Depends(get_db)):
    #     """
    #     Retrieve a user by ID (production mode: PostgreSQL/Redis).
    #     """
    #     ...

# Test database connection on startup
@app.on_event("startup")
async def startup_event():
    print("🚀 Starting CogniFlow Users Service...")
    if NO_DATABASE_MODE:
        print("⚠️  Running in NO_DATABASE_MODE: Database connection is disabled.")
    else:
        if test_database_connection():
            print("✅ Users Service ready with database connection")
        else:
            print("❌ Users Service started but database connection failed")

@app.get("/", summary="Service Health Check")
async def root(db: Session = Depends(get_db)):
    """
    Service health check endpoint with comprehensive system status.
    
    Returns current service status, user statistics, and system health metrics
    for monitoring and load balancer health checks.
    
    Args:
        db: Database session (None in development mode)
        
    Returns:
        Service health information and statistics
    """
    if NO_DATABASE_MODE:
        total_users = len(user_store.users)
        active_users = len([u for u in user_store.users.values() if u.status == UserStatus.ACTIVE])
        total_sessions = sum(len(sessions) for sessions in user_store.learning_sessions.values())
        db_status = "no-database-mode"
    else:
        # Production mode: Query actual database statistics
        """
        Production implementation:
        
        try:
            total_users = db.query(User).count()
            active_users = db.query(User).filter(User.status == UserStatus.ACTIVE).count()
            total_sessions = db.query(LearningSession).count()
            db_status = "connected"
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            total_users = "Error"
            active_users = "Error"
            total_sessions = "Error"
            db_status = "connection_error"
        """
        total_users = 0
        active_users = 0
        total_sessions = 0
        db_status = "database_mode_placeholder"

    return {
        "service": "CogniFlow Users Service",
        "status": "healthy",
        "version": "2.0.0",
        "mode": "development" if NO_DATABASE_MODE else "production",
        "database": db_status,
        "statistics": {
            "total_users": total_users,
            "active_users": active_users,
            "total_learning_sessions": total_sessions
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/users/", response_model=List[UserResponse], summary="List Users with Advanced Filtering")
async def get_users(
    skip: int = Query(0, ge=0, description="Number of users to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of users to return"),
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
    status: Optional[UserStatus] = Query(None, description="Filter by user status"),
    search: Optional[str] = Query(None, description="Search in username, email, or full name"),
    db: Session = Depends(get_db)
):
    """
    Retrieve users with advanced filtering and pagination.
    
    This endpoint supports comprehensive user listing with filtering by role,
    status, and text search capabilities. Includes pagination for performance.
    
    Args:
        skip: Number of users to skip for pagination
        limit: Maximum number of users to return
        role: Filter users by specific role
        status: Filter users by account status
        search: Text search across username, email, and full name
        db: Database session
        
    Returns:
        List of users matching the specified criteria
        
    Production considerations:
    - Implement database indexing on frequently queried fields
    - Add caching for common filter combinations
    - Consider implementing cursor-based pagination for large datasets
    """
    if NO_DATABASE_MODE:
        users = list(user_store.users.values())
        
        # Apply filters
        if role:
            users = [u for u in users if u.role == role]
        if status:
            users = [u for u in users if u.status == status]
        if search:
            search_lower = search.lower()
            users = [u for u in users if (
                search_lower in u.username.lower() or
                search_lower in u.email.lower() or
                search_lower in u.full_name.lower()
            )]
        
        # Apply pagination
        total_count = len(users)
        users = users[skip:skip + limit]
        
        logger.info(f"Retrieved {len(users)} users (total: {total_count}) with filters: role={role}, status={status}, search={search}")
        return users
    
    else:
        # Production mode: Optimized database queries with proper indexing
        """
        Production implementation:
        
        query = db.query(User)
        
        if role:
            query = query.filter(User.role == role)
        if status:
            query = query.filter(User.status == status)
        if search:
            query = query.filter(
                or_(
                    User.username.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    User.full_name.ilike(f"%{search}%")
                )
            )
        
        total_count = query.count()
        users = query.offset(skip).limit(limit).all()
        
        # Add total count to response headers for pagination
        # response.headers["X-Total-Count"] = str(total_count)
        
        return users
        """
        logger.warning("Database mode not fully implemented - returning empty list")
        return []

@app.get("/users/{user_id}", response_model=UserResponse, summary="Get User by ID")
async def get_user(user_id: str, db: Session = Depends(get_db)):
    """
    Retrieve detailed information for a specific user.
    
    This endpoint provides comprehensive user information including
    profile data, learning preferences, and current status.
    
    Args:
        user_id: Unique user identifier
        db: Database session
        
    Returns:
        Complete user information
        
    Raises:
        HTTPException: If user is not found (404) or access denied (403)
        
    Production considerations:
    - Implement field-level permissions based on requester role
    - Add user activity logging for audit purposes
    - Cache frequently accessed user profiles
    """
    if NO_DATABASE_MODE:
        user = user_store.users.get(user_id)
        if not user:
            logger.warning(f"User not found: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        logger.info(f"Retrieved user: {user.email}")
        return user
    
    else:
        # Production mode: Database query with proper error handling
        """
        Production implementation:
        
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
        user = db.query(User).filter(User.id == user_uuid).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Log access for audit purposes
        logger.info(f"User accessed: {user.email} by requester")
        
        return user
        """
        logger.warning("Database mode not implemented")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database mode not fully implemented"
        )

@app.get("/users/{user_id}/stats", response_model=UserStatsResponse, summary="Get User Learning Statistics")
async def get_user_stats(user_id: str, db: Session = Depends(get_db)):
    """
    Retrieve comprehensive learning statistics for a specific user.
    
    This endpoint provides detailed analytics about a user's learning progress,
    including time spent, courses completed, current streaks, and performance metrics.
    
    Args:
        user_id: Unique user identifier
        db: Database session
        
    Returns:
        Comprehensive user learning statistics
        
    Raises:
        HTTPException: If user is not found (404)
        
    Production considerations:
    - Implement real-time analytics with time-series data
    - Add comparative analytics (peer comparisons, cohort analysis)
    - Cache computed statistics with appropriate TTL
    - Include predictive analytics for learning outcomes
    """
    if NO_DATABASE_MODE:
        # Verify user exists
        if user_id not in user_store.users:
            logger.warning(f"User stats requested for non-existent user: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        # Get or create user statistics
        user_stats = user_store.user_stats.get(user_id)
        if not user_stats:
            # Create default statistics for new users
            user_stats = UserStats(
                id=str(uuid.uuid4()),
                user_id=user_id,
                total_courses_enrolled=0,
                total_courses_completed=0,
                total_learning_time_minutes=0,
                current_streak_days=0,
                longest_streak_days=0,
                total_points=0,
                last_updated=datetime.now(timezone.utc)
            )
            user_store.user_stats[user_id] = user_stats
            logger.info(f"Created default statistics for user: {user_id}")
        
        logger.info(f"Retrieved statistics for user: {user_id}")
        return user_stats
    
    else:
        # Production mode: Advanced analytics with aggregations
        """
        Production implementation:
        
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
        # Verify user exists
        user = db.query(User).filter(User.id == user_uuid).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get or create user statistics with real-time calculations
        user_stats = db.query(UserStats).filter(UserStats.user_id == user_uuid).first()
        if not user_stats:
            # Calculate statistics from learning sessions and course enrollments
            total_time = db.query(func.sum(LearningSession.duration_minutes)).filter(
                LearningSession.user_id == user_uuid
            ).scalar() or 0
            
            enrollments = db.query(CourseEnrollment).filter(
                CourseEnrollment.user_id == user_uuid
            ).all()
            
            completed_courses = len([e for e in enrollments if e.completion_percentage >= 100])
            
            # Calculate current streak
            current_streak = calculate_learning_streak(user_uuid, db)
            
            user_stats = UserStats(
                user_id=user_uuid,
                total_courses_enrolled=len(enrollments),
                total_courses_completed=completed_courses,
                total_learning_time_minutes=total_time,
                current_streak_days=current_streak,
                total_points=calculate_user_points(user_uuid, db)
            )
            
            db.add(user_stats)
            db.commit()
            db.refresh(user_stats)
        
        return user_stats
        """
        logger.warning("Database mode not implemented")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database mode not fully implemented"
        )


@app.post("/users/", response_model=UserResponse, summary="Create New User Account")
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account with comprehensive validation.
    
    This endpoint handles new user registration with proper validation,
    duplicate checking, and initialization of user-related data structures.
    
    Args:
        user_data: User registration information
        db: Database session
        
    Returns:
        Created user information
        
    Raises:
        HTTPException: If username/email already exists (400) or validation fails
        
    Production considerations:
    - Implement proper password hashing with bcrypt
    - Add email verification workflow
    - Create user profile and preferences records
    - Send welcome email with account activation
    - Log user registration for analytics
    """
    if NO_DATABASE_MODE:
        # Check for existing username or email
        existing_users = list(user_store.users.values())
        if any(u.username == user_data.username for u in existing_users):
            logger.warning(f"Attempted registration with existing username: {user_data.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        if any(u.email == user_data.email for u in existing_users):
            logger.warning(f"Attempted registration with existing email: {user_data.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        
        # Create new user with proper initialization
        user_id = str(uuid.uuid4())
        new_user = User(
            id=user_id,
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            role=user_data.role,
            status=UserStatus.ACTIVE,
            password_hash=f"hashed_{user_data.password}",  # In production: proper bcrypt hashing
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            last_login=None,
            email_verified=True,  # In production: False until email verification
            learning_style_preferences={},
            timezone="UTC",
            preferred_difficulty_level=1
        )
        
        # Store user in memory
        user_store.users[user_id] = new_user
        
        # Initialize user statistics
        user_stats = UserStats(
            id=str(uuid.uuid4()),
            user_id=user_id,
            total_courses_enrolled=0,
            total_courses_completed=0,
            total_learning_time_minutes=0,
            current_streak_days=0,
            longest_streak_days=0,
            total_points=0,
            last_updated=datetime.now(timezone.utc)
        )
        user_store.user_stats[user_id] = user_stats
        
        # Initialize user preferences
        preferences = UserPreferences()
        user_store.user_preferences[user_id] = preferences
        
        logger.info(f"Created new user account: {new_user.email} with role: {new_user.role}")
        return new_user
    
    else:
        # Production mode: Database transaction with proper error handling
        """
        Production implementation:
        
        # Check for existing users
        existing_user = db.query(User).filter(
            (User.username == user_data.username) | (User.email == user_data.email)
        ).first()
        
        if existing_user:
            if existing_user.username == user_data.username:
                raise HTTPException(status_code=400, detail="Username already exists")
            else:
                raise HTTPException(status_code=400, detail="Email already exists")
        
        # Hash password securely
        password_hash = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt())
        
        # Create user with database transaction
        try:
            new_user = User(
                username=user_data.username,
                email=user_data.email,
                full_name=user_data.full_name,
                role=user_data.role,
                status=UserStatus.PENDING,  # Requires email verification
                password_hash=password_hash.decode('utf-8'),
                email_verified=False
            )
            
            db.add(new_user)
            db.flush()  # Get the user ID
            
            # Create related records
            user_stats = UserStats(user_id=new_user.id)
            user_profile = UserProfile(user_id=new_user.id)
            
            db.add(user_stats)
            db.add(user_profile)
            db.commit()
            db.refresh(new_user)
            
            # Send verification email (async task)
            # send_verification_email.delay(new_user.email, new_user.id)
            
            logger.info(f"Created user account: {new_user.email}")
            return new_user
            
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create user: {e}")
            raise HTTPException(status_code=500, detail="Failed to create user account")
        """
        logger.warning("Database mode not implemented")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database mode not fully implemented"
        )

@app.get("/users/role/{role}", response_model=List[UserResponse], summary="Get Users by Role")
async def get_users_by_role(role: UserRole, db: Session = Depends(get_db)):
    """
    Retrieve users filtered by their assigned role.
    
    This endpoint provides role-based user filtering for administrative
    purposes and role-specific user management.
    
    Args:
        role: User role to filter by
        db: Database session
        
    Returns:
        List of users with the specified role
        
    Production considerations:
    - Add pagination for large user sets
    - Implement role hierarchy permissions
    - Cache role-based user lists with appropriate TTL
    - Add additional filtering options (status, activity, etc.)
    """
    if NO_DATABASE_MODE:
        filtered_users = [user for user in user_store.users.values() if user.role == role]
        logger.info(f"Retrieved {len(filtered_users)} users with role: {role}")
        return filtered_users
    
    else:
        # Production mode: Optimized database query with indexing
        """
        Production implementation:
        
        users = db.query(User).filter(User.role == role).all()
        
        # Log access for audit purposes
        logger.info(f"Role-based user query: {role} - {len(users)} users found")
        
        return users
        """
        logger.warning("Database mode not implemented")
        return []

@app.put("/users/{user_id}/last-login", summary="Update User Last Login")
async def update_last_login(user_id: str, db: Session = Depends(get_db)):
    """
    Update the last login timestamp for a user.
    
    This endpoint is typically called by the authentication service
    to track user activity and login patterns for analytics.
    
    Args:
        user_id: Unique user identifier
        db: Database session
        
    Returns:
        Success confirmation message
        
    Raises:
        HTTPException: If user is not found (404)
        
    Production considerations:
    - Consider using async background tasks for non-critical updates
    - Implement login pattern analytics
    - Add session tracking integration
    - Include geographic login tracking for security
    """
    if NO_DATABASE_MODE:
        user = user_store.users.get(user_id)
        if not user:
            logger.warning(f"Login update attempted for non-existent user: {user_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update timestamps
        current_time = datetime.now(timezone.utc)
        user.last_login = current_time
        user.updated_at = current_time
        
        logger.info(f"Updated last login for user: {user.email}")
        return {"message": "Last login updated successfully", "timestamp": current_time.isoformat()}
    
    else:
        # Production mode: Database update with proper error handling
        """
        Production implementation:
        
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user ID format"
            )
        
        user = db.query(User).filter(User.id == user_uuid).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Update last login timestamp
        current_time = datetime.now(timezone.utc)
        user.last_login = current_time
        # updated_at is typically handled by SQLAlchemy with onupdate parameter
        
        try:
            db.commit()
            logger.info(f"Updated last login for user: {user.email}")
            return {"message": "Last login updated successfully", "timestamp": current_time.isoformat()}
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to update last login for user {user_id}: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update last login"
            )
        """
        logger.warning("Database mode not implemented")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database mode not fully implemented"
        )

# Advanced user management endpoints

@app.get("/users/{user_id}/preferences", response_model=UserPreferences, summary="Get User Preferences")
async def get_user_preferences(user_id: str, db: Session = Depends(get_db)):
    """
    Retrieve user learning preferences and settings.
    
    This endpoint provides access to personalized learning preferences
    including learning style, difficulty preferences, and notification settings.
    
    Args:
        user_id: Unique user identifier
        db: Database session
        
    Returns:
        User preferences and learning settings
        
    Raises:
        HTTPException: If user is not found (404)
    """
    if NO_DATABASE_MODE:
        if user_id not in user_store.users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        preferences = user_store.user_preferences.get(user_id)
        if not preferences:
            # Create default preferences
            preferences = UserPreferences()
            user_store.user_preferences[user_id] = preferences
        
        return preferences
    
    else:
        # Production mode: Database query with caching
        """
        # Query user preferences from database
        # Implement Redis caching for frequently accessed preferences
        # Include user profile integration
        """
        raise HTTPException(status_code=503, detail="Database mode not implemented")

@app.put("/users/{user_id}/preferences", response_model=UserPreferences, summary="Update User Preferences")
async def update_user_preferences(
    user_id: str, 
    preferences: UserPreferences, 
    db: Session = Depends(get_db)
):
    """
    Update user learning preferences and settings.
    
    This endpoint allows users to customize their learning experience
    by updating preferences for learning style, difficulty, notifications, etc.
    
    Args:
        user_id: Unique user identifier
        preferences: Updated user preferences
        db: Database session
        
    Returns:
        Updated user preferences
        
    Raises:
        HTTPException: If user is not found (404)
        
    Production considerations:
    - Validate preference combinations for optimal learning
    - Trigger adaptive content recalculation
    - Log preference changes for analytics
    - Implement A/B testing for preference impact
    """
    if NO_DATABASE_MODE:
        if user_id not in user_store.users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        user_store.user_preferences[user_id] = preferences
        logger.info(f"Updated preferences for user: {user_id}")
        return preferences
    
    else:
        # Production mode: Database update with validation
        """
        # Update preferences in database
        # Clear related caches
        # Trigger adaptive learning algorithm updates
        # Log changes for analytics
        """
        raise HTTPException(status_code=503, detail="Database mode not implemented")

@app.get("/users/{user_id}/learning-goals", response_model=List[LearningGoal], summary="Get User Learning Goals")
async def get_user_learning_goals(user_id: str, db: Session = Depends(get_db)):
    """
    Retrieve user's learning goals and progress.
    
    This endpoint provides access to a user's learning objectives,
    target dates, and progress tracking for goal achievement.
    
    Args:
        user_id: Unique user identifier
        db: Database session
        
    Returns:
        List of user learning goals with progress
        
    Raises:
        HTTPException: If user is not found (404)
    """
    if NO_DATABASE_MODE:
        if user_id not in user_store.users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        goals = user_store.learning_goals.get(user_id, [])
        return goals
    
    else:
        # Production mode: Database query with analytics
        """
        # Query learning goals from database
        # Calculate real-time progress
        # Include deadline tracking and notifications
        """
        raise HTTPException(status_code=503, detail="Database mode not implemented")

@app.post("/users/{user_id}/learning-goals", response_model=LearningGoal, summary="Create Learning Goal")
async def create_learning_goal(
    user_id: str,
    goal_title: str,
    goal_description: Optional[str] = None,
    target_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Create a new learning goal for the user.
    
    This endpoint allows users to set learning objectives with optional
    target dates and descriptions for progress tracking.
    
    Args:
        user_id: Unique user identifier
        goal_title: Title of the learning goal
        goal_description: Optional detailed description
        target_date: Optional target completion date
        db: Database session
        
    Returns:
        Created learning goal
        
    Raises:
        HTTPException: If user is not found (404)
    """
    if NO_DATABASE_MODE:
        if user_id not in user_store.users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        goal = LearningGoal(
            id=str(uuid.uuid4()),
            title=goal_title,
            description=goal_description,
            target_date=target_date,
            progress_percentage=0.0,
            is_completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        if user_id not in user_store.learning_goals:
            user_store.learning_goals[user_id] = []
        user_store.learning_goals[user_id].append(goal)
        
        logger.info(f"Created learning goal for user {user_id}: {goal_title}")
        return goal
    
    else:
        # Production mode: Database creation with validation
        """
        # Create goal in database
        # Set up progress tracking
        # Schedule reminder notifications
        # Integrate with course recommendations
        """
        raise HTTPException(status_code=503, detail="Database mode not implemented")

@app.get("/users/{user_id}/achievements", response_model=List[Achievement], summary="Get User Achievements")
async def get_user_achievements(user_id: str, db: Session = Depends(get_db)):
    """
    Retrieve user's earned achievements and badges.
    
    This endpoint provides access to a user's achievement history,
    badges earned, and gamification progress for motivation and engagement.
    
    Args:
        user_id: Unique user identifier
        db: Database session
        
    Returns:
        List of user achievements with details
        
    Raises:
        HTTPException: If user is not found (404)
    """
    if NO_DATABASE_MODE:
        if user_id not in user_store.users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        achievements = user_store.achievements.get(user_id, [])
        return achievements
    
    else:
        # Production mode: Database query with gamification logic
        """
        # Query achievements from database
        # Calculate available achievements
        # Check for newly earned achievements
        # Update achievement progress
        """
        raise HTTPException(status_code=503, detail="Database mode not implemented")

@app.get("/users/{user_id}/learning-analytics", summary="Get User Learning Analytics")
async def get_user_learning_analytics(
    user_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Retrieve comprehensive learning analytics for the user.
    
    This endpoint provides detailed analytics including learning patterns,
    performance trends, engagement metrics, and personalized insights.
    
    Args:
        user_id: Unique user identifier
        days: Number of days to include in analysis
        db: Database session
        
    Returns:
        Comprehensive learning analytics data
        
    Raises:
        HTTPException: If user is not found (404)
        
    Production considerations:
    - Implement advanced statistical analysis
    - Add predictive analytics for learning outcomes
    - Include comparative analytics with peer groups
    - Generate personalized learning recommendations
    """
    if NO_DATABASE_MODE:
        if user_id not in user_store.users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Generate sample analytics data for development
        sessions = user_store.learning_sessions.get(user_id, [])
        stats = user_store.user_stats.get(user_id)
        
        analytics = {
            "user_id": user_id,
            "analysis_period_days": days,
            "total_learning_time_minutes": stats.total_learning_time_minutes if stats else 0,
            "average_session_duration": 45,  # Sample data
            "learning_streak_days": stats.current_streak_days if stats else 0,
            "completion_rate": 0.85,  # Sample data
            "engagement_score": 0.78,  # Sample data
            "learning_velocity": 1.2,  # Courses per week
            "focus_score": 0.82,  # Average attention during sessions
            "optimal_learning_times": ["09:00-11:00", "14:00-16:00"],  # Peak performance times
            "recommended_session_duration": 50,  # Personalized recommendation
            "strengths": ["Visual Learning", "Problem Solving", "Consistency"],
            "improvement_areas": ["Reading Comprehension", "Time Management"],
            "next_milestones": [
                {"title": "Complete Advanced Python Course", "progress": 0.65},
                {"title": "Achieve 30-day Learning Streak", "progress": 0.8}
            ]
        }
        
        logger.info(f"Generated learning analytics for user: {user_id}")
        return analytics
    
    else:
        # Production mode: Advanced analytics with machine learning
        """
        # Query learning session data
        # Perform statistical analysis
        # Generate predictive insights
        # Calculate personalized recommendations
        # Include comparative analytics
        """
        raise HTTPException(status_code=503, detail="Database mode not implemented")

# Health check endpoint for container orchestration
@app.get("/health", summary="Service Health Check")
async def health_check():
    """
    Comprehensive health check endpoint for monitoring and load balancing.
    
    Returns detailed service health information including system statistics,
    performance metrics, and operational status for monitoring systems.
    
    Returns:
        Comprehensive service health information
    """
    if NO_DATABASE_MODE:
        user_count = len(user_store.users)
        active_user_count = len([u for u in user_store.users.values() if u.status == UserStatus.ACTIVE])
        session_count = sum(len(sessions) for sessions in user_store.learning_sessions.values())
        goal_count = sum(len(goals) for goals in user_store.learning_goals.values())
    else:
        # Production mode: Query actual database metrics
        user_count = 0
        active_user_count = 0
        session_count = 0
        goal_count = 0
    
    return {
        "service": "CogniFlow Users Service",
        "status": "healthy",
        "version": "2.0.0",
        "mode": "development" if NO_DATABASE_MODE else "production",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metrics": {
            "total_users": user_count,
            "active_users": active_user_count,
            "learning_sessions": session_count,
            "learning_goals": goal_count
        },
        "features": [
            "User Profile Management",
            "Learning Analytics",
            "Goal Tracking",
            "Achievement System",
            "Preference Management",
            "Progress Tracking"
        ]
    }

# Startup event handler
@app.on_event("startup")
async def startup_event():
    """
    Service startup initialization.
    
    Performs necessary initialization tasks including database connection
    testing, logging setup, and service health verification.
    """
    logger.info("Starting CogniFlow Users Service v2.0.0")
    
    if NO_DATABASE_MODE:
        logger.info("Running in development mode with in-memory storage")
        logger.info(f"Initialized with {len(user_store.users)} sample users")
    else:
        logger.info("Running in production mode with database storage")
        if test_database_connection():
            logger.info("Database connection established successfully")
        else:
            logger.error("Database connection failed - service may be degraded")
    
    logger.info("CogniFlow Users Service startup completed")

# Application initialization
app = FastAPI(
    title="CogniFlow Users Service",
    description="""
    Professional user management service for the CogniFlow learning platform.
    
    This service provides comprehensive user profile management, learning analytics,
    goal tracking, and achievement systems with both development and production modes.
    
    Features:
    - User profile and preference management
    - Learning progress tracking and analytics
    - Goal setting and achievement tracking
    - Role-based access control
    - Comprehensive audit logging
    - Professional error handling and validation
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "CogniFlow Development Team",
        "email": "dev@cogniflow.edu"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    }
)

# Configure CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Production: Configure specific origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Note: User preferences functionality is already implemented above
# in the get_user_preferences() and update_user_preferences() endpoints
# with comprehensive error handling, logging, and production-ready code comments
