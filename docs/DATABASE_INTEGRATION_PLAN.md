# 🗃️ CogniFlow Database Integration Plan

## 📅 Timeline & Phases

### **Phase 2A: Foundation Databases (Week 1-2)**
**Priority: CRITICAL** - Required before any AI features

#### PostgreSQL (Structured Data)
```bash
# Add to docker-compose.yml
postgres:
  image: postgres:15-alpine
  environment:
    POSTGRES_DB: cogniflow
    POSTGRES_USER: cogniflow_user
    POSTGRES_PASSWORD: secure_password
  volumes:
    - postgres_data:/var/lib/postgresql/data
  ports:
    - "5432:5432"
```

#### Required Tables (Week 1)
- `users` - User accounts and profiles
- `courses` - Course metadata
- `lessons` - Lesson content and structure
- `enrollments` - User course enrollments

#### Required Tables (Week 2)
- `user_progress` - Learning progress tracking
- `user_sessions` - Login sessions and activity
- `course_analytics` - Basic course metrics

### **Phase 2B: Analytics Database (Week 3-4)**
**Priority: HIGH** - Required for AI personalization

#### MongoDB (Analytics & Interaction Data)
```bash
# Add to docker-compose.yml
mongodb:
  image: mongo:7
  environment:
    MONGO_INITDB_ROOT_USERNAME: cogniflow
    MONGO_INITDB_ROOT_PASSWORD: secure_password
  volumes:
    - mongodb_data:/data/db
  ports:
    - "27017:27017"
```

#### Collections Needed
- `interaction_logs` - Click tracking, time-on-page
- `learning_sessions` - Study session data
- `quiz_attempts` - Assessment results
- `ai_conversations` - Chat history with AI tutor

### **Phase 2C: Performance Optimization (Week 5-6)**
**Priority: MEDIUM** - Performance and scaling

#### Redis Enhancement
```bash
# Already in docker-compose.yml, enhance usage for:
# - Session caching
# - Course data caching
# - Real-time user status
# - Message queues for AI processing
```

## 🛠️ Implementation Steps

### Step 1: Add Database Services (Day 1)
```yaml
# docker-compose.yml additions
volumes:
  postgres_data:
  mongodb_data:
  redis_data:  # Already exists

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: cogniflow
      POSTGRES_USER: cogniflow_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-secure_password}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    
  mongodb:
    image: mongo:7
    environment:
      MONGO_INITDB_ROOT_USERNAME: cogniflow
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD:-secure_password}
    volumes:
      - mongodb_data:/data/db
    ports:
      - "27017:27017"
```

### Step 2: Update Service Dependencies (Day 1)
```python
# services/users-service/requirements.txt
fastapi
uvicorn[standard]
pydantic
python-multipart
sqlalchemy          # PostgreSQL ORM
psycopg2-binary     # PostgreSQL driver
alembic             # Database migrations
python-jose[cryptography]  # JWT tokens
passlib[bcrypt]     # Password hashing
```

```python
# services/courses-service/requirements.txt
fastapi
uvicorn[standard]
pydantic
python-multipart
sqlalchemy          # PostgreSQL ORM
psycopg2-binary     # PostgreSQL driver
pymongo             # MongoDB driver
```

### Step 3: Database Models (Day 2-3)
```python
# services/users-service/database.py
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://cogniflow_user:secure_password@postgres:5432/cogniflow"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserDB(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    role = Column(String, default="student")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    last_login = Column(DateTime, nullable=True)
```

### Step 4: Migration Scripts (Day 3-4)
```python
# services/users-service/create_tables.py
from database import engine, Base, UserDB
from sqlalchemy.orm import Session

def create_tables():
    Base.metadata.create_all(bind=engine)

def migrate_demo_data():
    # Migrate existing in-memory data to PostgreSQL
    with Session(engine) as session:
        # Insert demo users from current main.py
        pass
```

### Step 5: Update Service Code (Day 4-7)
```python
# services/users-service/main.py (updated)
from database import SessionLocal, UserDB
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users/", response_model=List[User])
async def get_users(db: Session = Depends(get_db)):
    """Retrieve all users from PostgreSQL."""
    users = db.query(UserDB).all()
    return users
```

## 🎯 Integration Checkpoints

### Week 1 Checkpoint
- [ ] PostgreSQL container running
- [ ] Basic tables created
- [ ] Users service connected to PostgreSQL
- [ ] Demo data migrated
- [ ] Authentication endpoints working

### Week 2 Checkpoint
- [ ] Courses service connected to PostgreSQL
- [ ] All CRUD operations working
- [ ] Data persistence verified
- [ ] API endpoints returning correct data

### Week 3 Checkpoint
- [ ] MongoDB container running
- [ ] Analytics collection structure defined
- [ ] Basic interaction logging implemented
- [ ] Redis caching for frequently accessed data

### Week 4 Checkpoint
- [ ] Full database integration complete
- [ ] Performance optimized
- [ ] Ready for AI service integration
- [ ] Data migration tools ready

## 📊 Why This Timeline is Critical

### **Immediate Blockers Without Database:**
1. **No Authentication**: Can't implement secure login/JWT
2. **No Data Persistence**: Service restarts lose all data
3. **No Analytics**: Can't track user behavior for AI features
4. **No Scalability**: In-memory storage doesn't scale

### **AI Features That Need Database (Phase 2B):**
1. **Conversational AI**: Needs chat history and user context
2. **Spaced Repetition**: Requires learning history and scheduling
3. **Personalization**: Needs user behavior and progress data
4. **Adaptive Content**: Requires performance analytics

### **Research Features That Need Database (Phase 3):**
1. **Pilot Study**: Needs comprehensive data collection
2. **Learning Analytics**: Requires detailed interaction logs
3. **A/B Testing**: Needs experimental data tracking

## 🚀 Quick Start Command

Once you're ready to implement:
```bash
# 1. Update docker-compose.yml with database services
# 2. Add database dependencies to requirements.txt
# 3. Run the full stack with databases
docker-compose down
docker-compose up --build

# 4. Create tables and migrate data
docker-compose exec users-service python create_tables.py
docker-compose exec courses-service python create_tables.py
```

## 🎯 Success Metrics

**Database integration is successful when:**
- [ ] All services survive container restarts with data intact
- [ ] User authentication with JWT tokens works
- [ ] Course enrollment persists across sessions
- [ ] Analytics data accumulates over time
- [ ] Performance remains fast with caching
- [ ] Ready to add AI services without data concerns