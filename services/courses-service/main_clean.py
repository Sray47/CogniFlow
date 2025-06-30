"""
CogniFlow Courses Service

This service manages course content, enrollment, and progress tracking.
Supports both development mode (in-memory storage) and production mode (database).

Key Features:
- Course catalog management
- User enrollment and progress tracking
- Lesson completion tracking
- Course analytics and recommendations
- Instructor management

Author: CogniFlow Development Team
Version: 1.0.0
"""

import os
import asyncio
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import datetime
from enum import Enum

# Import our store abstraction
from store import InMemoryCourseStore, CourseStoreInterface, DifficultyLevel, CourseStatus, LessonType

NO_DATABASE_MODE = os.getenv("NO_DATABASE_MODE", "true").lower() == "true"

app = FastAPI(
    title="CogniFlow Courses Service", 
    description="Professional course management and enrollment system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class Lesson(BaseModel):
    id: int
    title: str
    type: LessonType
    content_url: Optional[str] = None
    description: str
    duration_minutes: int
    order: int

class Course(BaseModel):
    id: int
    title: str
    description: str
    instructor_id: str
    instructor_name: str
    difficulty: DifficultyLevel
    status: CourseStatus
    category: str
    estimated_duration_hours: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    enrollment_count: int = 0
    rating: float = 0.0
    total_ratings: int = 0
    tags: List[str] = []
    price: float = 0.0
    image_url: Optional[str] = None

class CourseWithLessons(Course):
    lessons: List[Lesson] = []

class EnrollmentRequest(BaseModel):
    user_id: str
    course_id: int

class EnrollmentResponse(BaseModel):
    id: str
    user_id: str
    course_id: int
    enrolled_at: datetime.datetime
    status: str

class LessonProgressRequest(BaseModel):
    user_id: str
    course_id: int
    lesson_id: int

class CourseProgressResponse(BaseModel):
    user_id: str
    course_id: int
    progress_percentage: float
    completed_lessons: List[int]
    total_lessons: int
    current_lesson_id: Optional[int]
    time_spent_minutes: int
    last_updated: datetime.datetime

# Initialize store
if NO_DATABASE_MODE:
    course_store = InMemoryCourseStore()
else:
    # Production mode would initialize database connections
    course_store = None

# Analytics service URL
ANALYTICS_SERVICE_URL = os.getenv("ANALYTICS_SERVICE_URL", "http://learning-analytics:8000")

# Helper function to fire analytics events
async def fire_analytics_event(event_type: str, user_id: str, metadata: dict):
    """Fire an event to the learning analytics service"""
    try:
        event_data = {
            "event_type": event_type,
            "user_id": user_id,
            "event_data": metadata,
            "timestamp": datetime.datetime.now().isoformat(),
            "service": "courses"
        }
        # Try to send to analytics service, fallback to logging
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{ANALYTICS_SERVICE_URL}/events/simple", 
                    json=event_data,
                    timeout=5.0
                )
                if response.status_code == 200:
                    print(f"✅ Analytics Event Sent: {event_type}")
                else:
                    print(f"⚠️ Analytics Event Failed: {response.status_code}")
        except Exception:
            # Fallback to logging if analytics service is not available
            print(f"📊 Analytics Event (Local): {event_data}")
        
    except Exception as e:
        print(f"Failed to fire analytics event: {e}")

# --- API Endpoints ---

@app.get("/", summary="Service Health Check")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "CogniFlow Courses Service",
        "version": "1.0.0",
        "status": "healthy",
        "description": "Professional course management and enrollment system",
        "mode": "development" if NO_DATABASE_MODE else "production"
    }

@app.get("/courses/", response_model=List[Course], summary="Get all courses")
async def get_courses(
    status: Optional[str] = Query(None, description="Filter by course status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty level")
):
    """Get all courses with optional filtering"""
    try:
        if NO_DATABASE_MODE:
            courses = course_store.get_all_courses(status=status, category=category, difficulty=difficulty)
        else:
            # Production: Query database
            courses = []
        
        return courses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching courses: {str(e)}")

@app.get("/courses/{course_id}", response_model=CourseWithLessons, summary="Get course by ID")
async def get_course(course_id: int):
    """Get a specific course with its lessons"""
    try:
        if NO_DATABASE_MODE:
            course = course_store.get_course(course_id)
        else:
            # Production: Query database
            course = None
        
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        return course
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching course: {str(e)}")

