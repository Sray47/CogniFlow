"""
AI Tutor Service - Data Store Abstraction
==========================================

This module provides data storage abstraction for the AI Tutor service.
In development mode, it uses in-memory storage.
In production mode, it can be swapped with PostgreSQL/Redis implementations.

Key Features:
- Spaced repetition scheduling with SM-2 algorithm
- Chat history management
- Gamification system with points and badges
- Adaptive content recommendations
- Learning session tracking
"""

import datetime
import random
import uuid
from typing import List, Dict, Optional, Any
from abc import ABC, abstractmethod


class AITutorStoreInterface(ABC):
    """Abstract interface for AI Tutor data storage"""
    
    @abstractmethod
    def get_chat_history(self, user_id: str) -> List[dict]:
        pass
    
    @abstractmethod
    def add_chat_message(self, user_id: str, message: str, response: str):
        pass
    
    @abstractmethod
    def update_spaced_repetition(self, user_id: str, item_id: str, performance: str) -> dict:
        pass
    
    @abstractmethod
    def get_spaced_repetition_schedule(self, user_id: str) -> List[dict]:
        pass
    
    @abstractmethod
    def get_user_points(self, user_id: str) -> int:
        pass
    
    @abstractmethod
    def add_points(self, user_id: str, points: int, reason: str):
        pass
    
    @abstractmethod
    def get_user_badges(self, user_id: str) -> List[dict]:
        pass
    
    @abstractmethod
    def award_badge(self, user_id: str, badge_id: str, badge_name: str):
        pass


