# CogniFlow Project Structure

This document provides a detailed overview of the CogniFlow project structure and explains the purpose of each component.

```
CogniFlow/
├── README.md                 # Main project documentation
├── LICENSE                   # MIT License
├── .gitignore               # Git ignore patterns
├── docker-compose.yml       # Docker orchestration configuration
├── setup.sh                 # Unix/Linux setup script
├── setup.ps1               # Windows PowerShell setup script
│
├── frontend/                # React TypeScript Frontend
│   ├── public/             # Static assets
│   ├── src/
│   │   ├── App.tsx         # Main application component
│   │   ├── App.css         # Application styles
│   │   ├── index.tsx       # React entry point
│   │   └── ...             # Other React components
│   ├── package.json        # Frontend dependencies
│   ├── tsconfig.json       # TypeScript configuration
│   └── Dockerfile          # Frontend container configuration
│
└── services/                # Microservices directory
    │
    ├── api-gateway/        # API Gateway Service (Node.js)
    │   ├── index.js        # Gateway routing logic
    │   ├── package.json    # Gateway dependencies
    │   └── Dockerfile      # Gateway container configuration
    │
    ├── users-service/      # Users Management Service (Python)
    │   ├── main.py         # FastAPI application
    │   ├── requirements.txt # Python dependencies
    │   └── Dockerfile      # Users service container configuration
    │
    └── courses-service/    # Courses Management Service (Python)
        ├── main.py         # FastAPI application
        ├── requirements.txt # Python dependencies
        └── Dockerfile      # Courses service container configuration
```

## 🔧 Component Details

### Frontend (`/frontend`)
- **Technology**: React 18 + TypeScript
- **Purpose**: User interface for the learning platform
- **Key Features**:
  - Modern, responsive design
  - Real-time data from microservices
  - Dashboard with statistics and course listings
  - User management interface

### API Gateway (`/services/api-gateway`)
- **Technology**: Node.js + Express
- **Purpose**: Single entry point for all client requests
- **Responsibilities**:
  - Request routing to appropriate microservices
  - CORS handling
  - Request/response transformation
  - Future: Authentication, rate limiting

### Users Service (`/services/users-service`)
- **Technology**: Python + FastAPI
- **Purpose**: User management and authentication
- **Features**:
  - User registration and profiles
  - Role-based access (student, instructor, admin)
  - Learning progress tracking
  - User analytics

### Courses Service (`/services/courses-service`)
- **Technology**: Python + FastAPI
- **Purpose**: Course and content management
- **Features**:
  - Course creation and management
  - Lesson organization
  - Enrollment handling
  - Progress tracking
  - Category management

## 🌐 Service Communication

```
Frontend (3000) 
    ↓ HTTP Requests
API Gateway (8000)
    ↓ Proxy Requests
┌─────────────────┐    ┌─────────────────┐
│ Users Service   │    │ Courses Service │
│     (8001)      │    │     (8002)      │
└─────────────────┘    └─────────────────┘
```

## 📊 Data Models

### User Model
```typescript
interface User {
  id: number;
  username: string;
  email: string;
  full_name: string;
  role: 'student' | 'instructor' | 'admin';
  is_active: boolean;
  created_at: string;
}
```

### Course Model
```typescript
interface Course {
  id: number;
  title: string;
  description: string;
  instructor_id: number;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  status: 'draft' | 'published' | 'archived';
  category: string;
  estimated_duration_hours: number;
  enrollment_count: number;
  rating: number;
  tags: string[];
}
```

### Lesson Model
```typescript
interface Lesson {
  id: number;
  title: string;
  type: 'video' | 'text' | 'quiz' | 'interactive' | 'simulation';
  content_url?: string;
  description: string;
  duration_minutes: number;
  order: number;
}
```

## 🔮 Future Expansion Points

### Analytics Service
```
services/analytics-service/
├── main.py              # Learning analytics processing
├── models/              # Data models for analytics
│   ├── engagement.py    # User engagement metrics
│   ├── performance.py   # Learning performance tracking
│   └── behavior.py      # User behavior analysis
└── requirements.txt     # Analytics dependencies
```

### AI Service
```
services/ai-service/
├── main.py              # AI orchestration
├── chat/                # Conversational AI
│   ├── tutor.py         # Virtual tutor implementation
│   └── context.py       # Conversation context management
├── personalization/     # Adaptive learning
│   ├── recommender.py   # Content recommendation
│   └── difficulty.py    # Dynamic difficulty adjustment
└── requirements.txt     # AI dependencies (transformers, openai, etc.)
```

### Notification Service
```
services/notification-service/
├── main.py              # Notification orchestration
├── channels/            # Communication channels
│   ├── email.py         # Email notifications
│   ├── push.py          # Push notifications
│   └── sms.py           # SMS notifications
└── templates/           # Message templates
```

## 🗃️ Database Design (Future)

### PostgreSQL (Structured Data)
- Users table
- Courses table
- Enrollments table
- Lessons table
- Quiz/Assessment tables

### MongoDB (Analytics & Logs)
- User interaction logs
- Learning session data
- Chat conversation history
- Performance metrics

### Redis (Caching)
- Session data
- Frequently accessed course data
- Real-time user status
- Message queues

## 🚀 Deployment Architecture

### Development
- Docker Compose for local development
- Hot reloading for all services
- Shared volumes for code changes

### Production (Future)
```
Load Balancer
    ↓
API Gateway (Multiple instances)
    ↓
Service Mesh (Istio/Envoy)
    ↓
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   Users     │ │   Courses   │ │     AI      │
│  Service    │ │   Service   │ │   Service   │
│ (Replicated)│ │ (Replicated)│ │ (GPU-enabled)│
└─────────────┘ └─────────────┘ └─────────────┘
    ↓               ↓               ↓
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ PostgreSQL  │ │  MongoDB    │ │   Redis     │
│ (Primary/   │ │ (Replica    │ │ (Cluster)   │
│  Replica)   │ │  Set)       │ │             │
└─────────────┘ └─────────────┘ └─────────────┘
```

## 📝 Configuration Management

### Environment Variables
```bash
# API Gateway
NODE_ENV=development
PORT=8000

# Users Service  
DATABASE_URL=postgresql://user:pass@localhost/cogniflow
JWT_SECRET=your-secret-key
REDIS_URL=redis://localhost:6379

# Courses Service
DATABASE_URL=postgresql://user:pass@localhost/cogniflow  
REDIS_URL=redis://localhost:6379

# AI Service (Future)
OPENAI_API_KEY=your-openai-key
HUGGINGFACE_API_KEY=your-hf-key
MODEL_CACHE_DIR=/app/models
```

### Docker Environment Files
```
.env.development
.env.staging
.env.production
```

## 🧪 Testing Structure

```
tests/
├── unit/                # Unit tests for individual components
│   ├── users/           # Users service tests
│   ├── courses/         # Courses service tests
│   └── frontend/        # Frontend component tests
├── integration/         # Service integration tests
│   ├── api/             # API endpoint tests
│   └── database/        # Database integration tests
└── e2e/                 # End-to-end tests
    ├── user-journey/    # Complete user workflows
    └── performance/     # Load and performance tests
```

This structure provides a solid foundation for scaling the CogniFlow platform as it grows from a demo to a full-featured AI-powered learning platform.
