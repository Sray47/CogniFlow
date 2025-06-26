"""
CogniFlow Users Service - Refactored with Store Abstraction

This service manages user profiles, learning progress, and user-related analytics.
Uses abstracted storage layers that can be swapped between in-memory and database implementations.

Key Features:
- User profile management and preferences
- Learning progress tracking and analytics  
- Achievement system and gamification
- User statistics and leaderboards
- Social features and connections

Author: CogniFlow Development Team
Version: 3.0.0
"""

import os
import datetime
import httpx
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

# Import our store abstraction
from store import InMemoryUserStore, UserRole, UserStatus, LearningStyle

app = FastAPI(
    title="CogniFlow Users Service",
    description="Comprehensive user management with progress tracking and gamification",
    version="3.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize store (can be swapped with database implementation)
store = InMemoryUserStore()

# Analytics service URL for event firing
ANALYTICS_SERVICE_URL = os.getenv("ANALYTICS_SERVICE_URL", "http://learning-analytics:8000")

# Pydantic models for request/response validation
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    role: Optional[UserRole] = UserRole.STUDENT

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    timezone: Optional[str] = None

class UserResponse(BaseModel):
    user_id: str
    email: str
    username: str
    full_name: str
    role: UserRole
    status: UserStatus
    created_at: datetime.datetime
    last_login: Optional[datetime.datetime]
    profile_picture: Optional[str]
    bio: Optional[str]
    location: Optional[str]

class UserPreferences(BaseModel):
    learning_style: Optional[LearningStyle] = None
    difficulty_preference: Optional[str] = None
    notification_settings: Optional[Dict[str, Any]] = None
    privacy_settings: Optional[Dict[str, Any]] = None
    study_preferences: Optional[Dict[str, Any]] = None
    ui_preferences: Optional[Dict[str, Any]] = None

class ProgressUpdate(BaseModel):
    lesson_completed: Optional[bool] = False
    course_completed: Optional[bool] = False
    study_time_minutes: Optional[int] = 0
    points_earned: Optional[int] = 0
    experience_points: Optional[int] = 0

class Achievement(BaseModel):
    id: str
    name: str
    description: str
    icon: str
    category: str
    points: int
    earned_at: Optional[datetime.datetime] = None
    progress: Optional[int] = None

class UserStats(BaseModel):
    total_courses_enrolled: int
    courses_completed: int
    lessons_completed: int
    total_study_time_minutes: int
    current_streak_days: int
    total_points: int
    current_level: int
    achievements_count: int

class AnalyticsEvent(BaseModel):
    user_id: str
    event_type: str
    event_data: Dict[str, Any]
    timestamp: str = datetime.datetime.now().isoformat()


async def fire_analytics_event(event: AnalyticsEvent):
    """Fire analytics event to learning analytics service"""
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{ANALYTICS_SERVICE_URL}/events",
                json=event.dict(),
                timeout=5.0
            )
    except Exception as e:
        print(f"Failed to fire analytics event: {e}")


# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Users Service",
        "status": "healthy",
        "version": "3.0.0",
        "capabilities": [
            "user_management",
            "progress_tracking",
            "achievement_system",
            "preferences_management",
            "analytics_integration",
            "social_features"
        ]
    }

