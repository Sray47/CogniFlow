# CogniFlow Refactored Prototype Guide

## Overview

This document describes the refactored CogniFlow prototype that implements a feature-rich, impressive learning platform while maintaining clean architecture patterns that prepare it for future database and AI integration.

## Key Architectural Improvements

### 1. Store Abstraction Pattern

Every service now implements a **Store Abstraction Layer** that separates data access from business logic:

```
Service Architecture:
├── main.py (API endpoints)
├── store.py (Data abstraction)
│   ├── Abstract Interface
│   ├── InMemoryStore (Development)
│   └── PostgreSQLStore (Future Production)
└── models.py (Data models)
```

**Benefits:**
- Easy to swap storage implementations
- Clean separation of concerns
- Testable business logic
- Production-ready architecture

### 2. Centralized Analytics Event Bus

All services fire events to the **Learning Analytics Service**, creating a centralized event bus for:
- User behavior tracking
- Learning progress analytics
- Real-time insights
- Cross-service data correlation

## Service Architecture

### 🔐 Authentication Service (`services/authentication/`)
**Store:** `InMemoryAuthStore`
**Features:**
- JWT-based authentication
- Active session management
- Role-based access control
- Admin session monitoring

**Key Endpoints:**
- `POST /auth/login` - User authentication
- `GET /admin/sessions` - View active sessions (Admin only)
- `POST /auth/logout` - Session termination

### 👤 Users Service (`services/users-service/`)
**Store:** `InMemoryUserStore`
**Features:**
- User profile management
- Learning preferences tracking
- Achievement system
- Progress analytics

**Key Endpoints:**
- `GET /users/{user_id}` - Get user profile
- `POST /users/{user_id}/progress/{course_id}` - Update learning progress
- `GET /users/{user_id}/achievements` - Get user achievements

### 📚 Courses Service (`services/courses-service/`)
**Store:** `InMemoryCourseStore`
**Features:**
- Course catalog management
- User enrollment system
- Lesson progress tracking
- Course analytics

**Key Endpoints:**
- `GET /courses/` - List all courses
- `POST /courses/{course_id}/enroll` - Enroll in course
- `POST /users/{user_id}/progress/{course_id}/lessons/{lesson_id}` - Complete lesson
- `GET /users/{user_id}/progress/{course_id}` - Get course progress

### 🤖 AI Tutor Service (`services/ai-tutor-service/`)
**Store:** `InMemoryAITutorStore`
**Features:**
- Intelligent chat conversations
- Spaced repetition engine (SM-2 algorithm)
- Gamification with points and badges
- Adaptive content suggestions
- Quiz generation and grading

**Key Endpoints:**
- `POST /chat` - Chat with AI tutor
- `GET /spaced-repetition/{user_id}` - Get study schedule
- `POST /spaced-repetition/update` - Update learning progress
- `GET /gamification/{user_id}` - Get points and badges
- `POST /quiz/generate` - Generate practice quiz

### 📈 Learning Analytics Service (`services/learning-analytics/`)
**Store:** `InMemoryAnalyticsStore`
**Features:**
- Centralized event bus
- Real-time analytics processing
- User behavior analysis
- Platform-wide insights
- Predictive analytics

**Key Endpoints:**
- `POST /events` - Record learning events
- `GET /analytics/user/{user_id}` - Get user analytics
- `GET /analytics/system` - Get platform analytics
- `GET /events/user/{user_id}` - Get user activity history

## Core Features Implemented

### 🎯 Spaced Repetition Engine
- **Algorithm:** SM-2 (SuperMemo 2)
- **Features:** Adaptive scheduling, performance tracking, retention optimization
- **Integration:** Available through AI Tutor Service
- **Data:** Tracks ease factor, repetition intervals, due dates

### 🏆 Gamification System
- **Points:** Awarded for completing lessons, quizzes, and achievements
- **Badges:** Unlocked based on learning milestones
- **Streaks:** Daily learning consistency tracking
- **Leaderboards:** User ranking and social features

### 📊 Progress Tracking
- **Course Progress:** Percentage completion, lessons completed
- **Learning Analytics:** Time spent, difficulty preferences, learning patterns
- **Adaptive Content:** Personalized recommendations based on performance

### 🎓 Enrollment System
- **Course Enrollment:** One-click enrollment with progress initialization
- **Progress Updates:** Real-time lesson completion tracking
- **Analytics Integration:** All progress events fire to analytics service

## Data Flow Architecture

```
Frontend → API Gateway → Services → Store Layer → Analytics Events
                                      ↓
                              Learning Analytics Service
                                      ↓
                              Real-time Insights Dashboard
```

**Event Flow Example:**
1. User completes lesson in Courses Service
2. Courses Service updates progress in CourseStore
3. Courses Service fires "LESSON_COMPLETED" event to Analytics Service
4. Analytics Service processes event for real-time insights
5. AI Tutor Service uses analytics for adaptive recommendations

## Sample Data Structure

### User Profile
```json
{
  "user_id": "user1",
  "profile": {
    "name": "John Doe",
    "learning_style": "visual",
    "difficulty_preference": "intermediate"
  },
  "progress": {
    "courses_enrolled": 3,
    "lessons_completed": 15,
    "total_study_time_minutes": 450
  },
  "gamification": {
    "total_points": 850,
    "badges": ["first_lesson", "quiz_master"],
    "current_streak": 7
  }
}
```

