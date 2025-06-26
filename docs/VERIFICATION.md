# CogniFlow System Verification

This document provides instructions for verifying that the CogniFlow system is working correctly.

## 🐳 Docker Method (Recommended)

### Prerequisites
1. **Install Docker Desktop**: Download from [docker.com](https://www.docker.com/products/docker-desktop)
2. **Start Docker Desktop**: Make sure Docker is running
3. **Verify Installation**: Run `docker --version` and `docker-compose --version`

### Quick Start
```bash
# Clone and navigate to project
cd CogniFlow

# Build and start all services
docker-compose up --build

# Wait for all services to start (about 2-3 minutes)
# You should see logs from all services
```

### Service URLs
Once running, access these URLs:
- **Frontend**: http://localhost:3000 - Main application interface
- **API Gateway**: http://localhost:8000 - API endpoint status
- **API Documentation**: http://localhost:8000/docs - Interactive API docs
- **Users API**: http://localhost:8000/api/users/users/ - Users data
- **Courses API**: http://localhost:8000/api/courses/courses/ - Courses data

### Verification Checklist
- [ ] Frontend loads at http://localhost:3000
- [ ] Dashboard shows user and course statistics
- [ ] API Gateway responds at http://localhost:8000
- [ ] Users service returns data
- [ ] Courses service returns data
- [ ] No error messages in browser console

## 🔧 Manual Method (For Development)

If Docker isn't available, you can run services manually:

### 1. Start API Gateway
```bash
cd services/api-gateway
npm install
npm start
# Should start on port 8000
```

### 2. Start Users Service
```bash
cd services/users-service
pip install -r requirements.txt
uvicorn main:app --reload --port 8001
# Should start on port 8001
```

### 3. Start Courses Service
```bash
cd services/courses-service
pip install -r requirements.txt
uvicorn main:app --reload --port 8002
# Should start on port 8002
```

### 4. Start Frontend
```bash
cd frontend
npm install
npm start
# Should start on port 3000
```

## 🧪 Testing the APIs

### Test Users Service
```bash
# Get all users
curl http://localhost:8000/api/users/users/

# Get specific user
curl http://localhost:8000/api/users/users/1

# Get user progress
curl http://localhost:8000/api/users/users/1/progress
```

### Test Courses Service
```bash
# Get all courses
curl http://localhost:8000/api/courses/courses/

# Get specific course
curl http://localhost:8000/api/courses/courses/1

# Get course lessons
curl http://localhost:8000/api/courses/courses/1/lessons
```

## 🐛 Troubleshooting

### Common Issues

**Port Already in Use**
```bash
# Find and kill process using port 3000
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Or use different ports
PORT=3001 npm start  # For React
uvicorn main:app --port 8003  # For Python services
```

**Docker Issues**
```bash
# Clean up Docker
docker-compose down
docker system prune -f

# Rebuild from scratch
docker-compose up --build --force-recreate
```

**CORS Errors**
- Make sure API Gateway is running on port 8000
- Check that frontend is configured to use correct API URL
- Verify all services are accessible from the gateway

**Import Errors (Python)**
```bash
# Make sure you're in the right directory
cd services/users-service  # or courses-service
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Node.js Errors**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Service Health Checks

**API Gateway Health**
```bash
curl http://localhost:8000/health
# Expected: {"status": "API Gateway is running", "timestamp": "..."}
```

**Users Service Health**
```bash
curl http://localhost:8001/
# Expected: {"service": "CogniFlow Users Service", "status": "running", ...}
```

**Courses Service Health**
```bash
curl http://localhost:8002/
# Expected: {"service": "CogniFlow Courses Service", "status": "running", ...}
```

## 📊 Expected Data

### Sample Users
- Alice Johnson (Student) - alice@example.com
- Bob Smith (Instructor) - bob@example.com  
- System Administrator (Admin) - admin@cogniflow.com

### Sample Courses
- Introduction to Artificial Intelligence (Beginner)
- Advanced Python Programming (Advanced)
- Data Science Fundamentals (Intermediate)
- Introduction to Web Development (Draft)

### Sample Lessons
- What is Artificial Intelligence? (Video)
- Types of Machine Learning (Text)
- AI Knowledge Check (Quiz)
- Advanced Python Decorators (Video)
- Context Managers and With Statement (Interactive)

## 🎯 Success Criteria

The system is working correctly if:

1. **Frontend Dashboard**: Shows statistics (3 users, 4 courses, etc.)
2. **Course Display**: Lists published courses with ratings and metadata
3. **User Display**: Shows community members with roles and status
4. **API Connectivity**: All API calls return valid JSON data
5. **Responsive Design**: Interface works on different screen sizes
6. **Real-time Data**: Frontend shows actual data from backend services

## 🔮 Next Steps

Once the basic system is verified:

1. **Add Authentication**: JWT tokens and protected routes
2. **Database Integration**: Replace in-memory data with PostgreSQL
3. **AI Integration**: Add OpenAI API for conversational features
4. **Advanced UI**: More interactive components and better UX
5. **Testing**: Unit, integration, and E2E tests
6. **Analytics**: User behavior tracking and learning metrics

## 📞 Getting Help

If you encounter issues:

1. Check this troubleshooting guide first
2. Review service logs for error messages
3. Verify all prerequisites are installed
4. Test individual services before running together
5. Open an issue on GitHub with detailed error messages

The system is designed to be robust and self-documenting through the API docs at http://localhost:8000/docs when running.
