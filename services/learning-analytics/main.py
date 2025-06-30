# services/learning-analytics/main.py

"""
Learning Analytics Service

This service provides comprehensive learning progress tracking and analytics capabilities.
It monitors user learning behavior, course completion, lesson progress, and generates
insights for both learners and instructors.

Development Mode: Uses in-memory data structures for rapid prototyping
Production Mode: Integrates with PostgreSQL for persistence and Redis for caching

Author: CogniFlow Development Team
Version: 1.0.0
"""

import os
import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from dataclasses import dataclass, field
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration for deployment mode
NO_DATABASE_MODE = os.getenv("NO_DATABASE_MODE", "False").lower() == "true"

# Development mode imports
if NO_DATABASE_MODE:
    # In-memory data structures for development
    from collections import defaultdict
    import json
else:
    # Production mode imports (commented for now)
    # from sqlalchemy import create_engine, Column, String, Integer, DateTime, Float, Boolean, Text, JSON
    # from sqlalchemy.ext.declarative import declarative_base
    # from sqlalchemy.orm import sessionmaker, Session
    # import redis
    pass

app = FastAPI(
    title="CogniFlow Learning Analytics Service",
    version="1.0.0",
    description="Advanced learning progress tracking and analytics system"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production: Replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Data Models and Enums
class LearningEventType(str, Enum):
    """Types of learning events that can be tracked"""
    LESSON_START = "lesson_start"
    LESSON_COMPLETE = "lesson_complete"
    LESSON_PAUSE = "lesson_pause"
    LESSON_RESUME = "lesson_resume"
    QUIZ_ATTEMPT = "quiz_attempt"
    QUIZ_COMPLETE = "quiz_complete"
    COURSE_ENROLL = "course_enroll"
    COURSE_COMPLETE = "course_complete"
    SESSION_START = "session_start"
    SESSION_END = "session_end"


class LearningDifficulty(str, Enum):
    """Perceived difficulty levels for content adaptation"""
    TOO_EASY = "too_easy"
    JUST_RIGHT = "just_right"
    CHALLENGING = "challenging"
    TOO_DIFFICULT = "too_difficult"


class CompletionStatus(str, Enum):
    """Status of learning content completion"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    PAUSED = "paused"
    FAILED = "failed"


# Pydantic Models for API Request/Response
class LearningEventRequest(BaseModel):
    """Request model for recording learning events"""
    user_id: str
    course_id: int
    lesson_id: Optional[int] = None
    event_type: LearningEventType
    event_data: Dict[str, Any] = {}
    timestamp: Optional[datetime.datetime] = None
    
    @validator('timestamp', pre=True, always=True)
    def set_timestamp(cls, v):
        return v or datetime.datetime.utcnow()


class ProgressUpdateRequest(BaseModel):
    """Request model for updating learning progress"""
    user_id: str
    course_id: int
    lesson_id: int
    completion_percentage: float
    time_spent_minutes: int
    difficulty_rating: Optional[LearningDifficulty] = None
    notes: Optional[str] = None
    
    @validator('completion_percentage')
    def validate_percentage(cls, v):
        if not 0 <= v <= 100:
            raise ValueError('Completion percentage must be between 0 and 100')
        return v


class LearningSessionRequest(BaseModel):
    """Request model for learning session tracking"""
    user_id: str
    course_id: int
    session_start: datetime.datetime
    session_end: Optional[datetime.datetime] = None
    lessons_accessed: List[int] = []
    total_engagement_score: Optional[float] = None


# Response Models
class LearningProgressResponse(BaseModel):
    """Response model for learning progress data"""
    user_id: str
    course_id: int
    course_title: str
    overall_progress_percentage: float
    total_time_spent_minutes: int
    lessons_completed: int
    total_lessons: int
    current_lesson_id: Optional[int]
    estimated_completion_time: Optional[datetime.datetime]
    last_accessed: datetime.datetime
    completion_status: CompletionStatus
    average_difficulty_rating: Optional[float]


class LearningAnalyticsResponse(BaseModel):
    """Response model for comprehensive learning analytics"""
    user_id: str
    total_courses_enrolled: int
    total_courses_completed: int
    total_learning_time_hours: float
    average_completion_rate: float
    learning_streak_days: int
    preferred_learning_time: Optional[str]
    learning_velocity: float  # lessons per day
    retention_score: float
    engagement_score: float


# Development Mode: In-Memory Data Storage
if NO_DATABASE_MODE:
    
    @dataclass
    class LearningEvent:
        """In-memory learning event data structure"""
        id: str = field(default_factory=lambda: str(uuid.uuid4()))
        user_id: str = ""
        course_id: int = 0
        lesson_id: Optional[int] = None
        event_type: LearningEventType = LearningEventType.SESSION_START
        event_data: Dict[str, Any] = field(default_factory=dict)
        timestamp: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    
    
    @dataclass
    class LearningProgress:
        """In-memory learning progress data structure"""
        id: str = field(default_factory=lambda: str(uuid.uuid4()))
        user_id: str = ""
        course_id: int = 0
        lesson_id: int = 0
        completion_percentage: float = 0.0
        time_spent_minutes: int = 0
        difficulty_rating: Optional[LearningDifficulty] = None
        notes: Optional[str] = None
        last_updated: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
        completion_status: CompletionStatus = CompletionStatus.NOT_STARTED
    
    
    @dataclass
    class LearningSession:
        """In-memory learning session data structure"""
        id: str = field(default_factory=lambda: str(uuid.uuid4()))
        user_id: str = ""
        course_id: int = 0
        session_start: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
        session_end: Optional[datetime.datetime] = None
        lessons_accessed: List[int] = field(default_factory=list)
        total_engagement_score: Optional[float] = None
    
    # In-memory storage
    learning_events: List[LearningEvent] = []
    learning_progress: List[LearningProgress] = []
    learning_sessions: List[LearningSession] = []
    
    # Sample data for development
    sample_courses = {
        1: {"title": "Introduction to Artificial Intelligence", "total_lessons": 8},
        2: {"title": "Advanced Python Programming", "total_lessons": 12},
        3: {"title": "Data Science Fundamentals", "total_lessons": 10},
    }


# Production Mode: Database Models (Commented for development)
"""
Production Database Models - Uncomment and configure for production deployment

from sqlalchemy import Column, String, Integer, DateTime, Float, Boolean, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class LearningEventDB(Base):
    __tablename__ = "learning_events"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    course_id = Column(Integer, nullable=False, index=True)
    lesson_id = Column(Integer, nullable=True)
    event_type = Column(String, nullable=False)
    event_data = Column(JSON, default={})
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)