### Spaced Repetition Item
```json
{
  "item_id": "python_basics",
  "topic": "Python Variables and Data Types",
  "next_review": "2025-06-27T10:00:00",
  "interval": 3,
  "ease_factor": 2.5,
  "repetitions": 2,
  "due": true
}
```

### Learning Event
```json
{
  "event_id": "evt_12345",
  "user_id": "user1",
  "event_type": "lesson_completed",
  "event_data": {
    "course_id": 1,
    "lesson_id": 3,
    "duration_minutes": 25,
    "completion_rate": 0.95
  },
  "timestamp": "2025-06-26T14:30:00Z"
}
```

## Running the Prototype

### Development Mode (No Database)

1. **Set Environment Variable:**
   ```bash
   export NO_DATABASE_MODE=true
   ```

2. **Start Individual Services:**
   ```bash
   # Authentication Service
   cd services/authentication && python main.py

   # Users Service
   cd services/users-service && python main.py

   # Courses Service
   cd services/courses-service && python main.py

   # AI Tutor Service
   cd services/ai-tutor-service && python main.py

   # Learning Analytics Service
   cd services/learning-analytics && python main.py
   ```

3. **Start with Docker Compose:**
   ```bash
   docker-compose -f docker-compose.no-db.yml up
   ```

### Testing the Features

#### 1. Test Course Enrollment
```bash
curl -X POST "http://localhost:8003/courses/1/enroll" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user1", "course_id": 1}'
```

#### 2. Complete a Lesson
```bash
curl -X POST "http://localhost:8003/users/user1/progress/1/lessons/1"
```

#### 3. Get Spaced Repetition Schedule
```bash
curl "http://localhost:8000/spaced-repetition/user1"
```

#### 4. Update Spaced Repetition
```bash
curl -X POST "http://localhost:8000/spaced-repetition/update" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user1", "item_id": "python_basics", "performance": "good"}'
```

#### 5. Get Gamification Stats
```bash
curl "http://localhost:8000/gamification/user1"
```

#### 6. View Analytics
```bash
curl "http://localhost:8001/analytics/user/user1"
```

## Frontend Integration Points

The refactored services expose clean APIs that can be easily integrated with the React frontend:

### Dashboard Features
- **My Progress:** Call `/users/{user_id}/enrollments` to show course progress
- **Study Schedule:** Call `/spaced-repetition/{user_id}` for items due today
- **Points & Badges:** Call `/gamification/{user_id}` for gamification stats

### Course Features
- **Course Catalog:** Call `/courses/` with filtering options
- **Enroll Button:** Call `POST /courses/{id}/enroll`
- **Lesson Completion:** Call `POST /users/{user_id}/progress/{course_id}/lessons/{lesson_id}`

### AI Tutor Features
- **Chat Interface:** Call `POST /chat` for AI conversations
- **Quiz Generation:** Call `POST /quiz/generate` for practice tests
- **Adaptive Suggestions:** Call `/adaptive-content/{user_id}` for recommendations

## Production Migration Path

When ready to move to production with real databases:

1. **Implement PostgreSQL Stores:**
   ```python
   # Example: services/users-service/store.py
   class PostgreSQLUserStore(UserStoreInterface):
       def __init__(self, db_session):
           self.db = db_session
       
       def get_user(self, user_id: str):
           return self.db.query(User).filter(User.id == user_id).first()
   ```

2. **Update Service Initialization:**
   ```python
   # In main.py
   if NO_DATABASE_MODE:
       store = InMemoryUserStore()
   else:
       store = PostgreSQLUserStore(db_session)
   ```

3. **Add Real AI Integration:**
   ```python
   # Replace mock responses with real LLM calls
   async def generate_ai_response(message: str) -> str:
       # Integration with OpenAI, Anthropic, etc.
       pass
   ```

## Architecture Benefits

1. **Scalability:** Each service is independent and can be scaled separately
2. **Maintainability:** Clean separation between data access and business logic  
3. **Testability:** Store interfaces can be easily mocked for testing
4. **Flexibility:** Easy to swap storage implementations or add new features
5. **Production Ready:** Architecture patterns follow industry best practices

## Demo Scenarios

### Scenario 1: New User Learning Flow
1. User creates account (Authentication Service)
2. User browses courses (Courses Service)
3. User enrolls in "Python Basics" (Courses Service)
4. User completes first lesson (Progress tracked, Analytics fired)
5. User chats with AI tutor about questions (AI Tutor Service)
6. System schedules content for spaced repetition (AI Tutor Service)
7. User earns points and first badge (Gamification)

### Scenario 2: Returning User Experience
1. User logs in (Authentication Service)
2. Dashboard shows due spaced repetition items (AI Tutor Service)
3. User reviews scheduled content (Performance tracked)
4. User continues course progress (Courses Service)
5. System adapts content difficulty (AI Tutor Service)
6. User views progress analytics (Learning Analytics Service)

This refactored prototype demonstrates a production-ready architecture while providing an impressive, feature-rich learning experience that feels dynamic and intelligent!
