# services/courses-service/main.py
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

# Helper function to fire analytics events
async def fire_analytics_event(event_type: str, user_id: str, metadata: dict):
    """Fire an event to the learning analytics service"""
    try:
        event_data = {
            "event_type": event_type,
            "user_id": user_id,
            "metadata": metadata,
            "timestamp": datetime.datetime.now().isoformat(),
            "service": "courses"
        }
        
        # For now, just log the event (in production, make HTTP call)
        print(f"Analytics Event: {event_data}")
        
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
            category="Programming",
            estimated_duration_hours=35,
            created_at=datetime.datetime.now() - datetime.timedelta(days=60),
            updated_at=datetime.datetime.now() - datetime.timedelta(days=5),
            enrollment_count=89,
            rating=4.9,
            tags=["Python", "Programming", "Advanced", "Development"]
        ),
        Course(
            id=3,
            title="Data Science Fundamentals",
            description="Learn the core concepts of data science including statistics, data visualization, and exploratory data analysis.",
            instructor_id=2,
            difficulty=DifficultyLevel.INTERMEDIATE,
            status=CourseStatus.PUBLISHED,
            category="Data Science",
            estimated_duration_hours=25,
            created_at=datetime.datetime.now() - datetime.timedelta(days=30),
            updated_at=datetime.datetime.now() - datetime.timedelta(days=2),
            enrollment_count=234,
            rating=4.6,
            tags=["Data Science", "Statistics", "Visualization", "Analytics"]
        ),
        Course(
            id=4,
            title="Introduction to Web Development",
            description="Start your journey in web development with HTML, CSS, JavaScript, and modern frameworks.",
            instructor_id=2,
            difficulty=DifficultyLevel.BEGINNER,
            status=CourseStatus.DRAFT,
            category="Web Development",
            estimated_duration_hours=30,
            created_at=datetime.datetime.now() - datetime.timedelta(days=15),
            updated_at=datetime.datetime.now() - datetime.timedelta(days=1),
            enrollment_count=0,
            rating=0.0,
            tags=["Web Development", "HTML", "CSS", "JavaScript", "Frontend"]
        ),
    ]

    db_lessons = [
        # Lessons for AI Course (Course ID: 1)
        Lesson(id=1, title="What is Artificial Intelligence?", type=LessonType.VIDEO, 
               content_url="/content/ai-intro-video.mp4", description="Overview of AI and its history", 
               duration_minutes=15, order=1),
        Lesson(id=2, title="Types of Machine Learning", type=LessonType.TEXT, 
               content_url="/content/ml-types.html", description="Supervised, unsupervised, and reinforcement learning", 
               duration_minutes=20, order=2),
        Lesson(id=3, title="AI Knowledge Check", type=LessonType.QUIZ, 
               content_url="/quiz/ai-basics", description="Test your understanding of AI fundamentals", 
               duration_minutes=10, order=3),
        
        # Lessons for Python Course (Course ID: 2)
        Lesson(id=4, title="Advanced Python Decorators", type=LessonType.VIDEO, 
               content_url="/content/python-decorators.mp4", description="Master Python decorators", 
               duration_minutes=25, order=1),
        Lesson(id=5, title="Context Managers and With Statement", type=LessonType.INTERACTIVE, 
               content_url="/interactive/context-managers", description="Learn context managers with hands-on exercises", 
               duration_minutes=30, order=2),
        
        # Lessons for Data Science Course (Course ID: 3)
        Lesson(id=6, title="Introduction to Statistics", type=LessonType.TEXT, 
               content_url="/content/stats-intro.html", description="Basic statistical concepts", 
               duration_minutes=18, order=1),
        Lesson(id=7, title="Data Visualization with Python", type=LessonType.SIMULATION, 
               content_url="/simulation/data-viz", description="Interactive data visualization exercises", 
               duration_minutes=35, order=2),
    ]

    db_enrollments = [
        Enrollment(
            id=1, user_id=1, course_id=1, 
            enrolled_at=datetime.datetime.now() - datetime.timedelta(days=10),
            progress_percentage=60.0, completed_lessons=[1, 2],
            last_accessed=datetime.datetime.now() - datetime.timedelta(hours=2)
        ),
        Enrollment(
            id=2, user_id=1, course_id=3, 
            enrolled_at=datetime.datetime.now() - datetime.timedelta(days=5),
            progress_percentage=25.0, completed_lessons=[6],
            last_accessed=datetime.datetime.now() - datetime.timedelta(hours=6)
        ),
    ]

    class InMemoryCourseStore:
        """
        In-memory course, lesson, and enrollment store for development mode.
        Production implementation would use PostgreSQL for persistence and Redis for caching.
        """
        def __init__(self):
            self.courses = []
            self.lessons = []
            self.enrollments = []
            self._init_sample_data()

        def _init_sample_data(self):
            # Add sample courses, lessons, and enrollments for dev mode
            pass  # Already initialized in db_courses, db_lessons, db_enrollments above

        def get_courses(self):
            return self.courses

        def get_course(self, course_id):
            for c in self.courses:
                if c.id == course_id:
                    return c
            return None

        def get_lessons(self, course_id):
            return [l for l in self.lessons if l.course_id == course_id]

        def enroll_user(self, user_id, course_id):
            # Add enrollment logic
            pass

        # ... more methods as needed ...

    course_store = InMemoryCourseStore()

    # --- Production-ready code (PostgreSQL/Redis) ---
    # class ProductionCourseStore:
    #     """
    #     Production-ready course store using PostgreSQL and Redis.
    #     - Use SQLAlchemy ORM for course/lesson/enrollment models
    #     - Use Redis for caching
    #     - Implement proper transactional logic and error handling
    #     """
    #     def __init__(self, db: Session, redis_client):
    #         self.db = db
    #         self.redis = redis_client
    #     ...
    # course_store = ProductionCourseStore(...)
    #
    # All endpoints should use the appropriate store (course_store) based on NO_DATABASE_MODE.
    #
    # This modular approach ensures rapid development and easy migration to production.

    @app.get("/", summary="Service Health Check")
    async def root():
        return {
            "service": "CogniFlow Courses Service",
            "status": "running",
            "version": "1.0.0",
            "total_courses": len(db_courses),
            "published_courses": len([c for c in db_courses if c.status == CourseStatus.PUBLISHED])
        }

    # --- Expanded Endpoints for Courses Service (No-DB Mode) ---
    @app.get("/courses/", response_model=List[Course], summary="Get all courses")
    def get_courses(status: Optional[CourseStatus] = None, difficulty: Optional[DifficultyLevel] = None, category: Optional[str] = None, limit: int = Query(default=10, le=100)):
        """
        List all courses with optional filtering by status, difficulty, and category.
        """
        results = db_courses
        if status:
            results = [c for c in results if c.status == status]
        if difficulty:
            results = [c for c in results if c.difficulty == difficulty]
        if category:
            results = [c for c in results if c.category == category]
        return results[:limit]

    @app.get("/courses/{course_id}", response_model=CourseWithLessons, summary="Get course by ID")
    def get_course(course_id: int):
        """
        Get course details and lessons by course ID.
        """
        course = next((c for c in db_courses if c.id == course_id), None)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        lessons = [l for l in db_lessons if l.course_id == course_id]
        return CourseWithLessons(**course.dict(), lessons=lessons)

    @app.get("/courses/{course_id}/lessons", response_model=List[Lesson], summary="Get course lessons")
    def get_course_lessons(course_id: int):
        """
        Get all lessons for a course.
        """
        return [l for l in db_lessons if l.course_id == course_id]

    @app.post("/courses/{course_id}/enroll/{user_id}", response_model=Enrollment, summary="Enroll user in course")
    def enroll_user(course_id: int, user_id: int):
        """
        Enroll a user in a course (in-memory only).
        """
        enrollment = Enrollment(
            id=len(db_enrollments) + 1,
            user_id=user_id,
            course_id=course_id,
            enrolled_at=datetime.datetime.now(),
            progress_percentage=0.0,
            completed_lessons=[],
            last_accessed=datetime.datetime.now()
        )
        db_enrollments.append(enrollment)
        return enrollment

    @app.get("/users/{user_id}/enrollments", response_model=List[Enrollment], summary="Get user enrollments")
    def get_user_enrollments(user_id: int):
        """
        Get all enrollments for a user.
        """
        return [e for e in db_enrollments if e.user_id == user_id]

    @app.get("/users/{user_id}/courses/{course_id}/progress", response_model=CourseProgress, summary="Get course progress")
    def get_course_progress(user_id: int, course_id: int):
        """
        Get progress for a user in a specific course.
        """
        enrollment = next((e for e in db_enrollments if e.user_id == user_id and e.course_id == course_id), None)
        if not enrollment:
            raise HTTPException(status_code=404, detail="Enrollment not found")
        return CourseProgress(
            user_id=user_id,
            course_id=course_id,
            progress_percentage=enrollment.progress_percentage,
            completed_lessons=enrollment.completed_lessons,
            last_accessed=enrollment.last_accessed
        )

    @app.get("/categories/", response_model=List[str], summary="Get all course categories")
    def get_categories():
        """
        List all unique course categories.
        """
        return list(set(c.category for c in db_courses))

    # --- Advanced Features (No-DB Mode) ---
    @app.post("/courses/", response_model=Course, summary="Create a new course")
    def create_course(course: Course):
        """
        Create a new course (in-memory only).
        """
        db_courses.append(course)
        return course

    @app.post("/courses/{course_id}/lessons", response_model=Lesson, summary="Add lesson to course")
    def add_lesson(course_id: int, lesson: Lesson):
        """
        Add a lesson to a course (in-memory only).
        """
        db_lessons.append(lesson)
        return lesson

    @app.delete("/courses/{course_id}", summary="Delete a course")
    def delete_course(course_id: int):
        """
        Delete a course (in-memory only).
        """
        global db_courses
        db_courses = [c for c in db_courses if c.id != course_id]
        return {"detail": "Course deleted."}

    # --- Production-ready code (PostgreSQL/Redis) ---
    # @app.get("/courses/", ...)
    # def get_courses(..., db: Session = Depends(get_db)):
    #     ...
    # @app.post("/courses/", ...)
    # def create_course(..., db: Session = Depends(get_db)):
    #     ...
# ...existing code...
```