@app.post("/users", response_model=UserResponse, status_code=201)
async def create_user(user_data: UserCreate, background_tasks: BackgroundTasks):
    """Create a new user account"""
    try:
        # Check if username or email already exists
        existing_users = [user for user in store.users.values() 
                         if user.get("email") == user_data.email or user.get("username") == user_data.username]
        
        if existing_users:
            raise HTTPException(status_code=400, detail="Username or email already exists")
        
        new_user = store.create_user(user_data.dict())
        
        # Fire analytics event
        event = AnalyticsEvent(
            user_id=new_user["user_id"],
            event_type="user_created",
            event_data={
                "role": new_user["role"],
                "registration_method": "direct"
            }
        )
        background_tasks.add_task(fire_analytics_event, event)
        
        return UserResponse(**new_user)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user profile by ID"""
    user = store.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(**user)

@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, update_data: UserUpdate, background_tasks: BackgroundTasks):
    """Update user profile"""
    try:
        updated_user = store.update_user(user_id, update_data.dict(exclude_unset=True))
        
        # Fire analytics event
        event = AnalyticsEvent(
            user_id=user_id,
            event_type="profile_updated",
            event_data=update_data.dict(exclude_unset=True)
        )
        background_tasks.add_task(fire_analytics_event, event)
        
        return UserResponse(**updated_user)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")

@app.delete("/users/{user_id}")
async def delete_user(user_id: str, background_tasks: BackgroundTasks):
    """Deactivate user account (soft delete)"""
    success = store.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Fire analytics event
    event = AnalyticsEvent(
        user_id=user_id,
        event_type="user_deactivated",
        event_data={"deactivation_method": "admin"}
    )
    background_tasks.add_task(fire_analytics_event, event)
    
    return {"message": "User deactivated successfully"}

@app.get("/users", response_model=List[UserResponse])
async def list_users(
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    role: Optional[UserRole] = None,
    status: Optional[UserStatus] = None
):
    """List users with optional filtering"""
    all_users = list(store.users.values())
    
    # Apply filters
    if role:
        all_users = [user for user in all_users if user.get("role") == role]
    if status:
        all_users = [user for user in all_users if user.get("status") == status]
    
    # Apply pagination
    paginated_users = all_users[offset:offset + limit]
    
    return [UserResponse(**user) for user in paginated_users]

@app.get("/users/{user_id}/progress")
async def get_user_progress(user_id: str):
    """Get user's learning progress"""
    if user_id not in store.users:
        raise HTTPException(status_code=404, detail="User not found")
    
    progress = store.get_user_progress(user_id)
    return progress

@app.post("/users/{user_id}/progress")
async def update_user_progress(user_id: str, progress_update: ProgressUpdate, background_tasks: BackgroundTasks):
    """Update user's learning progress"""
    if user_id not in store.users:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Convert progress update to dict and filter out None values
    update_data = {}
    
    if progress_update.lesson_completed:
        update_data["lessons_completed"] = 1
    if progress_update.course_completed:
        update_data["courses_completed"] = 1
    if progress_update.study_time_minutes:
        update_data["total_study_time_minutes"] = progress_update.study_time_minutes
    if progress_update.points_earned:
        update_data["total_points"] = progress_update.points_earned
    if progress_update.experience_points:
        update_data["experience_points"] = progress_update.experience_points
    
    store.update_user_progress(user_id, update_data)
    
    # Fire analytics event
    event = AnalyticsEvent(
        user_id=user_id,
        event_type="progress_updated",
        event_data=update_data
    )
    background_tasks.add_task(fire_analytics_event, event)
    
    return {"message": "Progress updated successfully", "progress": store.get_user_progress(user_id)}

@app.get("/users/{user_id}/achievements", response_model=List[Achievement])
async def get_user_achievements(user_id: str):
    """Get user's achievements"""
    if user_id not in store.users:
        raise HTTPException(status_code=404, detail="User not found")
    
    achievements = store.get_user_achievements(user_id)
    return [Achievement(**achievement) for achievement in achievements]

@app.post("/users/{user_id}/achievements")
async def award_achievement(user_id: str, achievement: Achievement, background_tasks: BackgroundTasks):
    """Award an achievement to user"""
    if user_id not in store.users:
        raise HTTPException(status_code=404, detail="User not found")
    
    store.add_achievement(user_id, achievement.dict())
    
    # Fire analytics event
    event = AnalyticsEvent(
        user_id=user_id,
        event_type="achievement_earned",
        event_data={
            "achievement_id": achievement.id,
            "achievement_name": achievement.name,
            "points": achievement.points
        }
    )
    background_tasks.add_task(fire_analytics_event, event)
    
    return {"message": "Achievement awarded successfully"}

@app.get("/users/{user_id}/preferences", response_model=UserPreferences)
async def get_user_preferences(user_id: str):
    """Get user preferences"""
    if user_id not in store.users:
        raise HTTPException(status_code=404, detail="User not found")
    
    preferences = store.get_user_preferences(user_id)
    return UserPreferences(**preferences)

