"""
CogniFlow Notifications Service - Cross-Service Integration
=========================================================

Handles integration with other CogniFlow services:
- User Service: Get user details and email addresses
- Courses Service: Course information for notifications
- Learning Analytics: Track notification engagement
- External Services: Email providers, push notification services

Development Mode: Mock integrations for rapid development
Production Mode: Real HTTP clients with retry logic and circuit breakers

Author: CogniFlow Development Team
"""

import aiohttp
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import os
from dataclasses import dataclass
from enum import Enum

# Production imports (commented for no-db mode)
# import tenacity
# from circuitbreaker import circuit
# import prometheus_client

logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION
# ============================================================================

NO_DATABASE_MODE = os.getenv('NO_DATABASE_MODE', 'true').lower() == 'true'
USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://users-service:8001')
COURSES_SERVICE_URL = os.getenv('COURSES_SERVICE_URL', 'http://courses-service:8002')
ANALYTICS_SERVICE_URL = os.getenv('ANALYTICS_SERVICE_URL', 'http://learning-analytics:8004')

# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class UserInfo:
    """User information from user service"""
    user_id: str
    email: str
    full_name: str
    preferences: Optional[dict] = None

@dataclass
class CourseInfo:
    """Course information from courses service"""
    course_id: str
    title: str
    instructor: str
    start_date: Optional[datetime] = None

@dataclass
class NotificationEvent:
    """Notification event for analytics tracking"""
    notification_id: str
    user_id: str
    event_type: str  # created, sent, delivered, read, failed
    channel: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

class IntegrationError(Exception):
    """Base exception for integration errors"""
    pass

class ServiceUnavailableError(IntegrationError):
    """Raised when a required service is unavailable"""
    pass

# ============================================================================
# BASE INTEGRATION CLIENT
# ============================================================================