class InMemoryAITutorStore(AITutorStoreInterface):
    """
    In-memory implementation of AI Tutor store for development mode.
    
    Features:
    - Spaced repetition with SM-2 algorithm
    - Gamification with points and badges
    - Chat history management
    - Adaptive content suggestions
    """
    
    def __init__(self):
        # Core data structures
        self.chat_history = {}  # user_id -> list of chat messages
        self.user_schedules = {}  # user_id -> spaced repetition schedule
        self.adaptive_content = {}  # user_id -> content preferences
        self.user_progress = {}  # user_id -> learning progress
        self.quiz_history = {}  # user_id -> quiz attempts
        self.learning_sessions = {}  # user_id -> session data
        
        # Gamification data
        self.user_points = {}  # user_id -> total points
        self.user_badges = {}  # user_id -> list of badges
        self.points_history = {}  # user_id -> list of point transactions
        
        # Initialize sample data
        self._init_sample_data()
    
    def _init_sample_data(self):
        """Initialize with sample data for demo purposes"""
        sample_users = ["user1", "user2", "user3"]
        
        # Sample badges available in the system
        self.available_badges = {
            "first_chat": {"name": "First Conversation", "description": "Started your first chat with AI tutor", "points": 10},
            "quiz_master": {"name": "Quiz Master", "description": "Completed 10 quizzes", "points": 50},
            "streak_5": {"name": "5-Day Streak", "description": "Studied for 5 consecutive days", "points": 100},
            "python_basics": {"name": "Python Basics", "description": "Mastered Python fundamentals", "points": 75},
            "fast_learner": {"name": "Fast Learner", "description": "Completed 3 lessons in one day", "points": 25},
            "perfectionist": {"name": "Perfectionist", "description": "Got 100% on 5 quizzes", "points": 150}
        }
        
        for user_id in sample_users:
            # Chat history
            self.chat_history[user_id] = [
                {
                    "id": str(uuid.uuid4()),
                    "timestamp": datetime.datetime.now() - datetime.timedelta(days=1), 
                    "message": "Hello AI tutor!", 
                    "response": "Hello! I'm excited to help you learn today. What would you like to explore?", 
                    "type": "greeting"
                },
                {
                    "id": str(uuid.uuid4()),
                    "timestamp": datetime.datetime.now() - datetime.timedelta(hours=2), 
                    "message": "Can you help me with Python?", 
                    "response": "Absolutely! Python is a fantastic programming language. What specific aspect would you like to focus on?", 
                    "type": "question"
                }
            ]
            
            # Spaced repetition schedule
            self.user_schedules[user_id] = [
                {
                    "item_id": "python_basics", 
                    "topic": "Python Variables and Data Types", 
                    "next_review": (datetime.datetime.now() + datetime.timedelta(days=1)).isoformat(),
                    "interval": 1,
                    "ease_factor": 2.5,
                    "repetitions": 2,
                    "due": True if random.random() > 0.5 else False
                },
                {
                    "item_id": "functions", 
                    "topic": "Python Functions and Scope", 
                    "next_review": (datetime.datetime.now() + datetime.timedelta(days=3)).isoformat(),
                    "interval": 3,
                    "ease_factor": 2.8,
                    "repetitions": 3,
                    "due": True if random.random() > 0.7 else False
                },
                {
                    "item_id": "loops", 
                    "topic": "Loops and Iteration", 
                    "next_review": (datetime.datetime.now() - datetime.timedelta(hours=2)).isoformat(),
                    "interval": 1,
                    "ease_factor": 2.3,
                    "repetitions": 1,
                    "due": True
                }
            ]
            
            # User preferences and adaptive content
            self.adaptive_content[user_id] = {
                "learning_style": random.choice(["visual", "auditory", "kinesthetic", "reading"]),
                "difficulty_preference": random.choice(["beginner", "intermediate", "advanced"]),
                "topic_interests": random.sample(["python", "mathematics", "data_science", "web_development", "machine_learning"], 3),
                "last_updated": datetime.datetime.now().isoformat(),
                "preferred_session_length": random.choice([15, 30, 45, 60]),
                "time_of_day_preference": random.choice(["morning", "afternoon", "evening"])
            }
            
            # User progress
            self.user_progress[user_id] = {
                "total_sessions": random.randint(5, 25),
                "total_time_minutes": random.randint(120, 600),
                "topics_mastered": random.randint(3, 12),
                "current_streak": random.randint(0, 15),
                "average_accuracy": random.uniform(0.65, 0.95),
                "last_session": (datetime.datetime.now() - datetime.timedelta(hours=random.randint(1, 48))).isoformat(),
                "sessions_this_week": random.randint(2, 7)
            }
            
            # Gamification data
            self.user_points[user_id] = random.randint(50, 500)
            self.user_badges[user_id] = random.sample(["first_chat", "python_basics", "fast_learner"], random.randint(1, 3))
            self.points_history[user_id] = [
                {"timestamp": datetime.datetime.now() - datetime.timedelta(days=1), "points": 25, "reason": "Completed Python quiz"},
                {"timestamp": datetime.datetime.now() - datetime.timedelta(hours=6), "points": 10, "reason": "Daily study session"},
                {"timestamp": datetime.datetime.now() - datetime.timedelta(hours=2), "points": 15, "reason": "Asked a great question"}
            ]
    
    def get_chat_history(self, user_id: str) -> List[dict]:
        """Get chat history for a user"""
        return self.chat_history.get(user_id, [])
    
    def add_chat_message(self, user_id: str, message: str, response: str):
        """Add a new chat message to history"""
        if user_id not in self.chat_history:
            self.chat_history[user_id] = []
        
        chat_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now().isoformat(),
            "message": message,
            "response": response,
            "type": "conversation"
        }
        
        self.chat_history[user_id].append(chat_entry)
        
        # Keep only last 50 messages for performance
        if len(self.chat_history[user_id]) > 50:
            self.chat_history[user_id] = self.chat_history[user_id][-50:]
        
        # Award points for engagement
        self.add_points(user_id, 2, "Chat interaction")
    
    def update_spaced_repetition(self, user_id: str, item_id: str, performance: str) -> dict:
        """
        Update spaced repetition schedule based on performance using SM-2 algorithm
        
        Performance levels:
        - 'easy': User found it very easy
        - 'good': User recalled with some effort  
        - 'hard': User recalled with difficulty
        - 'forgot': User completely forgot
        """
        if user_id not in self.user_schedules:
            self.user_schedules[user_id] = []
        
        # Find the item or create new one
        item = None
        for schedule_item in self.user_schedules[user_id]:
            if schedule_item["item_id"] == item_id:
                item = schedule_item
                break
        
        if not item:
            item = {
                "item_id": item_id,
                "topic": f"Topic: {item_id.replace('_', ' ').title()}",
                "interval": 1,
                "ease_factor": 2.5,
                "repetitions": 0
            }
            self.user_schedules[user_id].append(item)
        
        # SM-2 Algorithm implementation
        if performance == "forgot":
            item["ease_factor"] = max(1.3, item["ease_factor"] - 0.2)
            item["interval"] = 1
            item["repetitions"] = 0
            points_awarded = 5  # Still award some points for trying
        else:
            if item["repetitions"] == 0:
                item["interval"] = 1
            elif item["repetitions"] == 1:
                item["interval"] = 6
            else:
                item["interval"] = int(item["repetitions"] * item["ease_factor"])
            
            item["repetitions"] += 1
            
            # Adjust ease factor based on performance
            if performance == "easy":
                item["ease_factor"] = min(4.0, item["ease_factor"] + 0.15)
                points_awarded = 20
            elif performance == "good":
                item["ease_factor"] = item["ease_factor"]  # No change
                points_awarded = 15
            elif performance == "hard":
                item["ease_factor"] = max(1.3, item["ease_factor"] - 0.15)
                points_awarded = 10
        
        # Calculate next review date
        item["next_review"] = (datetime.datetime.now() + datetime.timedelta(days=item["interval"])).isoformat()
        item["due"] = False  # No longer due after review
        item["last_reviewed"] = datetime.datetime.now().isoformat()
        
        # Award points for spaced repetition practice
        self.add_points(user_id, points_awarded, f"Spaced repetition: {item['topic']}")
        
        return item
    
    def get_spaced_repetition_schedule(self, user_id: str) -> List[dict]:
        """Get user's spaced repetition schedule, with due items first"""
        schedule = self.user_schedules.get(user_id, [])
        
        # Update due status based on current time
        now = datetime.datetime.now()
        for item in schedule:
            next_review = datetime.datetime.fromisoformat(item["next_review"])
            item["due"] = now >= next_review
            item["overdue_hours"] = max(0, int((now - next_review).total_seconds() / 3600)) if item["due"] else 0
        
        # Sort by due status, then by next review date
        schedule.sort(key=lambda x: (not x["due"], x["next_review"]))
        
        return schedule
    
    def get_items_due_for_review(self, user_id: str) -> List[dict]:
        """Get only items that are due for review"""
        schedule = self.get_spaced_repetition_schedule(user_id)
        return [item for item in schedule if item["due"]]
    
    def get_user_points(self, user_id: str) -> int:
        """Get user's total points"""
        return self.user_points.get(user_id, 0)
    
    def add_points(self, user_id: str, points: int, reason: str):
        """Add points to user's account"""
        if user_id not in self.user_points:
            self.user_points[user_id] = 0
        if user_id not in self.points_history:
            self.points_history[user_id] = []
        
        self.user_points[user_id] += points
        self.points_history[user_id].append({
            "timestamp": datetime.datetime.now().isoformat(),
            "points": points,
            "reason": reason
        })
        
        # Check for badge eligibility
        self._check_badge_eligibility(user_id)
    
    def get_user_badges(self, user_id: str) -> List[dict]:
        """Get user's badges with full details"""
        user_badge_ids = self.user_badges.get(user_id, [])
        badges = []
        
        for badge_id in user_badge_ids:
            if badge_id in self.available_badges:
                badge_info = self.available_badges[badge_id].copy()
                badge_info["id"] = badge_id
                badge_info["earned_at"] = datetime.datetime.now().isoformat()  # Simplified for demo
                badges.append(badge_info)
        
        return badges
    
    def award_badge(self, user_id: str, badge_id: str, badge_name: str):
        """Award a badge to user"""
        if user_id not in self.user_badges:
            self.user_badges[user_id] = []
        
        if badge_id not in self.user_badges[user_id]:
            self.user_badges[user_id].append(badge_id)
            
            # Award bonus points for earning badge
            if badge_id in self.available_badges:
                bonus_points = self.available_badges[badge_id]["points"]
                self.add_points(user_id, bonus_points, f"Badge earned: {badge_name}")
    
    def _check_badge_eligibility(self, user_id: str):
        """Check if user is eligible for any new badges"""
        current_badges = self.user_badges.get(user_id, [])
        total_points = self.user_points.get(user_id, 0)
        
        # Check for point milestone badges
        if total_points >= 100 and "points_100" not in current_badges:
            self.award_badge(user_id, "points_100", "Century Club")
        
        # Check for streak badges based on sessions
        user_progress = self.user_progress.get(user_id, {})
        current_streak = user_progress.get("current_streak", 0)
        
        if current_streak >= 5 and "streak_5" not in current_badges:
            self.award_badge(user_id, "streak_5", "5-Day Streak")
    
    def get_adaptive_suggestions(self, user_id: str, topic: Optional[str] = None) -> List[str]:
        """Generate adaptive content suggestions based on user profile"""
        user_profile = self.adaptive_content.get(user_id, {})
        learning_style = user_profile.get("learning_style", "visual")
        interests = user_profile.get("topic_interests", ["general"])
        difficulty = user_profile.get("difficulty_preference", "beginner")
        
        suggestions = []
        
        if topic:
            # Topic-specific suggestions based on learning style
            if topic.lower() == "python":
                if learning_style == "visual":
                    suggestions = [
                        "Interactive Python code visualizer exercises",
                        "Flowchart-based Python logic building",
                        "Visual debugging tools and techniques",
                        "Infographic-style Python cheat sheets"
                    ]
                elif learning_style == "auditory":
                    suggestions = [
                        "Python podcast series for beginners",
                        "Code-along audio tutorials",
                        "Verbal explanation of Python concepts",
                        "Discussion-based Python problem solving"
                    ]
                else:
                    suggestions = [
                        f"Comprehensive Python learning path ({difficulty} level)",
                        f"Interactive Python exercises and challenges",
                        f"Real-world Python applications and case studies",
                        f"Python best practices and advanced concepts"
                    ]
            elif topic.lower() == "mathematics":
                suggestions = [
                    f"Visual mathematics concepts ({difficulty} level)",
                    f"Step-by-step math problem solving",
                    f"Interactive math simulations and games",
                    f"Real-world applications of mathematical concepts"
                ]
            else:
                suggestions = [
                    f"Comprehensive {topic} learning path ({difficulty} level)",
                    f"Interactive {topic} exercises and challenges",
                    f"Real-world {topic} applications and case studies",
                    f"Advanced {topic} concepts and best practices"
                ]
        else:
            # General suggestions based on interests
            for interest in interests[:3]:
                suggestions.extend([
                    f"Advanced {interest} masterclass series ({difficulty} level)",
                    f"Project-based {interest} learning track",
                    f"Interactive {interest} challenges and exercises"
                ])
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def get_user_stats(self, user_id: str) -> dict:
        """Get comprehensive user statistics"""
        progress = self.user_progress.get(user_id, {})
        points = self.user_points.get(user_id, 0)
        badges = len(self.user_badges.get(user_id, []))
        due_items = len(self.get_items_due_for_review(user_id))
        
        return {
            "total_points": points,
            "total_badges": badges,
            "current_streak": progress.get("current_streak", 0),
            "total_sessions": progress.get("total_sessions", 0),
            "topics_mastered": progress.get("topics_mastered", 0),
            "items_due_for_review": due_items,
            "average_accuracy": progress.get("average_accuracy", 0.0),
            "total_time_minutes": progress.get("total_time_minutes", 0)
        }


# Production implementation would look like this:
"""
class PostgreSQLAITutorStore(AITutorStoreInterface):
    def __init__(self, db_session, redis_client):
        self.db = db_session
        self.redis = redis_client
    
    def get_chat_history(self, user_id: str) -> List[dict]:
        # Query PostgreSQL for chat history
        # Use Redis for caching recent conversations
        pass
    
    def update_spaced_repetition(self, user_id: str, item_id: str, performance: str) -> dict:
        # Update spaced repetition in PostgreSQL
        # Update cache in Redis
        # Trigger background job for analytics
        pass
    
    # ... implement all other methods with proper database operations
"""
