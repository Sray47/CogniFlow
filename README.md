# 🧠 CogniFlow - AI-Powered Learning Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![React](https://img.shields.io/badge/React-18.x-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue.svg)](https://www.typescriptlang.org/)
[![Docker](https://img.shields.io/badge/Docker-Enabled-blue.svg)](https://www.docker.com/)

CogniFlow is a next-generation AI-powered online learning platform designed to revolutionize education through personalized, adaptive, and engaging learning experiences. Built with a modern microservices architecture, it addresses key challenges in online learning such as low engagement, high cognitive load, and one-size-fits-all content delivery.

## 🎯 Project Vision

This comprehensive project aims to move beyond traditional online courses and create a deeply personalized educational experience using:

- **🤖 AI-Powered Personalization**: Adaptive content delivery based on individual learning patterns
- **🎮 Gamification**: Interactive elements to boost engagement and retention
- **📊 Advanced Analytics**: Real-time learning metrics and progress tracking
- **🧘 Cognitive Load Optimization**: UI/UX designed to minimize mental effort
- **💬 Conversational AI**: Virtual tutors for step-by-step guidance
- **🔬 Research-Oriented**: Scientific validation through pilot studies

## 🏗️ Architecture Overview

CogniFlow follows a **microservices architecture** for scalability, maintainability, and independent service development:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │  Users Service  │
│   (React TS)    │◄──►│   (Node.js)     │◄──►│  (FastAPI)      │
│   Port: 3000    │    │   Port: 8000    │    │   Port: 8001    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                  │
                       ┌─────────────────┐    ┌─────────────────┐
                       │ Courses Service │    │     Redis       │
                       │   (FastAPI)     │    │   (Cache)       │
                       │   Port: 8002    │    │   Port: 6379    │
                       └─────────────────┘    └─────────────────┘
                                  │
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Analytics     │    │ Notifications   │
                       │   Service       │    │   Service       │
                       │   Port: 8004    │    │   Port: 8003    │
                       └─────────────────┘    └─────────────────┘
                                  │
                       ┌─────────────────┐    ┌─────────────────┐
                       │   PostgreSQL    │    │   WebSockets    │
                       │   (Database)    │    │ (Real-time)     │
                       │   Port: 5432    │    │                 │
                       └─────────────────┘    └─────────────────┘
```

### 🏢 Service Architecture

| Service | Technology | Port | Purpose |
|---------|------------|------|---------|
| **Frontend** | React 18 + TypeScript | 3000 | Modern, type-safe user interface |
| **API Gateway** | Node.js + Express | 8000 | Request routing and service orchestration |
| **Users Service** | Python + FastAPI | 8001 | User management, authentication, profiles |
| **Courses Service** | Python + FastAPI | 8002 | Course content, lessons, enrollment |
| **Notifications** | Python + FastAPI | 8003 | Real-time notifications, email, push alerts |
| **Analytics** | Python + FastAPI | 8004 | Learning analytics, progress tracking |
| **PostgreSQL** | Database | 5432 | Persistent data storage (production) |
| **Redis** | Cache/Session | 6379 | Fast caching and session management |

### 🔧 Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Frontend** | React 18 + TypeScript | Modern, type-safe user interface |
| **API Gateway** | Node.js + Express | Request routing and service orchestration |
| **Backend Services** | Python + FastAPI | High-performance API services |
| **Caching** | Redis | Fast data caching and session management |
| **Containerization** | Docker + Docker Compose | Consistent development and deployment |
| **Future AI** | Hugging Face, OpenAI API | Conversational AI and personalization |

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (recommended)
- **Node.js 18+** (for local development)
- **Python 3.9+** (for local development)

### 🔄 Two Deployment Modes

CogniFlow supports two deployment modes to fit different development and production needs:

#### Mode 1: No Database Mode (Quick Start) ⚡
Perfect for development, testing, and quick demos. Uses in-memory data structures.

**Windows:**
```powershell
.\start-no-db.ps1
```

**Linux/macOS:**
```bash
docker-compose -f docker-compose.no-db.yml up --build
```

#### Mode 2: Full Database Mode (Production) 🗄️
Uses PostgreSQL and Redis for data persistence and caching.

**Windows:**
```powershell
.\start-with-db.ps1
```

**Linux/macOS:**
```bash
docker-compose up --build
```

### 🌐 Access Points

Once running, access the application at:
- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Users Service**: http://localhost:8001/docs
- **Courses Service**: http://localhost:8002/docs
- **Notifications Service**: http://localhost:8003/docs
- **Analytics Service**: http://localhost:8004/docs
- **Authentication Service**: Auto-routed through gateway
- **PostgreSQL** (database mode only): localhost:5432
- **Redis** (database mode only): localhost:6379

### 🔧 Individual Service Setup

1. **Start the API Gateway**:
   ```bash
   cd services/api-gateway
   npm install
   npm start
   ```

2. **Start the Users Service**:
   ```bash
   cd services/users-service
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8001
   ```

3. **Start the Courses Service**:
   ```bash
   cd services/courses-service
   pip install -r requirements.txt
   uvicorn main:app --reload --port 8002
   ```

4. **Start the Frontend**:
   ```bash
   cd frontend
   npm install
   npm start
   ```

## 📋 Current Features

### ✅ Phase 1: Foundation (Completed)
- **Microservices Architecture**: Independent, scalable services
- **User Management**: Registration, profiles, and role-based access
- **Course Management**: Course creation, lessons, and enrollment
- **Authentication System**: JWT-based secure authentication with refresh tokens
- **Modern UI**: Responsive, beautiful interface with real-time data
- **API Documentation**: Auto-generated FastAPI docs
- **Docker Support**: One-command deployment with no-database dev mode

### ✅ Phase 2: Analytics & Notifications (Completed)
- **Learning Analytics**: Comprehensive tracking of user interactions and progress
- **Real-time Notifications**: WebSocket-based instant notification delivery
- **Email Notifications**: Template-based email system with user preferences
- **Progress Tracking**: Advanced metrics and learning pattern analysis
- **Cross-Service Integration**: Professional service-to-service communication
- **Bulk Operations**: Efficient batch processing for analytics and notifications
- **User Preferences**: Granular control over notification types and delivery

### 🔄 Phase 3: AI Features (Planned)
- **Conversational AI Tutor**: ChatGPT-style learning assistant
- **Spaced Repetition**: AI-optimized learning intervals
- **Personalized Content**: Adaptive difficulty and pacing
- **Achievement System**: Gamification with badges and leaderboards

### 🔮 Phase 4: Advanced Features (Future)
- **Affective Computing**: Emotion-aware tutoring
- **AR/VR Integration**: Immersive learning experiences
- **Peer Learning**: AI-facilitated study groups
- **Research Analytics**: Scientific learning effectiveness studies

## 📊 API Endpoints

### Authentication Service (`/api/auth`)
- `POST /login` - User authentication with JWT tokens
- `POST /refresh` - Refresh access tokens
- `POST /logout` - User logout and token invalidation
- `GET /me` - Get current user information
- `GET /health` - Service health check
- `GET /admin/audit-logs` - Get authentication audit logs (admin only)
- `GET /admin/active-sessions` - Get active user sessions (admin only)

### Users Service (`/api/users`)
- `GET /users/` - List all users
- `GET /users/{id}` - Get user by ID
- `GET /users/{id}/progress` - Get user learning progress
- `POST /users/` - Create new user
- `GET /users/role/{role}` - Get users by role

### Courses Service (`/api/courses`)
- `GET /courses/` - List courses (with filtering)
- `GET /courses/{id}` - Get course details with lessons
- `GET /courses/{id}/lessons` - Get course lessons
- `POST /courses/{id}/enroll/{user_id}` - Enroll user in course
- `GET /users/{id}/enrollments` - Get user enrollments
- `GET /categories/` - Get course categories

### Learning Analytics Service (`/api/analytics`)
- `POST /events` - Track learning events and interactions
- `GET /analytics/user/{user_id}` - Get comprehensive user analytics
- `GET /analytics/course/{course_id}` - Get course performance metrics
- `GET /analytics/platform` - Get platform-wide analytics
- `GET /progress/{user_id}` - Get detailed learning progress
- `POST /batch-events` - Submit multiple events efficiently

### Notifications Service (`/api/notifications`)
- `POST /notifications` - Create single notification
- `POST /notifications/bulk` - Create bulk notifications
- `GET /notifications/user/{user_id}` - Get user notifications
- `PUT /notifications/{id}/read` - Mark notification as read
- `GET /preferences/{user_id}` - Get notification preferences
- `PUT /preferences/{user_id}` - Update notification preferences
- `GET /templates` - Get notification templates
- `GET /analytics/delivery-stats` - Get delivery analytics
- `WS /ws/{user_id}` - Real-time notification WebSocket

## 🧪 Development Guide

### Adding a New Microservice

1. **Create service directory**:
   ```bash
   mkdir services/new-service
   cd services/new-service
   ```

2. **Create FastAPI service**:
   ```python
   # main.py
   from fastapi import FastAPI
   app = FastAPI(title="New Service")
   
   @app.get("/")
   async def root():
       return {"service": "new-service", "status": "running"}
   ```

3. **Add to Docker Compose**:
   ```yaml
   new-service:
     build: ./services/new-service
     volumes:
       - ./services/new-service:/code
   ```

4. **Update API Gateway**:
   ```javascript
   app.use('/api/new', createProxyMiddleware({ 
     target: 'http://new-service:8003', 
     changeOrigin: true 
   }));
   ```

### Database Integration

For production, replace in-memory data with real databases:

- **PostgreSQL**: For structured data (users, courses)
- **MongoDB**: For analytics and logs
- **Redis**: For caching and sessions

### AI Service Integration

Future AI features will be added as dedicated services:

```python
# services/ai-service/main.py
from fastapi import FastAPI
import openai

app = FastAPI(title="CogniFlow AI Service")

@app.post("/ai/chat")
async def chat_with_tutor(message: str):
    # Integration with OpenAI/Hugging Face
    response = openai.ChatCompletion.create(...)
    return {"response": response}
```

## 📈 Monitoring & Analytics

The platform is designed with analytics-first approach:

- **User Interaction Tracking**: Clicks, time-on-page, scroll patterns
- **Learning Metrics**: Completion rates, accuracy, retention
- **Performance Monitoring**: API response times, error rates
- **A/B Testing**: Feature effectiveness comparison

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Standards

- **Code Quality**: Use TypeScript for frontend, type hints for Python
- **Testing**: Write unit tests for all services
- **Documentation**: Update API docs and README for new features
- **Docker**: Ensure all services work in containers

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## � Security Notice

⚠️ **Important**: This is a **demonstration/educational project**. Before deploying to production:

1. **Review [SECURITY.md](SECURITY.md)** for comprehensive security guidelines
2. **Never commit `.env` files** - use `.env.example` as a template
3. **Generate strong secrets** for JWT tokens and database passwords
4. **Enable HTTPS/TLS** for all communications in production
5. **Implement proper authentication** and input validation

For production deployment, conduct a thorough security review and implement additional security measures.

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the security guidelines in [SECURITY.md](SECURITY.md)
4. Test your changes thoroughly
5. Submit a pull request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## �🙏 Acknowledgments

- **FastAPI**: For the amazing Python web framework
- **React**: For the powerful frontend library
- **Docker**: For containerization simplicity
- **OpenAI**: For future AI integration possibilities

## 🔮 Roadmap

### Short Term (Next 2-4 weeks)
- [ ] Add real database integration (PostgreSQL + MongoDB)
- [ ] Implement user authentication and JWT tokens
- [ ] Create quiz and assessment system
- [ ] Add basic analytics dashboard

### Medium Term (1-3 months)
- [ ] Integrate OpenAI API for conversational tutor
- [ ] Implement spaced repetition algorithm
- [ ] Add gamification features (points, badges, leaderboards)
- [ ] Create instructor dashboard for content creation

### Long Term (3-6 months)
- [ ] Develop mobile app companion
- [ ] Implement affective computing features
- [ ] Add AR/VR learning modules
- [ ] Conduct user research and pilot studies

---

**Built with ❤️ for the future of education**

For questions, issues, or contributions, please visit our [GitHub Issues](https://github.com/your-repo/issues) page.