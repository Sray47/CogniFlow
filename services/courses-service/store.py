"""
Courses Service - Data Store Abstraction
=========================================

This module provides data storage abstraction for the Courses service.
In development mode, it uses in-memory storage.
In production mode, it can be swapped with PostgreSQL implementations.

Key Features:
- Course management and enrollment
- Lesson progress tracking
- Course analytics and ratings
- Instructor management
"""

import datetime
import random
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod
from enum import Enum


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class CourseStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class LessonType(str, Enum):
    VIDEO = "video"
    TEXT = "text"
    QUIZ = "quiz"
    INTERACTIVE = "interactive"
    SIMULATION = "simulation"


class CourseStoreInterface(ABC):
    """Abstract interface for Course data storage"""
    
    @abstractmethod
    def get_course(self, course_id: int) -> Optional[dict]:
        pass
    
    @abstractmethod
    def get_all_courses(self, status: Optional[str] = None) -> List[dict]:
        pass
    
    @abstractmethod
    def enroll_user(self, user_id: str, course_id: int) -> dict:
        pass
    
    @abstractmethod
    def get_user_enrollments(self, user_id: str) -> List[dict]:
        pass
    
    @abstractmethod
    def update_lesson_progress(self, user_id: str, course_id: int, lesson_id: int) -> dict:
        pass
    
    @abstractmethod
    def get_course_progress(self, user_id: str, course_id: int) -> dict:
        pass