@app.put("/users/{user_id}/preferences", response_model=UserPreferences)
async def update_user_preferences(user_id: str, preferences: UserPreferences, background_tasks: BackgroundTasks):
    """Update user preferences"""
    if user_id not in store.users:
        raise HTTPException(status_code=404, detail="User not found")
    
    store.update_user_preferences(user_id, preferences.dict(exclude_unset=True))
    
    # Fire analytics event
    event = AnalyticsEvent(
        user_id=user_id,
        event_type="preferences_updated",
        event_data=preferences.dict(exclude_unset=True)
    )
    background_tasks.add_task(fire_analytics_event, event)
    
    return UserPreferences(**store.get_user_preferences(user_id))

@app.get("/users/{user_id}/stats", response_model=UserStats)
async def get_user_stats(user_id: str):
    """Get user statistics"""
    if user_id not in store.users:
        raise HTTPException(status_code=404, detail="User not found")
    
    progress = store.get_user_progress(user_id)
    achievements = store.get_user_achievements(user_id)
    
    stats = UserStats(
        total_courses_enrolled=progress.get("total_courses_enrolled", 0),
        courses_completed=progress.get("courses_completed", 0),
        lessons_completed=progress.get("lessons_completed", 0),
        total_study_time_minutes=progress.get("total_study_time_minutes", 0),
        current_streak_days=progress.get("current_streak_days", 0),
        total_points=progress.get("total_points", 0),
        current_level=progress.get("current_level", 1),
        achievements_count=len(achievements)
    )
    
    return stats

@app.get("/users/{user_id}/analytics")
async def get_user_analytics(user_id: str):
    """Get comprehensive user analytics"""
    if user_id not in store.users:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = store.get_user(user_id)
    progress = store.get_user_progress(user_id)
    statistics = store.get_user_statistics(user_id)
    social = store.get_user_social(user_id)
    
    return {
        "user_profile": {
            "user_id": user_id,
            "username": user.get("username"),
            "created_at": user.get("created_at"),
            "last_login": user.get("last_login")
        },
        "progress_summary": progress,
        "detailed_statistics": statistics,
        "social_activity": social,
        "generated_at": datetime.datetime.now().isoformat()
    }

@app.get("/leaderboard")
async def get_leaderboard(
    metric: str = Query(default="total_points", description="Metric to rank by"),
    limit: int = Query(default=20, le=100)
):
    """Get user leaderboard"""
    leaderboard = store.get_leaderboard(metric, limit)
    return {
        "leaderboard": leaderboard,
        "metric": metric,
        "total_users": len(leaderboard),
        "generated_at": datetime.datetime.now().isoformat()
    }

@app.get("/users/{user_id}/social")
async def get_user_social(user_id: str):
    """Get user's social connections and activity"""
    if user_id not in store.users:
        raise HTTPException(status_code=404, detail="User not found")
    
    social_data = store.get_user_social(user_id)
    return social_data

@app.post("/users/{user_id}/login")
async def record_user_login(user_id: str, background_tasks: BackgroundTasks):
    """Record user login for analytics and streak tracking"""
    if user_id not in store.users:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update last login
    store.users[user_id]["last_login"] = datetime.datetime.now()
    
    # Update streak logic could be more sophisticated
    progress = store.get_user_progress(user_id)
    last_activity = progress.get("last_activity")
    
    if last_activity:
        last_activity_date = datetime.datetime.fromisoformat(last_activity) if isinstance(last_activity, str) else last_activity
        days_since_last = (datetime.datetime.now() - last_activity_date).days
        
        if days_since_last == 1:
            # Continue streak
            store.update_user_progress(user_id, {"current_streak_days": 1})
        elif days_since_last > 1:
            # Reset streak
            progress["current_streak_days"] = 1
    else:
        # First activity
        progress["current_streak_days"] = 1
    
    # Fire analytics event
    event = AnalyticsEvent(
        user_id=user_id,
        event_type="user_login",
        event_data={
            "login_time": datetime.datetime.now().isoformat(),
            "current_streak": progress.get("current_streak_days", 1)
        }
    )
    background_tasks.add_task(fire_analytics_event, event)
    
    return {"message": "Login recorded successfully", "current_streak": progress.get("current_streak_days", 1)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