@app.post("/courses/{course_id}/enroll", response_model=EnrollmentResponse, summary="Enroll in a course")
async def enroll_in_course(course_id: int, request: EnrollmentRequest, background_tasks: BackgroundTasks):
    """Enroll a user in a course"""
    try:
        # Validate that course_id matches request
        if course_id != request.course_id:
            raise HTTPException(status_code=400, detail="Course ID mismatch")
        
        if NO_DATABASE_MODE:
            enrollment = course_store.enroll_user(request.user_id, request.course_id)
        else:
            # Production: Create enrollment in database
            enrollment = {}
        
        # Fire analytics event
        background_tasks.add_task(
            fire_analytics_event,
            "COURSE_ENROLLMENT",
            request.user_id,
            {"course_id": request.course_id}
        )
        
        return enrollment
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error enrolling in course: {str(e)}")

@app.get("/users/{user_id}/enrollments", summary="Get user enrollments")
async def get_user_enrollments(user_id: str):
    """Get all enrollments for a user"""
    try:
        if NO_DATABASE_MODE:
            enrollments = course_store.get_user_enrollments(user_id)
        else:
            # Production: Query database
            enrollments = []
        
        return enrollments
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching enrollments: {str(e)}")

@app.post("/users/{user_id}/progress/{course_id}/lessons/{lesson_id}", response_model=CourseProgressResponse, summary="Complete a lesson")
async def complete_lesson(user_id: str, course_id: int, lesson_id: int, background_tasks: BackgroundTasks):
    """Mark a lesson as completed and update course progress"""
    try:
        if NO_DATABASE_MODE:
            progress = course_store.update_lesson_progress(user_id, course_id, lesson_id)
        else:
            # Production: Update database
            progress = {}
        
        # Fire analytics event
        background_tasks.add_task(
            fire_analytics_event,
            "LESSON_COMPLETED",
            user_id,
            {
                "course_id": course_id,
                "lesson_id": lesson_id,
                "progress_percentage": progress.get("progress_percentage", 0)
            }
        )
        
        # Check if course is completed
        if progress.get("progress_percentage", 0) >= 100:
            background_tasks.add_task(
                fire_analytics_event,
                "COURSE_COMPLETED",
                user_id,
                {"course_id": course_id}
            )
        
        return progress
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating lesson progress: {str(e)}")

@app.get("/users/{user_id}/progress/{course_id}", response_model=CourseProgressResponse, summary="Get course progress")
async def get_course_progress(user_id: str, course_id: int):
    """Get detailed progress for a specific course"""
    try:
        if NO_DATABASE_MODE:
            progress = course_store.get_course_progress(user_id, course_id)
        else:
            # Production: Query database
            progress = {}
        
        return progress
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching course progress: {str(e)}")

@app.get("/courses/{course_id}/analytics", summary="Get course analytics")
async def get_course_analytics(course_id: int):
    """Get analytics for a specific course"""
    try:
        if NO_DATABASE_MODE:
            analytics = course_store.get_course_analytics(course_id)
        else:
            # Production: Query database
            analytics = {}
        
        return analytics
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching course analytics: {str(e)}")

@app.get("/categories", summary="Get course categories")
async def get_categories():
    """Get all available course categories"""
    try:
        if NO_DATABASE_MODE:
            courses = course_store.get_all_courses()
            categories = list(set(course["category"] for course in courses))
            categories.sort()
        else:
            # Production: Query database
            categories = []
        
        return {"categories": categories}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching categories: {str(e)}")

@app.get("/popular", response_model=List[Course], summary="Get popular courses")
async def get_popular_courses(limit: int = Query(10, description="Number of courses to return")):
    """Get most popular courses based on enrollment count"""
    try:
        if NO_DATABASE_MODE:
            courses = course_store.get_all_courses(status="published")
            # Already sorted by enrollment count in get_all_courses
            popular_courses = courses[:limit]
        else:
            # Production: Query database with ordering
            popular_courses = []
        
        return popular_courses
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching popular courses: {str(e)}")

@app.get("/health", summary="Health check")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "courses",
        "version": "1.0.0",
        "timestamp": datetime.datetime.now().isoformat(),
        "mode": "development" if NO_DATABASE_MODE else "production"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
