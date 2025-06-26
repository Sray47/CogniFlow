# services/learning-analytics/integrations.py

"""
Integration Module for Learning Analytics Service

This module provides integration capabilities with other CogniFlow services,
enabling seamless data flow and coordinated functionality across the platform.

Functions include:
- Course service integration for lesson metadata
- User service integration for user context
- Real-time event propagation
- Cross-service analytics aggregation

Author: CogniFlow Development Team
Version: 1.0.0
"""

import os
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service configuration
NO_DATABASE_MODE = os.getenv("NO_DATABASE_MODE", "False").lower() == "true"
USERS_SERVICE_URL = os.getenv("USERS_SERVICE_URL", "http://users-service:8001")
COURSES_SERVICE_URL = os.getenv("COURSES_SERVICE_URL", "http://courses-service:8002")


class ServiceIntegrationError(Exception):
    """Custom exception for service integration errors"""
    pass


class CourseServiceIntegration:
    """
    Integration with the Courses Service
    
    Provides methods to fetch course and lesson metadata required for
    comprehensive learning analytics and progress tracking.
    """
    
    def __init__(self, base_url: str = COURSES_SERVICE_URL):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session for service communication"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    
    async def get_course_details(self, course_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch detailed course information from the Courses Service
        
        Args:
            course_id: Unique identifier for the course
            
        Returns:
            Course details including metadata, lessons, and instructor information
            Returns None if course not found or service unavailable
        """
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/courses/{course_id}") as response:
                if response.status == 200:
                    course_data = await response.json()
                    logger.info(f"Successfully fetched course {course_id} details")
                    return course_data
                elif response.status == 404:
                    logger.warning(f"Course {course_id} not found")
                    return None
                else:
                    logger.error(f"Error fetching course {course_id}: HTTP {response.status}")
                    return None
        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching course {course_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching course {course_id}: {e}")
            return None
    
    
    async def get_lesson_metadata(self, course_id: int, lesson_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch specific lesson metadata for analytics context
        
        Args:
            course_id: Course identifier
            lesson_id: Lesson identifier within the course
            
        Returns:
            Lesson metadata including duration, type, difficulty, and content information
        """
        try:
            course_details = await self.get_course_details(course_id)
            if course_details and "lessons" in course_details:
                lesson = next(
                    (l for l in course_details["lessons"] if l.get("id") == lesson_id),
                    None
                )
                if lesson:
                    logger.info(f"Found lesson {lesson_id} in course {course_id}")
                    return lesson
                else:
                    logger.warning(f"Lesson {lesson_id} not found in course {course_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching lesson metadata: {e}")
            return None
    
    
    async def get_course_completion_requirements(self, course_id: int) -> Dict[str, Any]:
        """
        Get course completion requirements for progress calculation
        
        Args:
            course_id: Course identifier
            
        Returns:
            Dictionary containing completion requirements:
            - total_lessons: Number of lessons in the course
            - required_completion_percentage: Minimum completion rate
            - estimated_duration_hours: Expected time to complete
        """
        course_details = await self.get_course_details(course_id)
        
        if course_details:
            lessons = course_details.get("lessons", [])
            return {
                "total_lessons": len(lessons),
                "required_completion_percentage": 80.0,  # Default requirement
                "estimated_duration_hours": course_details.get("estimated_duration_hours", 0),
                "difficulty_level": course_details.get("difficulty", "intermediate"),
                "course_title": course_details.get("title", f"Course {course_id}")
            }
        else:
            # Fallback values if course service is unavailable
            logger.warning(f"Using fallback completion requirements for course {course_id}")
            return {
                "total_lessons": 10,  # Default assumption
                "required_completion_percentage": 80.0,
                "estimated_duration_hours": 20,
                "difficulty_level": "intermediate",
                "course_title": f"Course {course_id}"
            }
    
    
    async def close_session(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()


class UserServiceIntegration:
    """
    Integration with the Users Service
    
    Provides methods to fetch user information and context required for
    personalized learning analytics and recommendations.
    """
    
    def __init__(self, base_url: str = USERS_SERVICE_URL):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session for service communication"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    
    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch user profile information for learning context
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            User profile including preferences, learning style, and demographic info
        """
        try:
            session = await self._get_session()
            async with session.get(f"{self.base_url}/users/{user_id}") as response:
                if response.status == 200:
                    user_data = await response.json()
                    logger.info(f"Successfully fetched user {user_id} profile")
                    return user_data
                elif response.status == 404:
                    logger.warning(f"User {user_id} not found")
                    return None
                else:
                    logger.error(f"Error fetching user {user_id}: HTTP {response.status}")
                    return None
        except aiohttp.ClientError as e:
            logger.error(f"Network error fetching user {user_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching user {user_id}: {e}")
            return None
    
    
    async def get_user_learning_preferences(self, user_id: str) -> Dict[str, Any]:
        """
        Extract learning preferences from user profile for analytics personalization
        
        Args:
            user_id: User identifier
            
        Returns:
            Learning preferences including preferred difficulty, pace, and learning style
        """
        user_profile = await self.get_user_profile(user_id)
        
        if user_profile:
            return {
                "preferred_difficulty_level": user_profile.get("preferred_difficulty_level", 2),
                "learning_style_preferences": user_profile.get("learning_style_preferences", {}),
                "timezone": user_profile.get("timezone", "UTC"),
                "role": user_profile.get("role", "student"),
                "experience_level": user_profile.get("experience_level", "beginner")
            }
        else:
            # Default preferences if user service is unavailable
            logger.warning(f"Using default learning preferences for user {user_id}")
            return {
                "preferred_difficulty_level": 2,
                "learning_style_preferences": {"visual": 0.5, "auditory": 0.3, "kinesthetic": 0.2},
                "timezone": "UTC",
                "role": "student",
                "experience_level": "beginner"
            }
    
    
    async def update_user_last_activity(self, user_id: str) -> bool:
        """
        Update user's last activity timestamp in the Users Service
        
        Args:
            user_id: User identifier
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            session = await self._get_session()
            async with session.put(f"{self.base_url}/users/{user_id}/last-login") as response:
                success = response.status == 200
                if success:
                    logger.info(f"Updated last activity for user {user_id}")
                else:
                    logger.warning(f"Failed to update last activity for user {user_id}")
                return success
        except Exception as e:
            logger.error(f"Error updating last activity for user {user_id}: {e}")
            return False
    
    
    async def close_session(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()


class CrossServiceAnalytics:
    """
    Cross-service analytics aggregation and coordination
    
    Combines data from multiple services to provide comprehensive
    learning insights and platform-wide analytics.
    """
    
    def __init__(self):
        self.course_integration = CourseServiceIntegration()
        self.user_integration = UserServiceIntegration()
    
    
    async def get_enriched_progress_data(self, user_id: str, course_id: int, 
                                       base_progress: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich basic progress data with context from other services
        
        Args:
            user_id: User identifier
            course_id: Course identifier
            base_progress: Basic progress data from learning analytics
            
        Returns:
            Enriched progress data with course and user context
        """
        try:
            # Fetch data from other services concurrently
            course_details_task = self.course_integration.get_course_details(course_id)
            user_profile_task = self.user_integration.get_user_profile(user_id)
            completion_requirements_task = self.course_integration.get_course_completion_requirements(course_id)
            
            course_details, user_profile, completion_requirements = await asyncio.gather(
                course_details_task,
                user_profile_task, 
                completion_requirements_task,
                return_exceptions=True
            )
            
            # Enrich the base progress data
            enriched_data = base_progress.copy()
            
            if course_details and not isinstance(course_details, Exception):
                enriched_data.update({
                    "course_title": course_details.get("title", f"Course {course_id}"),
                    "course_difficulty": course_details.get("difficulty", "intermediate"),
                    "instructor_id": course_details.get("instructor_id"),
                    "course_category": course_details.get("category", "General"),
                    "course_tags": course_details.get("tags", [])
                })
            
            if completion_requirements and not isinstance(completion_requirements, Exception):
                enriched_data.update({
                    "total_lessons": completion_requirements["total_lessons"],
                    "estimated_total_duration_hours": completion_requirements["estimated_duration_hours"]
                })
            
            if user_profile and not isinstance(user_profile, Exception):
                enriched_data.update({
                    "user_role": user_profile.get("role", "student"),
                    "user_timezone": user_profile.get("timezone", "UTC"),
                    "user_experience_level": user_profile.get("experience_level", "beginner")
                })
            
            # Calculate personalized recommendations
            enriched_data["recommendations"] = await self._generate_recommendations(
                user_id, course_id, enriched_data
            )
            
            return enriched_data
            
        except Exception as e:
            logger.error(f"Error enriching progress data: {e}")
            # Return base data if enrichment fails
            return base_progress
    
    
    async def _generate_recommendations(self, user_id: str, course_id: int, 
                                      progress_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate personalized learning recommendations based on progress and context
        
        Args:
            user_id: User identifier
            course_id: Course identifier
            progress_data: Current progress data
            
        Returns:
            List of personalized recommendations
        """
        recommendations = []
        
        try:
            progress_percentage = progress_data.get("overall_progress_percentage", 0)
            completion_status = progress_data.get("completion_status", "not_started")
            
            # Recommendation logic based on progress
            if progress_percentage < 25:
                recommendations.append({
                    "type": "motivation",
                    "title": "Get Started",
                    "message": "You're just beginning your learning journey. Start with the first lesson to build momentum!",
                    "priority": "high"
                })
            elif progress_percentage < 50:
                recommendations.append({
                    "type": "pacing",
                    "title": "Maintain Momentum", 
                    "message": "You're making good progress! Try to complete at least one lesson every few days.",
                    "priority": "medium"
                })
            elif progress_percentage < 80:
                recommendations.append({
                    "type": "encouragement",
                    "title": "Almost There",
                    "message": "You're more than halfway through! Keep up the excellent work.",
                    "priority": "medium"
                })
            else:
                recommendations.append({
                    "type": "completion",
                    "title": "Finish Strong",
                    "message": "You're so close to completing this course. Finish the remaining lessons to earn your certificate!",
                    "priority": "high"
                })
            
            # Time-based recommendations
            last_accessed = progress_data.get("last_accessed")
            if last_accessed:
                last_access_date = datetime.fromisoformat(last_accessed.replace('Z', '+00:00'))
                days_since_access = (datetime.now() - last_access_date).days
                
                if days_since_access > 7:
                    recommendations.append({
                        "type": "re_engagement",
                        "title": "Welcome Back",
                        "message": f"It's been {days_since_access} days since your last session. Jump back in where you left off!",
                        "priority": "high"
                    })
                elif days_since_access > 3:
                    recommendations.append({
                        "type": "reminder",
                        "title": "Continue Learning",
                        "message": "Ready to continue your learning journey? Your next lesson is waiting!",
                        "priority": "medium"
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return []
    
    
    async def get_platform_wide_analytics(self) -> Dict[str, Any]:
        """
        Generate platform-wide analytics by aggregating data across services
        
        Returns:
            Comprehensive platform analytics including:
            - Total active users
            - Course completion rates
            - Popular content
            - Learning trends
        """
        try:
            # This would integrate with all services to get comprehensive data
            # For now, providing a structure for production implementation
            
            analytics = {
                "timestamp": datetime.utcnow().isoformat(),
                "total_active_users": 0,  # Would query users service
                "total_courses": 0,       # Would query courses service
                "total_learning_sessions": 0,  # From learning analytics
                "average_completion_rate": 0.0,
                "most_popular_courses": [],
                "learning_trends": {
                    "peak_learning_hours": [],
                    "preferred_content_types": {},
                    "average_session_duration_minutes": 0
                },
                "geographic_distribution": {},  # Based on user timezones
                "performance_metrics": {
                    "average_response_time_ms": 0,
                    "service_availability": {
                        "users_service": True,
                        "courses_service": True,
                        "learning_analytics": True
                    }
                }
            }
            
            logger.info("Generated platform-wide analytics")
            return analytics
            
        except Exception as e:
            logger.error(f"Error generating platform analytics: {e}")
            return {"error": "Unable to generate analytics", "timestamp": datetime.utcnow().isoformat()}
    
    
    async def cleanup(self):
        """Clean up resources and close connections"""
        await self.course_integration.close_session()
        await self.user_integration.close_session()


# Global integration instance for service-wide use
service_integrations = CrossServiceAnalytics()


async def initialize_integrations():
    """Initialize service integrations on startup"""
    logger.info("Initializing service integrations for Learning Analytics")
    # Any initialization logic would go here
    

async def cleanup_integrations():
    """Clean up integrations on shutdown"""
    logger.info("Cleaning up service integrations")
    await service_integrations.cleanup()


# Production-ready error handling and retry logic
class RetryableServiceCall:
    """
    Utility class for retryable service calls with exponential backoff
    
    Provides robust error handling for inter-service communication
    in production environments.
    """
    
    @staticmethod
    async def call_with_retry(
        coroutine_func,
        max_retries: int = 3,
        base_delay: float = 1.0,
        backoff_factor: float = 2.0
    ):
        """
        Execute a coroutine with retry logic and exponential backoff
        
        Args:
            coroutine_func: Async function to execute
            max_retries: Maximum number of retry attempts
            base_delay: Initial delay between retries (seconds)
            backoff_factor: Multiplier for delay on each retry
            
        Returns:
            Result of the coroutine function
            
        Raises:
            ServiceIntegrationError: If all retry attempts fail
        """
        last_exception = None
        delay = base_delay
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(f"Retry attempt {attempt}/{max_retries} after {delay}s delay")
                    await asyncio.sleep(delay)
                
                result = await coroutine_func()
                return result
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Service call attempt {attempt + 1} failed: {e}")
                
                if attempt < max_retries:
                    delay *= backoff_factor
                else:
                    break
        
        logger.error(f"All retry attempts failed. Last error: {last_exception}")
        raise ServiceIntegrationError(f"Service call failed after {max_retries} retries: {last_exception}")


# Development mode fallback data
FALLBACK_COURSE_DATA = {
    1: {
        "id": 1,
        "title": "Introduction to Artificial Intelligence",
        "difficulty": "beginner",
        "category": "Technology",
        "estimated_duration_hours": 20,
        "total_lessons": 8,
        "instructor_id": 2
    },
    2: {
        "id": 2,
        "title": "Advanced Python Programming", 
        "difficulty": "advanced",
        "category": "Programming",
        "estimated_duration_hours": 35,
        "total_lessons": 12,
        "instructor_id": 2
    },
    3: {
        "id": 3,
        "title": "Data Science Fundamentals",
        "difficulty": "intermediate", 
        "category": "Data Science",
        "estimated_duration_hours": 25,
        "total_lessons": 10,
        "instructor_id": 2
    }
}