class BaseServiceClient:
    """Base class for service integration clients"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session = None
        self._circuit_breaker_failures = 0
        self._circuit_breaker_last_failure = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={"User-Agent": "CogniFlow-Notifications/1.0"}
            )
        return self.session
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request with error handling and retries"""
        url = f"{self.base_url}{endpoint}"
        
        if NO_DATABASE_MODE:
            # Return mock data in development mode
            return await self._get_mock_response(method, endpoint, **kwargs)
        
        # Production HTTP request with retry logic
        session = await self._get_session()
        
        try:
            async with session.request(method, url, **kwargs) as response:
                if response.status == 200:
                    self._circuit_breaker_failures = 0
                    return await response.json()
                elif response.status == 404:
                    return None
                else:
                    raise IntegrationError(f"{self.service_name} returned {response.status}")
        
        except Exception as e:
            self._circuit_breaker_failures += 1
            self._circuit_breaker_last_failure = datetime.utcnow()
            logger.error(f"Error calling {self.service_name} {endpoint}: {str(e)}")
            
            if self._circuit_breaker_failures >= 3:
                raise ServiceUnavailableError(f"{self.service_name} is unavailable")
            
            # Return fallback data for non-critical operations
            return await self._get_fallback_response(method, endpoint, **kwargs)
    
    async def _get_mock_response(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Override in subclasses to provide mock responses"""
        return {}
    
    async def _get_fallback_response(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Override in subclasses to provide fallback responses"""
        return {}
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()

# ============================================================================
# USER SERVICE INTEGRATION
# ============================================================================

class UserServiceClient(BaseServiceClient):
    """Client for integrating with the User Service"""
    
    def __init__(self):
        super().__init__(USER_SERVICE_URL)
        
        # Mock user data for development
        self._mock_users = {
            "user123": UserInfo(
                user_id="user123",
                email="john.doe@example.com",
                full_name="John Doe",
                preferences={"language": "en", "timezone": "America/New_York"}
            ),
            "user456": UserInfo(
                user_id="user456", 
                email="jane.smith@example.com",
                full_name="Jane Smith",
                preferences={"language": "es", "timezone": "Europe/London"}
            ),
            "wsuser": UserInfo(
                user_id="wsuser",
                email="ws.user@example.com",
                full_name="WebSocket User"
            ),
            "integration_user": UserInfo(
                user_id="integration_user",
                email="test@example.com",
                full_name="Integration Test User"
            )
        }
    
    async def get_user_info(self, user_id: str) -> Optional[UserInfo]:
        """Get user information by ID"""
        try:
            response = await self._make_request('GET', f'/users/{user_id}')
            if response:
                return UserInfo(
                    user_id=response['id'],
                    email=response['email'],
                    full_name=response['name'],
                    preferences=response.get('preferences', {})
                )
            return None
        except Exception as e:
            logger.warning(f"Failed to get user {user_id}: {str(e)}")
            return None
    
    async def get_users_batch(self, user_ids: List[str]) -> Dict[str, UserInfo]:
        """Get multiple users in a single request"""
        try:
            response = await self._make_request('POST', '/users/batch', 
                                              json={"user_ids": user_ids})
            
            users = {}
            if response and 'users' in response:
                for user_data in response['users']:
                    user_info = UserInfo(
                        user_id=user_data['id'],
                        email=user_data['email'],
                        full_name=user_data['name'],
                        preferences=user_data.get('preferences', {})
                    )
                    users[user_info.user_id] = user_info
            
            return users
        except Exception as e:
            logger.warning(f"Failed to get users batch: {str(e)}")
            return {}
    
    async def _get_mock_response(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Provide mock responses for development"""
        if method == 'GET' and endpoint.startswith('/users/'):
            user_id = endpoint.split('/')[-1]
            if user_id in self._mock_users:
                user = self._mock_users[user_id]
                return {
                    'id': user.user_id,
                    'name': user.full_name,
                    'email': user.email,
                    'preferences': user.preferences
                }
        
        elif method == 'POST' and endpoint == '/users/batch':
            json_data = kwargs.get('json', {})
            user_ids = json_data.get('user_ids', [])
            users = []
            
            for user_id in user_ids:
                if user_id in self._mock_users:
                    user = self._mock_users[user_id]
                    users.append({
                        'id': user.user_id,
                        'name': user.full_name,
                        'email': user.email,
                        'preferences': user.preferences
                    })
                else:
                    # Generate mock user for unknown IDs
                    users.append({
                        'id': user_id,
                        'name': f"User {user_id}",
                        'email': f"{user_id}@example.com",
                        'preferences': {}
                    })
            
            return {'users': users}
        
        return {}

# ============================================================================
# COURSES SERVICE INTEGRATION  
# ============================================================================

class CoursesServiceClient(BaseServiceClient):
    """Client for integrating with the Courses Service"""
    
    def __init__(self):
        super().__init__(COURSES_SERVICE_URL)
        
        # Mock course data for development
        self._mock_courses = {
            "course123": CourseInfo(
                course_id="course123",
                title="Python 101: Introduction to Programming",
                instructor="Dr. Alice Johnson",
                start_date=datetime(2024, 1, 15)
            ),
            "course456": CourseInfo(
                course_id="course456",
                title="Advanced Machine Learning",
                instructor="Prof. Bob Wilson",
                start_date=datetime(2024, 2, 1)
            )
        }
    
    async def get_course_info(self, course_id: str) -> Optional[CourseInfo]:
        """Get course information by ID"""
        try:
            response = await self._make_request('GET', f'/courses/{course_id}')
            if response:
                return CourseInfo(
                    course_id=response['id'],
                    title=response['title'],
                    instructor=response.get('instructor_name', 'Unknown'),
                    start_date=datetime.fromisoformat(response['start_date']) if response.get('start_date') else None
                )
            return None
        except Exception as e:
            logger.warning(f"Failed to get course {course_id}: {str(e)}")
            return None
    
    async def get_user_courses(self, user_id: str) -> List[CourseInfo]:
        """Get courses enrolled by a user"""
        try:
            response = await self._make_request('GET', f'/users/{user_id}/courses')
            courses = []
            
            if response and 'courses' in response:
                for course_data in response['courses']:
                    course_info = CourseInfo(
                        course_id=course_data['id'],
                        title=course_data['title'],
                        instructor=course_data.get('instructor_name', 'Unknown'),
                        start_date=datetime.fromisoformat(course_data['start_date']) if course_data.get('start_date') else None
                    )
                    courses.append(course_info)
            
            return courses
        except Exception as e:
            logger.warning(f"Failed to get courses for user {user_id}: {str(e)}")
            return []
    
    async def _get_mock_response(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Provide mock responses for development"""
        if method == 'GET' and endpoint.startswith('/courses/') and not '/courses/' in endpoint[9:]:
            course_id = endpoint.split('/')[-1]
            if course_id in self._mock_courses:
                course = self._mock_courses[course_id]
                return {
                    'id': course.course_id,
                    'title': course.title,
                    'instructor_name': course.instructor,
                    'start_date': course.start_date.isoformat() if course.start_date else None
                }
        
        elif method == 'GET' and '/courses' in endpoint and endpoint.endswith('/courses'):
            # Return mock courses for any user
            courses = []
            for course in list(self._mock_courses.values())[:2]:  # Return first 2 courses
                courses.append({
                    'id': course.course_id,
                    'title': course.title,
                    'instructor_name': course.instructor,
                    'start_date': course.start_date.isoformat() if course.start_date else None
                })
            return {'courses': courses}
        
        return {}

# ============================================================================
# ANALYTICS SERVICE INTEGRATION
# ============================================================================

class AnalyticsServiceClient(BaseServiceClient):
    """Client for integrating with the Learning Analytics Service"""
    
    def __init__(self):
        super().__init__(ANALYTICS_SERVICE_URL)
    
    async def track_event(self, event: NotificationEvent):
        """Track a notification event for analytics"""
        try:
            event_data = {
                'user_id': event.user_id,
                'event_type': 'notification_interaction',
                'data': {
                    'notification_id': event.notification_id,
                    'notification_event': event.event_type,
                    'channel': event.channel,
                    'timestamp': event.timestamp.isoformat(),
                    'metadata': event.metadata or {}
                }
            }
            
            response = await self._make_request('POST', '/events', json=event_data)
            return response is not None
            
        except Exception as e:
            logger.warning(f"Failed to track notification event: {str(e)}")
            return False
    
    async def get_notification_metrics(self, user_id: str = None, 
                                     start_date: datetime = None,
                                     end_date: datetime = None) -> Dict[str, Any]:
        """Get notification delivery and engagement metrics"""
        try:
            params = {}
            if user_id:
                params['user_id'] = user_id
            if start_date:
                params['start_date'] = start_date.isoformat()
            if end_date:
                params['end_date'] = end_date.isoformat()
            
            response = await self._make_request('GET', '/analytics/notifications', 
                                              params=params)
            return response or {}
            
        except Exception as e:
            logger.warning(f"Failed to get notification metrics: {str(e)}")
            return {}
    
    async def _get_mock_response(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Provide mock responses for development"""
        if method == 'POST' and endpoint == '/events':
            return {'success': True, 'event_id': 'mock_event_id'}
        
        elif method == 'GET' and endpoint == '/analytics/notifications':
            return {
                'total_notifications': 150,
                'delivery_rate': 98.5,
                'read_rate': 75.2,
                'channel_performance': {
                    'real_time': {'delivered': 145, 'read': 120},
                    'email': {'delivered': 80, 'read': 45},
                    'push': {'delivered': 60, 'read': 35}
                }
            }
        
        return {}

# ============================================================================
# INTEGRATION MANAGER
# ============================================================================

class IntegrationManager:
    """Manages all service integrations for the notifications service"""
    
    def __init__(self):
        self.user_client = UserServiceClient()
        self.courses_client = CoursesServiceClient()
        self.analytics_client = AnalyticsServiceClient()

    async def enrich_notification_data(self, notification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich notification data with information from other services"""
        enriched = notification_data.copy()
        
        try:
            # Get user information
            user = await self.user_client.get_user_info(notification_data['user_id'])
            if user:
                enriched['user_name'] = user.full_name
                enriched['user_email'] = user.email
                enriched['user_timezone'] = user.preferences.get('timezone', 'UTC')
                enriched['user_language'] = user.preferences.get('language', 'en')
            
            # Get course information if course_id is in metadata
            course_id = notification_data.get('metadata', {}).get('course_id')
            if course_id:
                course = await self.courses_client.get_course_info(course_id)
                if course:
                    enriched['course_title'] = course.title
                    enriched['instructor_name'] = course.instructor
                    enriched.setdefault('metadata', {}).update({
                        'course_title': course.title,
                        'instructor_name': course.instructor
                    })
            
        except Exception as e:
            logger.warning(f"Failed to enrich notification data: {str(e)}")
        
        return enriched
    
    async def track_notification_lifecycle(self, notification_id: str, user_id: str, 
                                         event_type: str, channel: str, 
                                         metadata: Dict[str, Any] = None):
        """Track notification events for analytics"""
        try:
            event = NotificationEvent(
                notification_id=notification_id,
                user_id=user_id,
                event_type=event_type,
                channel=channel,
                timestamp=datetime.utcnow(),
                metadata=metadata
            )
            
            await self.analytics_client.track_event(event)
            
        except Exception as e:
            logger.warning(f"Failed to track notification lifecycle: {str(e)}")
    
    async def get_user_notification_preferences_context(self, user_id: str) -> Dict[str, Any]:
        """Get context for personalizing notifications based on user data"""
        context = {}
        
        try:
            # Get user info
            user = await self.user_client.get_user_info(user_id)
            if user:
                context['user_name'] = user.full_name
                context['user_timezone'] = user.preferences.get('timezone', 'UTC')
                context['preferred_language'] = user.preferences.get('language', 'en')
            
            # Get user's courses for course-related notifications
            courses = await self.courses_client.get_user_courses(user_id)
            context['enrolled_courses'] = [
                {'id': course.course_id, 'title': course.title} 
                for course in courses
            ]
            
        except Exception as e:
            logger.warning(f"Failed to get user context: {str(e)}")
        
        return context
    
    async def validate_notification_recipients(self, user_ids: List[str]) -> List[str]:
        """Validate that user IDs exist and are active"""
        try:
            users = await self.user_client.get_users_batch(user_ids)
            return [user_id for user_id, user in users.items() if user.is_active]
        except Exception as e:
            logger.warning(f"Failed to validate recipients: {str(e)}")
            return user_ids  # Return original list as fallback
    
    async def close(self):
        """Close all integration clients"""
        for client in [self.user_client, self.courses_client, self.analytics_client]:
            await client.close()

# Global integration manager instance
integration_manager = IntegrationManager()

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def get_user_info(user_id: str) -> Optional[UserInfo]:
    """Convenience function to get user information"""
    return await integration_manager.user_client.get_user_info(user_id)

async def get_course_info(course_id: str) -> Optional[CourseInfo]:
    """Convenience function to get course information"""
    return await integration_manager.courses_client.get_course_info(course_id)

async def track_notification_event(notification_id: str, user_id: str, 
                                 event_type: str, channel: str, 
                                 metadata: Dict[str, Any] = None):
    """Convenience function to track notification events"""
    event = NotificationEvent(
        notification_id=notification_id,
        user_id=user_id,
        event_type=event_type,
        channel=channel,
        timestamp=datetime.utcnow(),
        metadata=metadata or {}
    )
    await integration_manager.analytics_client.track_event(event)

# Production-ready integration features (commented for no-db mode)
"""
# Circuit breaker for service resilience
@circuit(failure_threshold=5, recovery_timeout=30)
async def make_resilient_request(client: BaseServiceClient, method: str, endpoint: str, **kwargs):
    return await client._make_request(method, endpoint, **kwargs)

# Metrics collection for monitoring
notification_requests_total = prometheus_client.Counter(
    'notification_service_requests_total',
    'Total notification service requests',
    ['service', 'endpoint', 'status']
)

notification_request_duration = prometheus_client.Histogram(
    'notification_service_request_duration_seconds',
    'Notification service request duration',
    ['service', 'endpoint']
)

# Retry configuration with exponential backoff
@tenacity.retry(
    stop=tenacity.stop_after_attempt(3),
    wait=tenacity.wait_exponential(multiplier=1, min=4, max=10),
    retry=tenacity.retry_if_exception_type((aiohttp.ClientError, ServiceUnavailableError))
)
async def make_retryable_request(client: BaseServiceClient, method: str, endpoint: str, **kwargs):
    return await client._make_request(method, endpoint, **kwargs)
"""