class LearningProgressDB(Base):
    __tablename__ = "learning_progress"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    course_id = Column(Integer, nullable=False)
    lesson_id = Column(Integer, nullable=False)
    completion_percentage = Column(Float, default=0.0)
    time_spent_minutes = Column(Integer, default=0)
    difficulty_rating = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    completion_status = Column(String, default=CompletionStatus.NOT_STARTED.value)

class LearningSessionDB(Base):
    __tablename__ = "learning_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    course_id = Column(Integer, nullable=False)
    session_start = Column(DateTime, nullable=False)
    session_end = Column(DateTime, nullable=True)
    lessons_accessed = Column(JSON, default=[])
    total_engagement_score = Column(Float, nullable=True)

# Database connection setup for production
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL) if DATABASE_URL else None
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None

def get_db():
    if not SessionLocal:
        yield None
    else:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
"""


# --- Import the Store Implementation ---
from store import AnalyticsStoreInterface, InMemoryAnalyticsStore

# Initialize store based on mode
if NO_DATABASE_MODE:
    analytics_store = InMemoryAnalyticsStore()
else:
    # Production mode: Use PostgreSQL/Redis implementation
    # from store import PostgreSQLAnalyticsStore
    # analytics_store = PostgreSQLAnalyticsStore(db_session, redis_client)
    pass

# Utility Functions
def calculate_learning_velocity(user_id: str, days: int = 7) -> float:
    """
    Calculate learning velocity (lessons completed per day) for a user
    
    Args:
        user_id: User identifier
        days: Number of days to analyze (default: 7)
    
    Returns:
        Average lessons completed per day
    """
    if NO_DATABASE_MODE:
        # Development mode calculation
        cutoff_date = datetime.datetime.utcnow() - datetime.timedelta(days=days)
        completed_events = [
            event for event in learning_events
            if (event.user_id == user_id and 
                event.event_type == LearningEventType.LESSON_COMPLETE and
                event.timestamp >= cutoff_date)
        ]
        return len(completed_events) / days if days > 0 else 0.0
    else:
        # Production mode: Query database for lesson completion events
        # db_session = get_db()
        # completed_lessons = db_session.query(LearningEventDB).filter(
        #     LearningEventDB.user_id == user_id,
        #     LearningEventDB.event_type == LearningEventType.LESSON_COMPLETE,
        #     LearningEventDB.timestamp >= cutoff_date
        # ).count()
        # return completed_lessons / days if days > 0 else 0.0
        return 0.0


def calculate_engagement_score(user_id: str, course_id: int) -> float:
    """
    Calculate engagement score based on learning patterns and behavior
    
    Args:
        user_id: User identifier
        course_id: Course identifier
    
    Returns:
        Engagement score between 0.0 and 1.0
    """
    if NO_DATABASE_MODE:
        # Development mode: Calculate based on session data and events
        user_events = [
            event for event in learning_events
            if event.user_id == user_id and event.course_id == course_id
        ]
        
        if not user_events:
            return 0.0
        
        # Factor in session frequency, completion rate, and time spent
        total_events = len(user_events)
        completion_events = len([e for e in user_events if e.event_type == LearningEventType.LESSON_COMPLETE])
        
        completion_rate = completion_events / max(total_events, 1)
        
        # Simple engagement calculation (can be enhanced with more sophisticated algorithms)
        return min(completion_rate * 1.2, 1.0)
    else:
        # Production mode: Use database queries for comprehensive analysis
        # Implementation would include more sophisticated engagement metrics
        return 0.0


# API Endpoints

@app.get("/", summary="Service Health Check")
async def root():
    """Service health check endpoint"""
    mode = "no-database-development" if NO_DATABASE_MODE else "production-database"
    return {
        "service": "CogniFlow Learning Analytics Service",
        "status": "operational",
        "version": "1.0.0",
        "mode": mode,
        "total_events": len(learning_events) if NO_DATABASE_MODE else "database-managed"
    }


@app.post("/events", summary="Record Learning Event")
async def record_learning_event(event_request: LearningEventRequest):
    """
    Record a learning event for analytics tracking
    
    This endpoint serves as the central event bus for the CogniFlow platform.
    All services can send learning events here for comprehensive analytics.
    """
    try:
        # Convert request to event dict
        event_data = {
            "user_id": event_request.user_id,
            "event_type": event_request.event_type.value,
            "event_data": {
                "course_id": event_request.course_id,
                "lesson_id": event_request.lesson_id,
                **event_request.event_data
            },
            "timestamp": event_request.timestamp
        }
        
        # Record event using store
        analytics_store.record_event(event_data)
        
        return {
            "status": "success",
            "message": "Event recorded successfully",
            "event_type": event_request.event_type.value,
            "timestamp": event_request.timestamp.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error recording event: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to record event: {str(e)}")


@app.post("/events/batch", summary="Record Multiple Learning Events")
async def record_batch_events(events: List[LearningEventRequest]):
    """
    Record multiple learning events in a single batch operation
    
    This endpoint is optimized for high-throughput scenarios where multiple
    learning events need to be recorded efficiently.
    """
    if not events:
        raise HTTPException(status_code=400, detail="No events provided")
    
    if len(events) > 100:  # Reasonable batch size limit
        raise HTTPException(status_code=400, detail="Batch size cannot exceed 100 events")
    
    results = []
    successful_events = 0
    failed_events = 0
    
    for i, event_request in enumerate(events):
        try:
            event_data = {
                "user_id": event_request.user_id,
                "event_type": event_request.event_type.value,
                "event_data": {
                    "course_id": event_request.course_id,
                    "lesson_id": event_request.lesson_id,
                    **event_request.event_data
                },
                "timestamp": event_request.timestamp
            }
            
            analytics_store.record_event(event_data)
            
            results.append({
                "index": i,
                "status": "success",
                "event_type": event_request.event_type.value
            })
            successful_events += 1
                
        except Exception as e:
            results.append({
                "index": i,
                "status": "error", 
                "message": str(e)
            })
            failed_events += 1
    
    return {
        "batch_results": {
            "total_events": len(events),
            "successful": successful_events,
            "failed": failed_events,
            "success_rate": successful_events / len(events) if events else 0.0
        },
        "individual_results": results
    }


@app.get("/analytics/user/{user_id}", summary="Get User Learning Analytics")
async def get_user_analytics_endpoint(user_id: str):
    """Get comprehensive analytics for a specific user"""
    try:
        analytics = analytics_store.get_user_analytics(user_id)
        
        if not analytics:
            raise HTTPException(status_code=404, detail="No analytics data found for user")
        
        return {
            "status": "success",
            "analytics": analytics,
            "generated_at": datetime.datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analytics: {str(e)}")


@app.get("/analytics/course/{course_id}", summary="Get Course Analytics")
async def get_course_analytics_endpoint(course_id: str):
    """Get comprehensive analytics for a specific course"""
    try:
        analytics = analytics_store.get_course_analytics(course_id)
        
        if not analytics:
            raise HTTPException(status_code=404, detail="No analytics data found for course")
        
        return {
            "status": "success",
            "analytics": analytics,
            "generated_at": datetime.datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting course analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analytics: {str(e)}")


@app.get("/analytics/system", summary="Get System-Wide Analytics")
async def get_system_analytics_endpoint():
    """Get comprehensive system-wide analytics"""
    try:
        analytics = analytics_store.get_system_analytics()
        
        return {
            "status": "success",
            "analytics": analytics,
            "mode": "development" if NO_DATABASE_MODE else "production"
        }
        
    except Exception as e:
        logger.error(f"Error getting system analytics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analytics: {str(e)}")


@app.get("/events/user/{user_id}", summary="Get User Events")
async def get_user_events(
    user_id: str, 
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    limit: int = Query(100, description="Maximum number of events to return")
):
    """Get events for a specific user"""
    try:
        events = analytics_store.get_user_events(user_id, event_type, limit)
        
        return {
            "status": "success",
            "user_id": user_id,
            "event_count": len(events),
            "events": events,
            "filters_applied": {
                "event_type": event_type,
                "limit": limit
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting user events: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve events: {str(e)}")


@app.get("/events/system", summary="Get System Events")
async def get_system_events(
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    limit: int = Query(100, description="Maximum number of events to return")
):
    """Get system-wide events"""
    try:
        events = analytics_store.get_system_events(event_type, limit)
        
        return {
            "status": "success",
            "event_count": len(events),
            "events": events,
            "filters_applied": {
                "event_type": event_type,
                "limit": limit
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting system events: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve events: {str(e)}")


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "learning-analytics-service", 
        "timestamp": datetime.datetime.now().isoformat(),
        "mode": "development" if NO_DATABASE_MODE else "production",
        "store_type": "InMemoryAnalyticsStore" if NO_DATABASE_MODE else "PostgreSQLAnalyticsStore"
    }


# Add imports for integration functionality
from integrations import service_integrations, initialize_integrations, cleanup_integrations

# Enhanced API endpoints

@app.get("/progress/{user_id}/{course_id}/enriched", 
         summary="Get Enriched Course Progress")
async def get_enriched_course_progress(user_id: str, course_id: str):
    """
    Retrieve comprehensive learning progress with enriched context data
    
    This endpoint provides detailed progress information by integrating data
    from the Users Service and Courses Service, offering a complete view of
    the learning experience.
    """
    if NO_DATABASE_MODE:
        try:
            # Get user analytics from our store
            user_analytics = analytics_store.get_user_analytics(user_id)
            course_analytics = analytics_store.get_course_analytics(course_id)
            
            # Create basic progress response
            basic_progress = {
                "user_id": user_id,
                "course_id": course_id,
                "course_title": f"Course {course_id}",
                "overall_progress_percentage": user_analytics.get("performance", {}).get("completion_rate", 0) * 100,
                "total_time_spent_minutes": user_analytics.get("real_time_metrics", {}).get("total_study_time", 0),
                "lessons_completed": user_analytics.get("real_time_metrics", {}).get("lessons_completed", 0),
                "total_lessons": 10,  # Default for demo
                "completion_status": "in_progress" if user_analytics else "not_started",
                "last_accessed": datetime.datetime.now()
            }
            
            # Enrich the data using service integrations
            enriched_progress = await service_integrations.get_enriched_progress_data(
                user_id, course_id, basic_progress
            )
            
            return {
                "status": "success",
                "data": enriched_progress,
                "enrichment_applied": True,
                "timestamp": datetime.datetime.now().isoformat()
            }            
        except HTTPException as e:
            if e.status_code == 404:
                # No basic progress found, but still provide enriched context
                try:
                    course_requirements = await service_integrations.course_integration.get_course_completion_requirements(course_id)
                    user_preferences = await service_integrations.user_integration.get_user_learning_preferences(user_id)
                    
                    return {
                        "status": "no_progress_found",
                        "data": {
                            "user_id": user_id,
                            "course_id": course_id,
                            "course_title": course_requirements.get("course_title", f"Course {course_id}"),
                            "total_lessons": course_requirements.get("total_lessons", 0),
                            "estimated_duration_hours": course_requirements.get("estimated_duration_hours", 0),
                            "user_preferences": user_preferences,
                            "overall_progress_percentage": 0.0,
                            "completion_status": "not_started",
                            "recommendations": [
                                {
                                    "type": "getting_started",
                                    "title": "Start Your Learning Journey",
                                    "message": "Begin with the first lesson to start tracking your progress!",
                                    "priority": "high"
                                }
                            ]
                        },
                        "enrichment_applied": True,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                except Exception as integration_error:
                    logger.error(f"Integration error: {integration_error}")
                    return {
                        "status": "no_progress_found",
                        "data": {
                            "user_id": user_id,
                            "course_id": course_id,
                            "course_title": f"Course {course_id}",
                            "overall_progress_percentage": 0.0,
                            "completion_status": "not_started",
                            "message": "Start your learning journey!"
                        },
                        "enrichment_applied": False,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
            else:
                raise e
                
        except Exception as e:
            logger.error(f"Error getting enriched progress: {e}")
            raise HTTPException(status_code=500, detail="Error retrieving enriched progress data")
    else:
        # Production mode implementation
        raise HTTPException(status_code=501, detail="Production database mode not implemented")


@app.get("/analytics/platform", summary="Get Platform-Wide Analytics")
async def get_platform_analytics():
    """
    Retrieve comprehensive platform-wide learning analytics
    
    This endpoint aggregates data across all services to provide insights into:
    - Overall platform usage patterns
    - Popular courses and content
    - Learning effectiveness metrics
    - User engagement trends
    - System performance indicators
    """
    try:
        # Get system analytics from our store
        system_analytics = analytics_store.get_system_analytics()
        
        # Attempt to get platform data from integrations
        try:
            platform_data = await service_integrations.get_platform_wide_analytics()
            system_analytics.update(platform_data)
        except Exception as integration_error:
            logger.warning(f"Integration error for platform analytics: {integration_error}")
        
        if NO_DATABASE_MODE:
            # Enhance with development mode specific data
            system_analytics.update({
                "mode": "development",
                "data_source": "simulated",
                "note": "This is development data. Production deployment will show real metrics."
            })
        
        return {
            "status": "success",
            "analytics": system_analytics,
            "generated_at": datetime.datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating platform analytics: {e}")
        raise HTTPException(status_code=500, detail="Error generating platform analytics")


@app.post("/progress", summary="Update Learning Progress")
async def update_learning_progress(progress_request: ProgressUpdateRequest):
    """Update learning progress for a user"""
    try:
        # Convert progress request to event
        event_data = {
            "user_id": progress_request.user_id,
            "event_type": "progress_updated",
            "event_data": {
                "course_id": progress_request.course_id,
                "lesson_id": progress_request.lesson_id,
                "completion_percentage": progress_request.completion_percentage,
                "time_spent_minutes": progress_request.time_spent_minutes,
                "difficulty_rating": progress_request.difficulty_rating.value if progress_request.difficulty_rating else None,
                "notes": progress_request.notes
            },
            "timestamp": datetime.datetime.now()
        }
        
        # Record the progress update as an event
        analytics_store.record_event(event_data)
        
        return {
            "status": "success",
            "message": "Progress updated successfully",
            "user_id": progress_request.user_id,
            "course_id": progress_request.course_id,
            "lesson_id": progress_request.lesson_id
        }
        
    except Exception as e:
        logger.error(f"Error updating progress: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update progress: {str(e)}")


@app.post("/sessions", summary="Record Learning Session")
async def record_learning_session(session_request: LearningSessionRequest):
    """Record a learning session"""
    try:
        # Convert session to event
        event_data = {
            "user_id": session_request.user_id,
            "event_type": "session_recorded",
            "event_data": {
                "course_id": session_request.course_id,
                "session_start": session_request.session_start.isoformat(),
                "session_end": session_request.session_end.isoformat() if session_request.session_end else None,
                "lessons_accessed": session_request.lessons_accessed,
                "total_engagement_score": session_request.total_engagement_score
            },
            "timestamp": session_request.session_start
        }
        
        # Record the session as an event
        analytics_store.record_event(event_data)
        
        return {
            "status": "success",
            "message": "Session recorded successfully",
            "session_data": {
                "user_id": session_request.user_id,
                "course_id": session_request.course_id,
                "duration": (session_request.session_end - session_request.session_start).total_seconds() / 60 if session_request.session_end else None
            }
        }
        
    except Exception as e:
        logger.error(f"Error recording session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to record session: {str(e)}")


# Simple Event Model for cross-service communication
class SimpleEventRequest(BaseModel):
    """Simplified event model for cross-service communication"""
    user_id: str
    event_type: str
    event_data: Dict[str, Any] = {}
    timestamp: str = datetime.datetime.now().isoformat()
    service: str = "unknown"

@app.post("/events/simple", summary="Record Simple Learning Event")
async def record_simple_event(event: SimpleEventRequest):
    """
    Record a learning event with simplified format for cross-service communication
    
    This endpoint accepts events from other services in a simplified JSON format.
    """
    try:
        # Convert to internal format and record
        event_data = {
            "user_id": event.user_id,
            "event_type": event.event_type,
            "event_data": event.event_data,
            "timestamp": datetime.datetime.fromisoformat(event.timestamp.replace('Z', '+00:00')) if event.timestamp else datetime.datetime.now(),
            "service": event.service
        }
        
        analytics_store.record_event(event_data)
        
        return {
            "status": "success",
            "message": "Event recorded successfully",
            "event_type": event.event_type
        }
        
    except Exception as e:
        logger.error(f"Error recording simple event: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to record event: {str(e)}")


# Startup and shutdown event handlers
@app.on_event("startup")
async def startup_event():
    """Initialize integrations and services on startup"""
    logger.info("Learning Analytics Service starting up...")
    try:
        await initialize_integrations()
        logger.info("Service integrations initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing integrations: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up integrations and services on shutdown"""
    logger.info("Learning Analytics Service shutting down...")
    try:
        await cleanup_integrations()
        logger.info("Service integrations cleaned up successfully")
    except Exception as e:
        logger.error(f"Error cleaning up integrations: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
