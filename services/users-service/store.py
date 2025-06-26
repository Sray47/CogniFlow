"""
Users Service - Data Store Abstraction
======================================

This module provides data storage abstraction for the Users service.
In development mode, it uses in-memory storage.
In production mode, it can be swapped with PostgreSQL/Redis implementations.

Key Features:
- User profile management and preferences
- Learning progress and achievement tracking
- User statistics and analytics
- Learning style and preferences
- Social features and connections
"""

import datetime
import random
import uuid
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod
from enum import Enum


class UserRole(str, Enum):
    STUDENT = "student"
    INSTRUCTOR = "instructor"
    ADMIN = "admin"
    MODERATOR = "moderator"


class UserStatus(str, Enum):
    ACTIVE = "active" 
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"


class LearningStyle(str, Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    KINESTHETIC = "kinesthetic"
    READING = "reading"


class UserStoreInterface(ABC):
    """Abstract interface for User data storage"""
    
    @abstractmethod
    def get_user(self, user_id: str) -> Optional[dict]:
        pass
    
    @abstractmethod
    def create_user(self, user_data: dict) -> dict:
        pass
    
    @abstractmethod
    def update_user(self, user_id: str, update_data: dict) -> dict:
        pass
    
    @abstractmethod
    def delete_user(self, user_id: str) -> bool:
        pass
    
    @abstractmethod
    def get_user_progress(self, user_id: str) -> dict:
        pass
    
    @abstractmethod
    def update_user_progress(self, user_id: str, progress_data: dict):
        pass
    
    @abstractmethod
    def get_user_achievements(self, user_id: str) -> List[dict]:
        pass
    
    @abstractmethod
    def add_achievement(self, user_id: str, achievement: dict):
        pass
    
    @abstractmethod
    def get_user_preferences(self, user_id: str) -> dict:
        pass
    
    @abstractmethod
    def update_user_preferences(self, user_id: str, preferences: dict):
        pass


class InMemoryUserStore(UserStoreInterface):
    """
    In-memory implementation of User store for development mode.
    
    Features:
    - Complete user profile management
    - Learning progress and statistics tracking
    - Achievement system
    - User preferences and settings
    - Social features
    """
    
    def __init__(self):
        # Core user data
        self.users = {}  # user_id -> user profile
        self.user_progress = {}  # user_id -> learning progress
        self.user_achievements = {}  # user_id -> list of achievements
        self.user_preferences = {}  # user_id -> preferences dict
        self.user_statistics = {}  # user_id -> detailed stats
        self.user_social = {}  # user_id -> social connections and activity
        
        # Tracking and analytics
        self.user_sessions = {}  # user_id -> session history
        self.user_activity_log = {}  # user_id -> activity log
        
        # Available achievements system
        self.available_achievements = {
            "first_login": {
                "id": "first_login",
                "name": "Welcome Aboard",
                "description": "Successfully logged in for the first time",
                "icon": "🎉",
                "category": "milestone",
                "points": 10
            },
            "course_completion": {
                "id": "course_completion", 
                "name": "Course Conqueror",
                "description": "Completed your first course",
                "icon": "🏆",
                "category": "achievement",
                "points": 100
            },
            "week_streak": {
                "id": "week_streak",
                "name": "Dedicated Learner",
                "description": "Studied for 7 consecutive days",
                "icon": "🔥",
                "category": "streak",
                "points": 50
            },
            "quiz_master": {
                "id": "quiz_master",
                "name": "Quiz Master",
                "description": "Scored 90%+ on 10 quizzes",
                "icon": "🎯",
                "category": "performance",
                "points": 75
            },
            "social_butterfly": {
                "id": "social_butterfly",
                "name": "Social Butterfly",
                "description": "Connected with 10 other learners",
                "icon": "🦋",
                "category": "social",
                "points": 25
            }
        }
        
        # Initialize with sample data
        self._init_sample_data()
    
    def _init_sample_data(self):
        """Initialize with comprehensive sample data for demo purposes"""
        sample_users = [
            {
                "user_id": "user1",
                "email": "alice@example.com",
                "username": "alice_learns",
                "full_name": "Alice Johnson",
                "role": UserRole.STUDENT,
                "learning_style": LearningStyle.VISUAL
            },
            {
                "user_id": "user2", 
                "email": "bob@example.com",
                "username": "bob_codes",
                "full_name": "Bob Smith",
                "role": UserRole.STUDENT,
                "learning_style": LearningStyle.KINESTHETIC
            },
            {
                "user_id": "user3",
                "email": "carol@example.com", 
                "username": "carol_teaches",
                "full_name": "Carol Davis",
                "role": UserRole.INSTRUCTOR,
                "learning_style": LearningStyle.AUDITORY
            }
        ]
        
        for user_data in sample_users:
            user_id = user_data["user_id"]
            
            # Create user profile
            self.users[user_id] = {
                "user_id": user_id,
                "email": user_data["email"],
                "username": user_data["username"],
                "full_name": user_data["full_name"],
                "role": user_data["role"],
                "status": UserStatus.ACTIVE,
                "created_at": datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 90)),
                "last_login": datetime.datetime.now() - datetime.timedelta(hours=random.randint(1, 48)),
                "profile_picture": f"https://api.dicebear.com/7.x/avataaars/svg?seed={user_data['username']}",
                "bio": f"Passionate learner interested in technology and continuous improvement. {user_data['full_name']} is dedicated to mastering new skills.",
                "location": random.choice(["New York, NY", "San Francisco, CA", "London, UK", "Toronto, CA", "Sydney, AU"]),
                "timezone": "UTC"
            }
            
            # User progress tracking
            self.user_progress[user_id] = {
                "total_courses_enrolled": random.randint(3, 15),
                "courses_completed": random.randint(1, 8),
                "lessons_completed": random.randint(25, 150),
                "total_study_time_minutes": random.randint(300, 2400),
                "current_streak_days": random.randint(0, 25),
                "longest_streak_days": random.randint(5, 40),
                "average_session_length_minutes": random.randint(15, 60),
                "total_points": random.randint(100, 1500),
                "current_level": random.randint(1, 12),
                "experience_points": random.randint(250, 3000),
                "last_activity": datetime.datetime.now() - datetime.timedelta(hours=random.randint(1, 24)),
                "weekly_goals": {
                    "study_minutes": 180,
                    "lessons_completed": 5,
                    "courses_started": 1
                },
                "weekly_progress": {
                    "study_minutes": random.randint(50, 200),
                    "lessons_completed": random.randint(2, 8),
                    "courses_started": random.randint(0, 2)
                }
            }
            
            # User achievements
            earned_achievements = random.sample(list(self.available_achievements.keys()), random.randint(1, 3))
            self.user_achievements[user_id] = []
            for achievement_id in earned_achievements:
                self.user_achievements[user_id].append({
                    **self.available_achievements[achievement_id],
                    "earned_at": datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 30)),
                    "progress": 100
                })
            
            # User preferences
            self.user_preferences[user_id] = {
                "learning_style": user_data["learning_style"],
                "difficulty_preference": random.choice(["beginner", "intermediate", "advanced"]),
                "notification_settings": {
                    "email_notifications": True,
                    "push_notifications": True,
                    "reminder_frequency": random.choice(["daily", "weekly", "bi-weekly"]),
                    "digest_frequency": "weekly"
                },
                "privacy_settings": {
                    "profile_visibility": "public",
                    "progress_visibility": "friends",
                    "allow_messages": True
                },
                "study_preferences": {
                    "preferred_study_time": random.choice(["morning", "afternoon", "evening"]),
                    "session_length_preference": random.choice([15, 30, 45, 60]),
                    "break_reminders": True,
                    "focus_mode": False
                },
                "ui_preferences": {
                    "theme": random.choice(["light", "dark", "auto"]),
                    "language": "en",
                    "font_size": "medium",
                    "animations_enabled": True
                }
            }
            
            # Detailed user statistics
            self.user_statistics[user_id] = {
                "learning_velocity": {
                    "lessons_per_week": random.uniform(3.0, 12.0),
                    "average_completion_rate": random.uniform(0.65, 0.98),
                    "time_to_complete_lesson_minutes": random.uniform(8.0, 25.0)
                },
                "engagement_metrics": {
                    "sessions_this_month": random.randint(8, 30),
                    "average_session_rating": random.uniform(3.5, 5.0),
                    "forum_posts": random.randint(0, 15),
                    "questions_asked": random.randint(2, 20),
                    "answers_provided": random.randint(0, 10)
                },
                "skill_progression": {
                    "python": random.uniform(0.2, 0.9),
                    "javascript": random.uniform(0.1, 0.8),
                    "data_science": random.uniform(0.0, 0.7),
                    "web_development": random.uniform(0.1, 0.85)
                },
                "performance_trends": {
                    "quiz_accuracy_trend": [random.uniform(0.6, 0.95) for _ in range(12)],  # Last 12 months
                    "study_time_trend": [random.randint(60, 300) for _ in range(12)],
                    "engagement_trend": [random.uniform(0.3, 1.0) for _ in range(12)]
                }
            }
            
            # Social connections and activity
            self.user_social[user_id] = {
                "friends": random.sample([uid for uid in ["user1", "user2", "user3"] if uid != user_id], random.randint(0, 2)),
                "following": random.randint(3, 15),
                "followers": random.randint(1, 20),
                "study_groups": random.randint(0, 3),
                "recent_activity": [
                    {
                        "activity_type": "course_enrollment",
                        "details": "Enrolled in Python Advanced Concepts",
                        "timestamp": datetime.datetime.now() - datetime.timedelta(days=2),
                        "privacy": "public"
                    },
                    {
                        "activity_type": "achievement_earned",
                        "details": "Earned 'Quiz Master' badge",
                        "timestamp": datetime.datetime.now() - datetime.timedelta(days=5),
                        "privacy": "friends"
                    }
                ]
            }
            
            # Session tracking
            self.user_sessions[user_id] = [
                {
                    "session_id": str(uuid.uuid4()),
                    "start_time": datetime.datetime.now() - datetime.timedelta(hours=random.randint(1, 72)),
                    "duration_minutes": random.randint(15, 120),
                    "activities": random.sample(["lesson", "quiz", "forum", "chat"], random.randint(1, 3)),
                    "effectiveness_score": random.uniform(0.6, 1.0)
                }
                for _ in range(random.randint(5, 20))
            ]
    
    def get_user(self, user_id: str) -> Optional[dict]:
        """Get complete user profile"""
        return self.users.get(user_id)
    
    def create_user(self, user_data: dict) -> dict:
        """Create a new user with default settings"""
        user_id = str(uuid.uuid4())
        
        new_user = {
            "user_id": user_id,
            "email": user_data.get("email"),
            "username": user_data.get("username"),
            "full_name": user_data.get("full_name"),
            "role": user_data.get("role", UserRole.STUDENT),
            "status": UserStatus.ACTIVE,
            "created_at": datetime.datetime.now(),
            "last_login": None,
            "profile_picture": f"https://api.dicebear.com/7.x/avataaars/svg?seed={user_data.get('username', user_id)}",
            "bio": "",
            "location": "",
            "timezone": "UTC"
        }
        
        self.users[user_id] = new_user
        
        # Initialize user progress
        self.user_progress[user_id] = {
            "total_courses_enrolled": 0,
            "courses_completed": 0, 
            "lessons_completed": 0,
            "total_study_time_minutes": 0,
            "current_streak_days": 0,
            "longest_streak_days": 0,
            "average_session_length_minutes": 0,
            "total_points": 0,
            "current_level": 1,
            "experience_points": 0,
            "last_activity": datetime.datetime.now(),
            "weekly_goals": {
                "study_minutes": 120,
                "lessons_completed": 3,
                "courses_started": 1
            },
            "weekly_progress": {
                "study_minutes": 0,
                "lessons_completed": 0,
                "courses_started": 0
            }
        }
        
        # Initialize achievements, preferences, etc.
        self.user_achievements[user_id] = []
        self.user_preferences[user_id] = self._get_default_preferences()
        self.user_statistics[user_id] = self._get_default_statistics()
        self.user_social[user_id] = self._get_default_social()
        self.user_sessions[user_id] = []
        
        # Award first login achievement
        self.add_achievement(user_id, self.available_achievements["first_login"])
        
        return new_user
    
    def update_user(self, user_id: str, update_data: dict) -> dict:
        """Update user profile information"""
        if user_id not in self.users:
            raise ValueError(f"User {user_id} not found")
        
        user = self.users[user_id]
        
        # Update allowed fields
        allowed_fields = ["full_name", "bio", "location", "timezone", "profile_picture"]
        for field in allowed_fields:
            if field in update_data:
                user[field] = update_data[field]
        
        user["updated_at"] = datetime.datetime.now()
        return user
    
    def delete_user(self, user_id: str) -> bool:
        """Soft delete user (mark as inactive)"""
        if user_id not in self.users:
            return False
        
        self.users[user_id]["status"] = UserStatus.INACTIVE
        self.users[user_id]["deactivated_at"] = datetime.datetime.now()
        return True
    
    def get_user_progress(self, user_id: str) -> dict:
        """Get comprehensive user learning progress"""
        return self.user_progress.get(user_id, {})
    
    def update_user_progress(self, user_id: str, progress_data: dict):
        """Update user learning progress"""
        if user_id not in self.user_progress:
            return
        
        progress = self.user_progress[user_id]
        
        # Update specific progress metrics
        for key, value in progress_data.items():
            if key in progress:
                if isinstance(progress[key], int):
                    progress[key] += value
                else:
                    progress[key] = value
        
        progress["last_activity"] = datetime.datetime.now()
        
        # Check for level progression
        self._check_level_progression(user_id)
    
    def get_user_achievements(self, user_id: str) -> List[dict]:
        """Get user's earned achievements"""
        return self.user_achievements.get(user_id, [])
    
    def add_achievement(self, user_id: str, achievement: dict):
        """Award achievement to user"""
        if user_id not in self.user_achievements:
            self.user_achievements[user_id] = []
        
        # Check if already earned
        for earned in self.user_achievements[user_id]:
            if earned["id"] == achievement["id"]:
                return
        
        achievement_with_timestamp = achievement.copy()
        achievement_with_timestamp["earned_at"] = datetime.datetime.now()
        achievement_with_timestamp["progress"] = 100
        
        self.user_achievements[user_id].append(achievement_with_timestamp)
        
        # Award points for achievement
        if "points" in achievement:
            self.update_user_progress(user_id, {"total_points": achievement["points"]})
    
    def get_user_preferences(self, user_id: str) -> dict:
        """Get user preferences and settings"""
        return self.user_preferences.get(user_id, {})
    
    def update_user_preferences(self, user_id: str, preferences: dict):
        """Update user preferences"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = self._get_default_preferences()
        
        # Deep merge preferences
        current = self.user_preferences[user_id]
        for key, value in preferences.items():
            if isinstance(value, dict) and key in current and isinstance(current[key], dict):
                current[key].update(value)
            else:
                current[key] = value
    
    def get_user_statistics(self, user_id: str) -> dict:
        """Get detailed user statistics and analytics"""
        return self.user_statistics.get(user_id, {})
    
    def get_user_social(self, user_id: str) -> dict:
        """Get user's social connections and activity"""
        return self.user_social.get(user_id, {})
    
    def get_leaderboard(self, metric: str = "total_points", limit: int = 10) -> List[dict]:
        """Get user leaderboard for specified metric"""
        user_scores = []
        
        for user_id, progress in self.user_progress.items():
            if user_id in self.users:
                user = self.users[user_id]
                score = progress.get(metric, 0)
                user_scores.append({
                    "user_id": user_id,
                    "username": user.get("username"),
                    "full_name": user.get("full_name"),
                    "profile_picture": user.get("profile_picture"),
                    "score": score,
                    "metric": metric
                })
        
        # Sort by score descending
        user_scores.sort(key=lambda x: x["score"], reverse=True)
        return user_scores[:limit]
    
    def _get_default_preferences(self) -> dict:
        """Get default user preferences"""
        return {
            "learning_style": LearningStyle.VISUAL,
            "difficulty_preference": "beginner",
            "notification_settings": {
                "email_notifications": True,
                "push_notifications": True,
                "reminder_frequency": "daily",
                "digest_frequency": "weekly"
            },
            "privacy_settings": {
                "profile_visibility": "public",
                "progress_visibility": "public",
                "allow_messages": True
            },
            "study_preferences": {
                "preferred_study_time": "evening",
                "session_length_preference": 30,
                "break_reminders": True,
                "focus_mode": False
            },
            "ui_preferences": {
                "theme": "light",
                "language": "en",
                "font_size": "medium",
                "animations_enabled": True
            }
        }
    
    def _get_default_statistics(self) -> dict:
        """Get default user statistics"""
        return {
            "learning_velocity": {
                "lessons_per_week": 0.0,
                "average_completion_rate": 0.0,
                "time_to_complete_lesson_minutes": 0.0
            },
            "engagement_metrics": {
                "sessions_this_month": 0,
                "average_session_rating": 0.0,
                "forum_posts": 0,
                "questions_asked": 0,
                "answers_provided": 0
            },
            "skill_progression": {},
            "performance_trends": {
                "quiz_accuracy_trend": [],
                "study_time_trend": [],
                "engagement_trend": []
            }
        }
    
    def _get_default_social(self) -> dict:
        """Get default social settings"""
        return {
            "friends": [],
            "following": 0,
            "followers": 0,
            "study_groups": 0,
            "recent_activity": []
        }
    
    def _check_level_progression(self, user_id: str):
        """Check if user should level up based on experience points"""
        progress = self.user_progress.get(user_id, {})
        current_level = progress.get("current_level", 1)
        experience_points = progress.get("experience_points", 0)
        
        # Simple level progression (could be more sophisticated)
        required_xp_for_next_level = current_level * 250
        
        if experience_points >= required_xp_for_next_level:
            progress["current_level"] = current_level + 1
            progress["experience_points"] = experience_points - required_xp_for_next_level
            
            # Award level up achievement (if exists)
            level_achievement = {
                "id": f"level_{current_level + 1}",
                "name": f"Level {current_level + 1}",
                "description": f"Reached level {current_level + 1}!",
                "icon": "⭐",
                "category": "progression",
                "points": (current_level + 1) * 10
            }
            self.add_achievement(user_id, level_achievement)


# Production implementation interface:
"""
class PostgreSQLUserStore(UserStoreInterface):
    def __init__(self, db_session, redis_client):
        self.db = db_session
        self.redis = redis_client

    def get_user(self, user_id: str) -> Optional[dict]:
        # Query PostgreSQL for user data
        # Cache frequently accessed data in Redis
        pass

    def update_user_progress(self, user_id: str, progress_data: dict):
        # Update progress in PostgreSQL
        # Update cache in Redis
        # Trigger analytics events
        pass

    # ... implement all other methods with proper database operations
"""
