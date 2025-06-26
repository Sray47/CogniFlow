"""
Test Suite for Learning Analytics Service

This comprehensive test suite validates the learning analytics functionality
in both development (no-database) and production modes.

Author: CogniFlow Development Team
Version: 1.0.0
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from httpx import AsyncClient
from fastapi.testclient import TestClient

from main import app, LearningEventType, LearningDifficulty, CompletionStatus


class TestLearningAnalyticsService:
    """Test class for Learning Analytics Service functionality"""
    
    def setup_method(self):
        """Setup method run before each test"""
        self.client = TestClient(app)
        self.test_user_id = "test_user_123"
        self.test_course_id = 1
        self.test_lesson_id = 1
    
    
    def test_service_health_check(self):
        """Test service health check endpoint"""
        response = self.client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["service"] == "CogniFlow Learning Analytics Service"
        assert data["status"] == "operational"
        assert data["version"] == "1.0.0"
        assert "mode" in data
    
    
    def test_health_endpoint(self):
        """Test dedicated health endpoint"""
        response = self.client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "learning-analytics-service"
        assert "timestamp" in data
    
    
    def test_record_learning_event_lesson_start(self):
        """Test recording a lesson start event"""
        event_data = {
            "user_id": self.test_user_id,
            "course_id": self.test_course_id,
            "lesson_id": self.test_lesson_id,
            "event_type": "lesson_start",
            "event_data": {
                "lesson_title": "Introduction to Machine Learning",
                "device": "desktop"
            }
        }
        
        response = self.client.post("/events", json=event_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "event_id" in data
        assert data["message"] == "Learning event recorded successfully"
        assert data["event_type"] == "lesson_start"
    
    
    def test_record_learning_event_lesson_complete(self):
        """Test recording a lesson completion event"""
        event_data = {
            "user_id": self.test_user_id,
            "course_id": self.test_course_id,
            "lesson_id": self.test_lesson_id,
            "event_type": "lesson_complete",
            "event_data": {
                "completion_time_minutes": 25,
                "quiz_score": 85
            }
        }
        
        response = self.client.post("/events", json=event_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "event_id" in data
        assert data["event_type"] == "lesson_complete"
    
    
    def test_update_learning_progress(self):
        """Test updating learning progress for a lesson"""
        progress_data = {
            "user_id": self.test_user_id,
            "course_id": self.test_course_id,
            "lesson_id": self.test_lesson_id,
            "completion_percentage": 75.0,
            "time_spent_minutes": 30,
            "difficulty_rating": "just_right",
            "notes": "Good introductory content, well explained"
        }
        
        response = self.client.put("/progress", json=progress_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "progress_id" in data
        assert data["message"] == "Progress updated successfully"
        assert data["completion_status"] == "in_progress"
    
    
    def test_update_progress_completion(self):
        """Test marking a lesson as completed"""
        progress_data = {
            "user_id": self.test_user_id,
            "course_id": self.test_course_id,
            "lesson_id": self.test_lesson_id,
            "completion_percentage": 100.0,
            "time_spent_minutes": 45,
            "difficulty_rating": "challenging"
        }
        
        response = self.client.put("/progress", json=progress_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["completion_status"] == "completed"
    
    
    def test_invalid_completion_percentage(self):
        """Test validation of completion percentage bounds"""
        progress_data = {
            "user_id": self.test_user_id,
            "course_id": self.test_course_id,
            "lesson_id": self.test_lesson_id,
            "completion_percentage": 150.0,  # Invalid: > 100
            "time_spent_minutes": 30
        }
        
        response = self.client.put("/progress", json=progress_data)
        assert response.status_code == 422  # Validation error
    
    
    def test_get_course_progress_new_user(self):
        """Test getting progress for a user with no existing data"""
        response = self.client.get(f"/progress/new_user_456/{self.test_course_id}")
        assert response.status_code == 404
        
        data = response.json()
        assert "No progress found" in data["detail"]
    
    
    def test_get_course_progress_existing_user(self):
        """Test getting progress for a user with existing data"""
        # First, create some progress data
        progress_data = {
            "user_id": self.test_user_id,
            "course_id": self.test_course_id,
            "lesson_id": 1,
            "completion_percentage": 100.0,
            "time_spent_minutes": 45,
            "difficulty_rating": "just_right"
        }
        self.client.put("/progress", json=progress_data)
        
        # Add progress for another lesson
        progress_data["lesson_id"] = 2
        progress_data["completion_percentage"] = 50.0
        progress_data["time_spent_minutes"] = 20
        self.client.put("/progress", json=progress_data)
        
        # Now get the course progress
        response = self.client.get(f"/progress/{self.test_user_id}/{self.test_course_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["user_id"] == self.test_user_id
        assert data["course_id"] == self.test_course_id
        assert data["lessons_completed"] == 1
        assert data["total_time_spent_minutes"] == 65
        assert data["completion_status"] == "in_progress"
        assert "course_title" in data
    
    
    def test_get_user_analytics_new_user(self):
        """Test getting analytics for a new user"""
        response = self.client.get("/analytics/new_user_789")
        assert response.status_code == 200
        
        data = response.json()
        assert data["user_id"] == "new_user_789"
        assert data["total_courses_enrolled"] == 0
        assert data["total_courses_completed"] == 0
        assert data["total_learning_time_hours"] == 0.0
        assert data["learning_velocity"] == 0.0
    
    
    def test_get_user_analytics_existing_user(self):
        """Test getting analytics for a user with learning data"""
        # Create progress data across multiple courses
        test_user = "analytics_test_user"
        
        # Course 1 progress
        for lesson_id in range(1, 4):
            progress_data = {
                "user_id": test_user,
                "course_id": 1,
                "lesson_id": lesson_id,
                "completion_percentage": 100.0,
                "time_spent_minutes": 30,
                "difficulty_rating": "just_right"
            }
            self.client.put("/progress", json=progress_data)
        
        # Course 2 progress (partial)
        progress_data = {
            "user_id": test_user,
            "course_id": 2,
            "lesson_id": 1,
            "completion_percentage": 75.0,
            "time_spent_minutes": 25
        }
        self.client.put("/progress", json=progress_data)
        
        # Get analytics
        response = self.client.get(f"/analytics/{test_user}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["user_id"] == test_user
        assert data["total_courses_enrolled"] == 2
        assert data["total_learning_time_hours"] > 0
        assert data["average_completion_rate"] > 0
    
    
    def test_record_learning_session(self):
        """Test recording a learning session"""
        session_start = datetime.utcnow()
        session_end = session_start + timedelta(minutes=45)
        
        session_data = {
            "user_id": self.test_user_id,
            "course_id": self.test_course_id,
            "session_start": session_start.isoformat(),
            "session_end": session_end.isoformat(),
            "lessons_accessed": [1, 2, 3],
            "total_engagement_score": 0.85
        }
        
        response = self.client.post("/sessions", json=session_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "session_id" in data
        assert data["message"] == "Learning session recorded successfully"
        assert "session_duration_minutes" in data
        assert data["session_duration_minutes"] == 45.0
    
    
    def test_learning_event_types(self):
        """Test various learning event types"""
        event_types = [
            "lesson_start",
            "lesson_complete", 
            "lesson_pause",
            "lesson_resume",
            "quiz_attempt",
            "quiz_complete",
            "course_enroll",
            "session_start",
            "session_end"
        ]
        
        for event_type in event_types:
            event_data = {
                "user_id": self.test_user_id,
                "course_id": self.test_course_id,
                "lesson_id": self.test_lesson_id,
                "event_type": event_type,
                "event_data": {"test": True}
            }
            
            response = self.client.post("/events", json=event_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["event_type"] == event_type
    
    
    def test_difficulty_rating_values(self):
        """Test all difficulty rating values"""
        difficulty_ratings = ["too_easy", "just_right", "challenging", "too_difficult"]
        
        for i, difficulty in enumerate(difficulty_ratings):
            progress_data = {
                "user_id": self.test_user_id,
                "course_id": self.test_course_id,
                "lesson_id": i + 10,  # Use different lesson IDs
                "completion_percentage": 100.0,
                "time_spent_minutes": 30,
                "difficulty_rating": difficulty
            }
            
            response = self.client.put("/progress", json=progress_data)
            assert response.status_code == 200
    
    
    def test_concurrent_progress_updates(self):
        """Test handling concurrent progress updates for the same lesson"""
        progress_data = {
            "user_id": self.test_user_id,
            "course_id": self.test_course_id,
            "lesson_id": 99,
            "completion_percentage": 50.0,
            "time_spent_minutes": 15
        }
        
        # First update
        response1 = self.client.put("/progress", json=progress_data)
        assert response1.status_code == 200
        
        # Second update (should update existing record)
        progress_data["completion_percentage"] = 100.0
        progress_data["time_spent_minutes"] = 20  # Additional time
        
        response2 = self.client.put("/progress", json=progress_data)
        assert response2.status_code == 200
        
        # Verify the progress was updated correctly
        response = self.client.get(f"/progress/{self.test_user_id}/{self.test_course_id}")
        assert response.status_code == 200
        
        # The total time should be cumulative (15 + 20 = 35 for this lesson)
        # Plus any other lessons for this user/course


@pytest.mark.asyncio
class TestAsyncLearningAnalytics:
    """Async test class for testing with async client"""
    
    @pytest.fixture
    async def async_client(self):
        """Async client fixture"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            yield client
    
    
    async def test_async_event_recording(self, async_client):
        """Test async event recording"""
        event_data = {
            "user_id": "async_user_123",
            "course_id": 1,
            "lesson_id": 1,
            "event_type": "lesson_start",
            "event_data": {"async_test": True}
        }
        
        response = await async_client.post("/events", json=event_data)
        assert response.status_code == 200
        
        data = response.json()
        assert data["event_type"] == "lesson_start"
    
    
    async def test_async_analytics_retrieval(self, async_client):
        """Test async analytics data retrieval"""
        # First create some data
        progress_data = {
            "user_id": "async_analytics_user",
            "course_id": 1,
            "lesson_id": 1,
            "completion_percentage": 100.0,
            "time_spent_minutes": 30
        }
        
        await async_client.put("/progress", json=progress_data)
        
        # Then retrieve analytics
        response = await async_client.get("/analytics/async_analytics_user")
        assert response.status_code == 200
        
        data = response.json()
        assert data["user_id"] == "async_analytics_user"


if __name__ == "__main__":
    """Run tests if script is executed directly"""
    pytest.main([__file__, "-v", "--tb=short"])
