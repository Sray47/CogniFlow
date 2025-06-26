"""
Learning Analytics Service - Data Store Abstraction
==================================================

This module provides data storage abstraction for the Learning Analytics service.
In development mode, it uses in-memory storage with event processing.
In production mode, it can be swapped with PostgreSQL/Redis implementations.

Key Features:
- Centralized event bus for analytics data
- Real-time learning progress tracking
- User behavior analytics and insights
- Course effectiveness metrics
- Predictive learning analytics
"""

import datetime
import uuid
import random
from typing import List, Dict, Optional, Any, Callable
from abc import ABC, abstractmethod
from collections import defaultdict


class EventType:
    """Standard event types for learning analytics"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    COURSE_ENROLLMENT = "course_enrollment"
    LESSON_STARTED = "lesson_started"
    LESSON_COMPLETED = "lesson_completed"
    QUIZ_STARTED = "quiz_started"
    QUIZ_COMPLETED = "quiz_completed"
    CHAT_INTERACTION = "chat_interaction"
    SPACED_REPETITION_REVIEW = "spaced_repetition_review"
    ACHIEVEMENT_EARNED = "achievement_earned"
    PROGRESS_UPDATED = "progress_updated"
    CONTENT_ACCESSED = "content_accessed"


class AnalyticsStoreInterface(ABC):
    """Abstract interface for Learning Analytics data storage"""
    
    @abstractmethod
    def record_event(self, event: dict):
        pass
    
    @abstractmethod
    def get_user_events(self, user_id: str, event_type: Optional[str] = None, limit: int = 100) -> List[dict]:
        pass
    
    @abstractmethod
    def get_system_events(self, event_type: Optional[str] = None, limit: int = 100) -> List[dict]:
        pass
    
    @abstractmethod
    def get_user_analytics(self, user_id: str) -> dict:
        pass
    
    @abstractmethod
    def get_course_analytics(self, course_id: str) -> dict:
        pass
    
    @abstractmethod
    def get_system_analytics(self) -> dict:
        pass
    
    @abstractmethod
    def add_event_listener(self, event_type: str, callback: Callable):
        pass


class InMemoryAnalyticsStore(AnalyticsStoreInterface):
    """
    In-memory implementation of Analytics store for development mode.
    
    Features:
    - Event bus with real-time processing
    - User behavior tracking and analysis
    - Course effectiveness metrics
    - System-wide analytics and insights
    - Event listeners for real-time reactions
    """
    
    def __init__(self):
        # Core event storage
        self.events = []  # All events in chronological order
        self.user_events = defaultdict(list)  # user_id -> events
        self.course_events = defaultdict(list)  # course_id -> events
        self.event_type_index = defaultdict(list)  # event_type -> events
        
        # Analytics data
        self.user_analytics = {}  # user_id -> analytics summary
        self.course_analytics = {}  # course_id -> analytics summary
        self.system_analytics = {}  # system-wide metrics
        
        # Event listeners for real-time processing
        self.event_listeners = defaultdict(list)  # event_type -> list of callbacks
        
        # Cache for expensive computations
        self.analytics_cache = {}
        self.cache_expiry = {}
        
        # Initialize with sample data
        self._init_sample_data()
        
        # Set up default event listeners
        self._setup_default_listeners()
    
    def _init_sample_data(self):
        """Initialize with sample analytics data"""
        sample_users = ["user1", "user2", "user3"]
        sample_courses = ["python_basics", "web_development", "data_science"]
        
        # Generate sample events from the past 30 days
        for _ in range(500):  # 500 sample events
            user_id = random.choice(sample_users)
            course_id = random.choice(sample_courses)
            event_type = random.choice([
                EventType.USER_LOGIN,
                EventType.LESSON_COMPLETED,
                EventType.QUIZ_COMPLETED,
                EventType.CHAT_INTERACTION,
                EventType.ACHIEVEMENT_EARNED,
                EventType.COURSE_ENROLLMENT
            ])
            
            # Generate realistic event data based on type
            event_data = self._generate_sample_event_data(event_type, user_id, course_id)
            
            # Create event with timestamp in the past 30 days
            event = {
                "event_id": str(uuid.uuid4()),
                "user_id": user_id,
                "event_type": event_type,
                "event_data": event_data,
                "timestamp": datetime.datetime.now() - datetime.timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                ),
                "session_id": f"session_{random.randint(1000, 9999)}"
            }
            
            self._store_event(event)
    
    def _generate_sample_event_data(self, event_type: str, user_id: str, course_id: str) -> dict:
        """Generate realistic sample event data based on event type"""
        if event_type == EventType.USER_LOGIN:
            return {
                "login_method": random.choice(["email", "social", "sso"]),
                "device_type": random.choice(["desktop", "mobile", "tablet"]),
                "location": random.choice(["New York", "London", "Tokyo", "Sydney"])
            }
        elif event_type == EventType.LESSON_COMPLETED:
            return {
                "course_id": course_id,
                "lesson_id": f"lesson_{random.randint(1, 20)}",
                "duration_minutes": random.randint(5, 45),
                "completion_rate": random.uniform(0.8, 1.0),
                "engagement_score": random.uniform(0.6, 1.0)
            }
        elif event_type == EventType.QUIZ_COMPLETED:
            return {
                "course_id": course_id,
                "quiz_id": f"quiz_{random.randint(1, 10)}",
                "score": random.randint(60, 100),
                "total_questions": random.randint(5, 20),
                "time_taken_minutes": random.randint(3, 30),
                "attempts": random.randint(1, 3)
            }
        elif event_type == EventType.CHAT_INTERACTION:
            return {
                "message_length": random.randint(10, 200),
                "response_time_ms": random.randint(500, 3000),
                "topic": random.choice(["python", "javascript", "math", "general"]),
                "satisfaction_rating": random.randint(3, 5)
            }
        elif event_type == EventType.ACHIEVEMENT_EARNED:
            return {
                "achievement_id": f"achievement_{random.randint(1, 20)}",
                "achievement_type": random.choice(["milestone", "streak", "performance", "social"]),
                "points_awarded": random.randint(10, 100)
            }
        elif event_type == EventType.COURSE_ENROLLMENT:
            return {
                "course_id": course_id,
                "enrollment_method": random.choice(["direct", "recommendation", "search"]),
                "price_paid": random.choice([0, 29.99, 49.99, 99.99])
            }
        else:
            return {}
    
    def _store_event(self, event: dict):
        """Store event in all relevant indices"""
        self.events.append(event)
        self.user_events[event["user_id"]].append(event)
        self.event_type_index[event["event_type"]].append(event)
        
        # Store course events if course_id is present
        if "course_id" in event.get("event_data", {}):
            course_id = event["event_data"]["course_id"]
            self.course_events[course_id].append(event)
        
        # Keep only recent events for memory management
        max_events = 10000
        if len(self.events) > max_events:
            self.events = self.events[-max_events:]
    
    def _setup_default_listeners(self):
        """Set up default event listeners for real-time analytics"""
        self.add_event_listener(EventType.USER_LOGIN, self._handle_user_login)
        self.add_event_listener(EventType.LESSON_COMPLETED, self._handle_lesson_completion)
        self.add_event_listener(EventType.QUIZ_COMPLETED, self._handle_quiz_completion)
        self.add_event_listener(EventType.ACHIEVEMENT_EARNED, self._handle_achievement_earned)
    
    def _handle_user_login(self, event: dict):
        """Handle user login event for real-time analytics"""
        user_id = event["user_id"]
        if user_id not in self.user_analytics:
            self.user_analytics[user_id] = {
                "total_logins": 0,
                "last_login": None,
                "login_streak": 0,
                "devices_used": set(),
                "locations": set()
            }
        
        analytics = self.user_analytics[user_id]
        analytics["total_logins"] += 1
        analytics["last_login"] = event["timestamp"]
        
        event_data = event.get("event_data", {})
        if "device_type" in event_data:
            analytics["devices_used"].add(event_data["device_type"])
        if "location" in event_data:
            analytics["locations"].add(event_data["location"])
    
    def _handle_lesson_completion(self, event: dict):
        """Handle lesson completion for real-time analytics"""
        user_id = event["user_id"]
        event_data = event.get("event_data", {})
        
        if user_id not in self.user_analytics:
            self.user_analytics[user_id] = {"lessons_completed": 0, "total_study_time": 0}
        
        self.user_analytics[user_id]["lessons_completed"] = self.user_analytics[user_id].get("lessons_completed", 0) + 1
        self.user_analytics[user_id]["total_study_time"] = self.user_analytics[user_id].get("total_study_time", 0) + event_data.get("duration_minutes", 0)
    
    def _handle_quiz_completion(self, event: dict):
        """Handle quiz completion for real-time analytics"""
        user_id = event["user_id"]
        event_data = event.get("event_data", {})
        
        if user_id not in self.user_analytics:
            self.user_analytics[user_id] = {"quizzes_completed": 0, "average_quiz_score": 0}
        
        current_quizzes = self.user_analytics[user_id].get("quizzes_completed", 0)
        current_avg = self.user_analytics[user_id].get("average_quiz_score", 0)
        new_score = event_data.get("score", 0)
        
        self.user_analytics[user_id]["quizzes_completed"] = current_quizzes + 1
        self.user_analytics[user_id]["average_quiz_score"] = ((current_avg * current_quizzes) + new_score) / (current_quizzes + 1)
    
    def _handle_achievement_earned(self, event: dict):
        """Handle achievement earned for real-time analytics"""
        user_id = event["user_id"]
        
        if user_id not in self.user_analytics:
            self.user_analytics[user_id] = {"achievements_earned": 0, "total_achievement_points": 0}
        
        self.user_analytics[user_id]["achievements_earned"] = self.user_analytics[user_id].get("achievements_earned", 0) + 1
        points = event.get("event_data", {}).get("points_awarded", 0)
        self.user_analytics[user_id]["total_achievement_points"] = self.user_analytics[user_id].get("total_achievement_points", 0) + points
    
    def record_event(self, event: dict):
        """Record a new analytics event"""
        # Add timestamp if not provided
        if "timestamp" not in event:
            event["timestamp"] = datetime.datetime.now()
        
        # Add event ID if not provided
        if "event_id" not in event:
            event["event_id"] = str(uuid.uuid4())
        
        # Store the event
        self._store_event(event)
        
        # Trigger event listeners
        event_type = event.get("event_type")
        if event_type in self.event_listeners:
            for callback in self.event_listeners[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in event listener for {event_type}: {e}")
        
        # Invalidate relevant caches
        self._invalidate_cache(event)
    
    def get_user_events(self, user_id: str, event_type: Optional[str] = None, limit: int = 100) -> List[dict]:
        """Get events for a specific user"""
        user_events = self.user_events.get(user_id, [])
        
        if event_type:
            user_events = [event for event in user_events if event.get("event_type") == event_type]
        
        # Sort by timestamp descending and limit
        user_events.sort(key=lambda x: x.get("timestamp", datetime.datetime.min), reverse=True)
        return user_events[:limit]
    
    def get_system_events(self, event_type: Optional[str] = None, limit: int = 100) -> List[dict]:
        """Get system-wide events"""
        if event_type:
            events = self.event_type_index.get(event_type, [])
        else:
            events = self.events
        
        # Sort by timestamp descending and limit
        events.sort(key=lambda x: x.get("timestamp", datetime.datetime.min), reverse=True)
        return events[:limit]
    
    def get_user_analytics(self, user_id: str) -> dict:
        """Get comprehensive analytics for a user"""
        cache_key = f"user_analytics_{user_id}"
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            return self.analytics_cache[cache_key]
        
        # Compute analytics
        user_events = self.user_events.get(user_id, [])
        
        if not user_events:
            return {}
        
        # Basic metrics
        analytics = {
            "user_id": user_id,
            "total_events": len(user_events),
            "first_activity": min(event["timestamp"] for event in user_events) if user_events else None,
            "last_activity": max(event["timestamp"] for event in user_events) if user_events else None,
            "event_breakdown": {}
        }
        
        # Event type breakdown
        for event in user_events:
            event_type = event.get("event_type", "unknown")
            analytics["event_breakdown"][event_type] = analytics["event_breakdown"].get(event_type, 0) + 1
        
        # Learning patterns
        analytics["learning_patterns"] = self._analyze_learning_patterns(user_events)
        
        # Performance metrics
        analytics["performance"] = self._analyze_user_performance(user_events)
        
        # Engagement metrics
        analytics["engagement"] = self._analyze_user_engagement(user_events)
        
        # Real-time analytics from listeners
        if user_id in self.user_analytics:
            analytics["real_time_metrics"] = self.user_analytics[user_id]
        
        # Cache the result
        self.analytics_cache[cache_key] = analytics
        self.cache_expiry[cache_key] = datetime.datetime.now() + datetime.timedelta(minutes=15)
        
        return analytics
    
    def get_course_analytics(self, course_id: str) -> dict:
        """Get comprehensive analytics for a course"""
        cache_key = f"course_analytics_{course_id}"
        
        if self._is_cache_valid(cache_key):
            return self.analytics_cache[cache_key]
        
        course_events = self.course_events.get(course_id, [])
        
        if not course_events:
            return {}
        
        analytics = {
            "course_id": course_id,
            "total_events": len(course_events),
            "unique_users": len(set(event["user_id"] for event in course_events)),
            "event_breakdown": {}
        }
        
        # Event breakdown
        for event in course_events:
            event_type = event.get("event_type", "unknown")
            analytics["event_breakdown"][event_type] = analytics["event_breakdown"].get(event_type, 0) + 1
        
        # Course effectiveness metrics
        analytics["effectiveness"] = self._analyze_course_effectiveness(course_events)
        
        # Cache the result
        self.analytics_cache[cache_key] = analytics
        self.cache_expiry[cache_key] = datetime.datetime.now() + datetime.timedelta(minutes=30)
        
        return analytics
    
    def get_system_analytics(self) -> dict:
        """Get system-wide analytics"""
        cache_key = "system_analytics"
        
        if self._is_cache_valid(cache_key):
            return self.analytics_cache[cache_key]
        
        now = datetime.datetime.now()
        
        analytics = {
            "total_events": len(self.events),
            "total_users": len(self.user_events),
            "total_courses": len(self.course_events),
            "events_by_type": {},
            "daily_activity": self._get_daily_activity(),
            "top_active_users": self._get_top_active_users(),
            "generated_at": now.isoformat()
        }
        
        # Events by type
        for event_type, events in self.event_type_index.items():
            analytics["events_by_type"][event_type] = len(events)
        
        # System health metrics
        analytics["system_health"] = {
            "average_events_per_user": len(self.events) / max(len(self.user_events), 1),
            "events_last_24h": len([e for e in self.events if (now - e["timestamp"]).total_seconds() < 86400]),
            "active_users_last_24h": len(set(e["user_id"] for e in self.events if (now - e["timestamp"]).total_seconds() < 86400))
        }
        
        # Cache the result
        self.analytics_cache[cache_key] = analytics
        self.cache_expiry[cache_key] = datetime.datetime.now() + datetime.timedelta(minutes=10)
        
        return analytics
    
    def add_event_listener(self, event_type: str, callback: Callable):
        """Add an event listener for real-time processing"""
        self.event_listeners[event_type].append(callback)
    
    def _analyze_learning_patterns(self, user_events: List[dict]) -> dict:
        """Analyze user learning patterns"""
        # Time-based patterns
        hours = [event["timestamp"].hour for event in user_events]
        days = [event["timestamp"].weekday() for event in user_events]
        
        # Most active hour and day
        from collections import Counter
        hour_counter = Counter(hours)
        day_counter = Counter(days)
        
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        return {
            "most_active_hour": hour_counter.most_common(1)[0][0] if hour_counter else None,
            "most_active_day": day_names[day_counter.most_common(1)[0][0]] if day_counter else None,
            "session_frequency": len(set(event.get("session_id") for event in user_events if event.get("session_id"))),
            "learning_consistency": self._calculate_consistency_score(user_events)
        }
    
    def _analyze_user_performance(self, user_events: List[dict]) -> dict:
        """Analyze user performance metrics"""
        quiz_events = [e for e in user_events if e.get("event_type") == EventType.QUIZ_COMPLETED]
        lesson_events = [e for e in user_events if e.get("event_type") == EventType.LESSON_COMPLETED]
        
        performance = {
            "total_quizzes": len(quiz_events),
            "total_lessons": len(lesson_events),
            "average_quiz_score": 0,
            "quiz_improvement_trend": "stable"
        }
        
        if quiz_events:
            scores = [e.get("event_data", {}).get("score", 0) for e in quiz_events]
            performance["average_quiz_score"] = sum(scores) / len(scores)
            
            # Calculate improvement trend
            if len(scores) >= 3:
                recent_avg = sum(scores[-3:]) / 3
                older_avg = sum(scores[:-3]) / max(len(scores) - 3, 1)
                if recent_avg > older_avg + 5:
                    performance["quiz_improvement_trend"] = "improving"
                elif recent_avg < older_avg - 5:
                    performance["quiz_improvement_trend"] = "declining"
        
        return performance
    
    def _analyze_user_engagement(self, user_events: List[dict]) -> dict:
        """Analyze user engagement metrics"""
        if not user_events:
            return {}
        
        now = datetime.datetime.now()
        last_week = now - datetime.timedelta(days=7)
        last_month = now - datetime.timedelta(days=30)
        
        recent_events = [e for e in user_events if e["timestamp"] > last_week]
        monthly_events = [e for e in user_events if e["timestamp"] > last_month]
        
        return {
            "events_last_week": len(recent_events),
            "events_last_month": len(monthly_events),
            "engagement_trend": "increasing" if len(recent_events) > len(monthly_events) / 4 else "stable",
            "favorite_activity": self._get_most_common_event_type(user_events),
            "session_length_avg": self._calculate_average_session_length(user_events)
        }
    
    def _analyze_course_effectiveness(self, course_events: List[dict]) -> dict:
        """Analyze course effectiveness metrics"""
        enrollments = len([e for e in course_events if e.get("event_type") == EventType.COURSE_ENROLLMENT])
        completions = len([e for e in course_events if e.get("event_type") == EventType.LESSON_COMPLETED])
        quiz_events = [e for e in course_events if e.get("event_type") == EventType.QUIZ_COMPLETED]
        
        effectiveness = {
            "enrollment_count": enrollments,
            "completion_rate": completions / max(enrollments, 1),
            "average_quiz_performance": 0,
            "student_satisfaction": 0
        }
        
        if quiz_events:
            scores = [e.get("event_data", {}).get("score", 0) for e in quiz_events]
            effectiveness["average_quiz_performance"] = sum(scores) / len(scores)
        
        return effectiveness
    
    def _get_daily_activity(self) -> dict:
        """Get daily activity over the past 30 days"""
        now = datetime.datetime.now()
        daily_counts = {}
        
        for i in range(30):
            date = (now - datetime.timedelta(days=i)).date()
            daily_counts[date.isoformat()] = 0
        
        for event in self.events:
            if (now - event["timestamp"]).days <= 30:
                date = event["timestamp"].date()
                if date.isoformat() in daily_counts:
                    daily_counts[date.isoformat()] += 1
        
        return daily_counts
    
    def _get_top_active_users(self, limit: int = 10) -> List[dict]:
        """Get most active users"""
        user_activity = {}
        for user_id, events in self.user_events.items():
            user_activity[user_id] = len(events)
        
        sorted_users = sorted(user_activity.items(), key=lambda x: x[1], reverse=True)
        return [{"user_id": user_id, "event_count": count} for user_id, count in sorted_users[:limit]]
    
    def _calculate_consistency_score(self, user_events: List[dict]) -> float:
        """Calculate learning consistency score (0-1)"""
        if len(user_events) < 2:
            return 0.0
        
        # Calculate variance in daily activity
        daily_activity = {}
        for event in user_events:
            date = event["timestamp"].date()
            daily_activity[date] = daily_activity.get(date, 0) + 1
        
        if len(daily_activity) < 2:
            return 0.5
        
        values = list(daily_activity.values())
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        
        # Convert variance to consistency score (lower variance = higher consistency)
        consistency = max(0.0, 1.0 - (variance / (mean + 1)))
        return consistency
    
    def _get_most_common_event_type(self, user_events: List[dict]) -> str:
        """Get the most common event type for a user"""
        from collections import Counter
        event_types = [e.get("event_type", "unknown") for e in user_events]
        counter = Counter(event_types)
        return counter.most_common(1)[0][0] if counter else "unknown"
    
    def _calculate_average_session_length(self, user_events: List[dict]) -> float:
        """Calculate average session length in minutes"""
        sessions = {}
        for event in user_events:
            session_id = event.get("session_id")
            if session_id:
                if session_id not in sessions:
                    sessions[session_id] = {"start": event["timestamp"], "end": event["timestamp"]}
                else:
                    if event["timestamp"] < sessions[session_id]["start"]:
                        sessions[session_id]["start"] = event["timestamp"]
                    if event["timestamp"] > sessions[session_id]["end"]:
                        sessions[session_id]["end"] = event["timestamp"]
        
        if not sessions:
            return 0.0
        
        total_minutes = sum((session["end"] - session["start"]).total_seconds() / 60 for session in sessions.values())
        return total_minutes / len(sessions)
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.analytics_cache:
            return False
        
        expiry = self.cache_expiry.get(cache_key)
        if not expiry or datetime.datetime.now() > expiry:
            return False
        
        return True
    
    def _invalidate_cache(self, event: dict):
        """Invalidate relevant caches when new events are recorded"""
        user_id = event.get("user_id")
        course_id = event.get("event_data", {}).get("course_id")
        
        # Invalidate user-specific cache
        if user_id:
            cache_key = f"user_analytics_{user_id}"
            if cache_key in self.analytics_cache:
                del self.analytics_cache[cache_key]
        
        # Invalidate course-specific cache
        if course_id:
            cache_key = f"course_analytics_{course_id}"
            if cache_key in self.analytics_cache:
                del self.analytics_cache[cache_key]
        
        # Invalidate system cache
        if "system_analytics" in self.analytics_cache:
            del self.analytics_cache["system_analytics"]


# Production implementation interface:
"""
class PostgreSQLAnalyticsStore(AnalyticsStoreInterface):
    def __init__(self, db_session, redis_client):
        self.db = db_session
        self.redis = redis_client
        self.event_queue = []  # For batch processing

    def record_event(self, event: dict):
        # Store in PostgreSQL for persistence
        # Cache in Redis for fast access
        # Queue for batch analytics processing
        pass

    def get_user_analytics(self, user_id: str) -> dict:
        # Query PostgreSQL with optimized queries
        # Use materialized views for complex analytics
        # Cache results in Redis
        pass

    # ... implement all other methods with proper database operations
"""