class InMemoryCourseStore(CourseStoreInterface):
    """
    In-memory implementation of Course store for development mode.
    
    Features:
    - Course and lesson management
    - User enrollment tracking
    - Progress tracking and analytics
    - Rating and review system
    """
    
    def __init__(self):
        # Core data structures
        self.courses = {}  # course_id -> course data
        self.lessons = {}  # course_id -> list of lessons
        self.enrollments = {}  # (user_id, course_id) -> enrollment data
        self.progress = {}  # (user_id, course_id) -> progress data
        self.user_enrollments = {}  # user_id -> list of course_ids
        
        # Initialize sample data
        self._init_sample_data()
    
    def _init_sample_data(self):
        """Initialize with comprehensive sample data for demo purposes"""
        
        # Sample courses
        courses_data = [
            {
                "id": 1,
                "title": "Introduction to Artificial Intelligence",
                "description": "A comprehensive beginner's guide to AI concepts, machine learning, and their applications in modern technology.",
                "instructor_id": "instructor1",
                "instructor_name": "Dr. Sarah Chen",
                "difficulty": DifficultyLevel.BEGINNER,
                "status": CourseStatus.PUBLISHED,
                "category": "Technology",
                "estimated_duration_hours": 20,
                "created_at": datetime.datetime.now() - datetime.timedelta(days=45),
                "updated_at": datetime.datetime.now() - datetime.timedelta(days=10),
                "enrollment_count": 156,
                "rating": 4.7,
                "total_ratings": 89,
                "tags": ["AI", "Machine Learning", "Technology", "Beginner"],
                "price": 0,  # Free course
                "image_url": "/images/courses/ai-intro.jpg"
            },
            {
                "id": 2,
                "title": "Advanced Python Programming",
                "description": "Deep dive into Python's advanced features, design patterns, and best practices for professional development.",
                "instructor_id": "instructor2",
                "instructor_name": "Prof. Alex Rodriguez",
                "difficulty": DifficultyLevel.ADVANCED,
                "status": CourseStatus.PUBLISHED,
                "category": "Programming",
                "estimated_duration_hours": 35,
                "created_at": datetime.datetime.now() - datetime.timedelta(days=60),
                "updated_at": datetime.datetime.now() - datetime.timedelta(days=5),
                "enrollment_count": 89,
                "rating": 4.9,
                "total_ratings": 67,
                "tags": ["Python", "Programming", "Advanced", "Development"],
                "price": 49.99,
                "image_url": "/images/courses/python-advanced.jpg"
            },
            {
                "id": 3,
                "title": "Data Science Fundamentals",
                "description": "Learn the core concepts of data science including statistics, data visualization, and exploratory data analysis.",
                "instructor_id": "instructor3",
                "instructor_name": "Dr. Maria Gonzalez",
                "difficulty": DifficultyLevel.INTERMEDIATE,
                "status": CourseStatus.PUBLISHED,
                "category": "Data Science",
                "estimated_duration_hours": 25,
                "created_at": datetime.datetime.now() - datetime.timedelta(days=30),
                "updated_at": datetime.datetime.now() - datetime.timedelta(days=2),
                "enrollment_count": 234,
                "rating": 4.6,
                "total_ratings": 156,
                "tags": ["Data Science", "Statistics", "Visualization", "Analytics"],
                "price": 39.99,
                "image_url": "/images/courses/data-science.jpg"
            },
            {
                "id": 4,
                "title": "Introduction to Web Development",
                "description": "Start your journey in web development with HTML, CSS, JavaScript, and modern frameworks.",
                "instructor_id": "instructor1",
                "instructor_name": "Dr. Sarah Chen",
                "difficulty": DifficultyLevel.BEGINNER,
                "status": CourseStatus.PUBLISHED,
                "category": "Web Development",
                "estimated_duration_hours": 30,
                "created_at": datetime.datetime.now() - datetime.timedelta(days=15),
                "updated_at": datetime.datetime.now() - datetime.timedelta(days=1),
                "enrollment_count": 67,
                "rating": 4.5,
                "total_ratings": 34,
                "tags": ["Web Development", "HTML", "CSS", "JavaScript", "Frontend"],
                "price": 29.99,
                "image_url": "/images/courses/web-dev.jpg"
            },
            {
                "id": 5,
                "title": "Machine Learning Masterclass",
                "description": "Advanced machine learning concepts, algorithms, and practical implementation with real-world projects.",
                "instructor_id": "instructor2",
                "instructor_name": "Prof. Alex Rodriguez",
                "difficulty": DifficultyLevel.ADVANCED,
                "status": CourseStatus.PUBLISHED,
                "category": "Machine Learning",
                "estimated_duration_hours": 45,
                "created_at": datetime.datetime.now() - datetime.timedelta(days=20),
                "updated_at": datetime.datetime.now() - datetime.timedelta(days=3),
                "enrollment_count": 45,
                "rating": 4.8,
                "total_ratings": 28,
                "tags": ["Machine Learning", "AI", "Advanced", "Projects"],
                "price": 79.99,
                "image_url": "/images/courses/ml-masterclass.jpg"
            }
        ]
        
        for course in courses_data:
            self.courses[course["id"]] = course
        
        # Sample lessons for each course
        lessons_data = {
            1: [  # AI Course
                {"id": 1, "title": "What is Artificial Intelligence?", "type": LessonType.VIDEO, 
                 "content_url": "/content/ai-intro-video.mp4", "description": "Overview of AI and its history", 
                 "duration_minutes": 15, "order": 1},
                {"id": 2, "title": "Types of Machine Learning", "type": LessonType.TEXT, 
                 "content_url": "/content/ml-types.html", "description": "Supervised, unsupervised, and reinforcement learning", 
                 "duration_minutes": 20, "order": 2},
                {"id": 3, "title": "AI Knowledge Check", "type": LessonType.QUIZ, 
                 "content_url": "/quiz/ai-basics", "description": "Test your understanding of AI fundamentals", 
                 "duration_minutes": 10, "order": 3},
                {"id": 4, "title": "Real-world AI Applications", "type": LessonType.INTERACTIVE, 
                 "content_url": "/interactive/ai-apps", "description": "Explore how AI is used in various industries", 
                 "duration_minutes": 25, "order": 4},
            ],
            2: [  # Python Course
                {"id": 5, "title": "Advanced Python Decorators", "type": LessonType.VIDEO, 
                 "content_url": "/content/python-decorators.mp4", "description": "Master Python decorators", 
                 "duration_minutes": 25, "order": 1},
                {"id": 6, "title": "Context Managers and With Statement", "type": LessonType.INTERACTIVE, 
                 "content_url": "/interactive/context-managers", "description": "Learn context managers with hands-on exercises", 
                 "duration_minutes": 30, "order": 2},
                {"id": 7, "title": "Metaclasses and Advanced OOP", "type": LessonType.TEXT, 
                 "content_url": "/content/metaclasses.html", "description": "Deep dive into Python's metaclass system", 
                 "duration_minutes": 35, "order": 3},
            ],
            3: [  # Data Science Course
                {"id": 8, "title": "Introduction to Statistics", "type": LessonType.TEXT, 
                 "content_url": "/content/stats-intro.html", "description": "Basic statistical concepts", 
                 "duration_minutes": 18, "order": 1},
                {"id": 9, "title": "Data Visualization with Python", "type": LessonType.SIMULATION, 
                 "content_url": "/simulation/data-viz", "description": "Interactive data visualization exercises", 
                 "duration_minutes": 35, "order": 2},
                {"id": 10, "title": "Exploratory Data Analysis", "type": LessonType.INTERACTIVE, 
                 "content_url": "/interactive/eda", "description": "Hands-on EDA techniques", 
                 "duration_minutes": 40, "order": 3},
            ]
        }
        
        for course_id, lessons in lessons_data.items():
            self.lessons[course_id] = lessons
        
        # Sample enrollments and progress
        sample_users = ["user1", "user2", "user3"]
        for user_id in sample_users:
            self.user_enrollments[user_id] = []
            
            # Enroll users in random courses
            enrolled_courses = random.sample(list(self.courses.keys()), random.randint(1, 3))
            for course_id in enrolled_courses:
                self._create_enrollment(user_id, course_id)
    
    def _create_enrollment(self, user_id: str, course_id: int):
        """Helper method to create enrollment with sample progress"""
        enrollment_key = (user_id, course_id)
        enrollment_date = datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 30))
        
        # Create enrollment record
        enrollment = {
            "id": f"enroll_{user_id}_{course_id}",
            "user_id": user_id,
            "course_id": course_id,
            "enrolled_at": enrollment_date,
            "status": "active",
            "last_accessed": datetime.datetime.now() - datetime.timedelta(hours=random.randint(1, 48))
        }
        
        self.enrollments[enrollment_key] = enrollment
        
        if user_id not in self.user_enrollments:
            self.user_enrollments[user_id] = []
        self.user_enrollments[user_id].append(course_id)
        
        # Create progress record with some sample progress
        course_lessons = self.lessons.get(course_id, [])
        completed_lessons = random.sample(
            [lesson["id"] for lesson in course_lessons], 
            random.randint(0, len(course_lessons))
        ) if course_lessons else []
        
        progress_percentage = (len(completed_lessons) / len(course_lessons) * 100) if course_lessons else 0
        
        progress = {
            "user_id": user_id,
            "course_id": course_id,
            "completed_lessons": completed_lessons,
            "progress_percentage": round(progress_percentage, 1),
            "time_spent_minutes": random.randint(30, 300),
            "current_lesson_id": course_lessons[0]["id"] if course_lessons and not completed_lessons else None,
            "last_lesson_completed": completed_lessons[-1] if completed_lessons else None,
            "started_at": enrollment_date,
            "last_updated": datetime.datetime.now() - datetime.timedelta(hours=random.randint(1, 24))
        }
        
        self.progress[enrollment_key] = progress
    
    def get_course(self, course_id: int) -> Optional[dict]:
        """Get a specific course by ID"""
        course = self.courses.get(course_id)
        if course:
            # Add lessons to course data
            course_with_lessons = course.copy()
            course_with_lessons["lessons"] = self.lessons.get(course_id, [])
            return course_with_lessons
        return None
    
    def get_all_courses(self, status: Optional[str] = None, category: Optional[str] = None, 
                       difficulty: Optional[str] = None) -> List[dict]:
        """Get all courses with optional filtering"""
        courses = list(self.courses.values())
        
        # Apply filters
        if status:
            courses = [c for c in courses if c["status"] == status]
        if category:
            courses = [c for c in courses if c["category"].lower() == category.lower()]
        if difficulty:
            courses = [c for c in courses if c["difficulty"] == difficulty]
        
        # Sort by enrollment count (most popular first)
        courses.sort(key=lambda x: x["enrollment_count"], reverse=True)
        
        return courses
    
    def enroll_user(self, user_id: str, course_id: int) -> dict:
        """Enroll a user in a course"""
        # Check if course exists
        if course_id not in self.courses:
            raise ValueError(f"Course {course_id} not found")
        
        enrollment_key = (user_id, course_id)
        
        # Check if already enrolled
        if enrollment_key in self.enrollments:
            return self.enrollments[enrollment_key]
        
        # Create new enrollment
        enrollment = {
            "id": f"enroll_{user_id}_{course_id}",
            "user_id": user_id,
            "course_id": course_id,
            "enrolled_at": datetime.datetime.now(),
            "status": "active",
            "last_accessed": datetime.datetime.now()
        }
        
        self.enrollments[enrollment_key] = enrollment
        
        # Add to user's enrollment list
        if user_id not in self.user_enrollments:
            self.user_enrollments[user_id] = []
        self.user_enrollments[user_id].append(course_id)
        
        # Initialize progress tracking
        progress = {
            "user_id": user_id,
            "course_id": course_id,
            "completed_lessons": [],
            "progress_percentage": 0.0,
            "time_spent_minutes": 0,
            "current_lesson_id": None,
            "last_lesson_completed": None,
            "started_at": datetime.datetime.now(),
            "last_updated": datetime.datetime.now()
        }
        
        self.progress[enrollment_key] = progress
        
        # Update course enrollment count
        self.courses[course_id]["enrollment_count"] += 1
        
        return enrollment
    
    def get_user_enrollments(self, user_id: str) -> List[dict]:
        """Get all enrollments for a user with course details"""
        user_course_ids = self.user_enrollments.get(user_id, [])
        enrollments_with_details = []
        
        for course_id in user_course_ids:
            enrollment_key = (user_id, course_id)
            enrollment = self.enrollments.get(enrollment_key)
            course = self.courses.get(course_id)
            progress = self.progress.get(enrollment_key, {})
            
            if enrollment and course:
                enrollment_detail = enrollment.copy()
                enrollment_detail["course"] = course
                enrollment_detail["progress"] = progress
                enrollments_with_details.append(enrollment_detail)
        
        # Sort by last accessed (most recent first)
        enrollments_with_details.sort(key=lambda x: x["last_accessed"], reverse=True)
        
        return enrollments_with_details
    
    def update_lesson_progress(self, user_id: str, course_id: int, lesson_id: int) -> dict:
        """Mark a lesson as completed and update progress"""
        enrollment_key = (user_id, course_id)
        
        # Check if user is enrolled
        if enrollment_key not in self.enrollments:
            raise ValueError(f"User {user_id} not enrolled in course {course_id}")
        
        # Get current progress
        progress = self.progress.get(enrollment_key, {})
        completed_lessons = progress.get("completed_lessons", [])
        
        # Add lesson if not already completed
        if lesson_id not in completed_lessons:
            completed_lessons.append(lesson_id)
            
            # Update progress
            course_lessons = self.lessons.get(course_id, [])
            total_lessons = len(course_lessons)
            progress_percentage = (len(completed_lessons) / total_lessons * 100) if total_lessons > 0 else 0
            
            progress.update({
                "completed_lessons": completed_lessons,
                "progress_percentage": round(progress_percentage, 1),
                "last_lesson_completed": lesson_id,
                "last_updated": datetime.datetime.now(),
                "time_spent_minutes": progress.get("time_spent_minutes", 0) + random.randint(10, 30)
            })
            
            # Update next lesson
            if course_lessons:
                current_lesson_index = next((i for i, lesson in enumerate(course_lessons) if lesson["id"] == lesson_id), -1)
                if current_lesson_index >= 0 and current_lesson_index < len(course_lessons) - 1:
                    progress["current_lesson_id"] = course_lessons[current_lesson_index + 1]["id"]
                else:
                    progress["current_lesson_id"] = None  # Course completed
            
            self.progress[enrollment_key] = progress
            
            # Update last accessed time
            self.enrollments[enrollment_key]["last_accessed"] = datetime.datetime.now()
        
        return progress
    
    def get_course_progress(self, user_id: str, course_id: int) -> dict:
        """Get detailed progress for a specific course"""
        enrollment_key = (user_id, course_id)
        
        if enrollment_key not in self.progress:
            raise ValueError(f"No progress found for user {user_id} in course {course_id}")
        
        progress = self.progress[enrollment_key].copy()
        course_lessons = self.lessons.get(course_id, [])
        
        # Add lesson details
        progress["total_lessons"] = len(course_lessons)
        progress["completed_lesson_count"] = len(progress.get("completed_lessons", []))
        progress["remaining_lessons"] = progress["total_lessons"] - progress["completed_lesson_count"]
        
        # Estimate time to completion
        avg_lesson_duration = sum(lesson.get("duration_minutes", 20) for lesson in course_lessons) / len(course_lessons) if course_lessons else 20
        estimated_remaining_time = progress["remaining_lessons"] * avg_lesson_duration
        progress["estimated_completion_time_minutes"] = estimated_remaining_time
        
        return progress
    
    def get_course_analytics(self, course_id: int) -> dict:
        """Get analytics for a specific course"""
        if course_id not in self.courses:
            raise ValueError(f"Course {course_id} not found")
        
        course = self.courses[course_id]
        
        # Calculate analytics from enrollments and progress
        enrollments_for_course = [
            (enrollment, progress) for (user_id, cid), (enrollment, progress) in 
            zip(self.enrollments.items(), self.progress.items()) if cid == course_id
        ]
        
        total_enrollments = len(enrollments_for_course)
        if total_enrollments == 0:
            return {
                "course_id": course_id,
                "total_enrollments": 0,
                "completion_rate": 0,
                "average_progress": 0,
                "average_time_spent": 0
            }
        
        completion_count = sum(1 for _, progress in enrollments_for_course if progress.get("progress_percentage", 0) >= 100)
        average_progress = sum(progress.get("progress_percentage", 0) for _, progress in enrollments_for_course) / total_enrollments
        average_time_spent = sum(progress.get("time_spent_minutes", 0) for _, progress in enrollments_for_course) / total_enrollments
        
        return {
            "course_id": course_id,
            "total_enrollments": total_enrollments,
            "completion_rate": round((completion_count / total_enrollments) * 100, 1),
            "average_progress": round(average_progress, 1),
            "average_time_spent": round(average_time_spent, 1),
            "rating": course.get("rating", 0),
            "total_ratings": course.get("total_ratings", 0)
        }
