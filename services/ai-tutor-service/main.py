"""
AI Tutor Service - Main Application
===================================

This service provides intelligent tutoring capabilities including:
- Chat-based learning conversations
- Spaced repetition scheduling
- Adaptive content recommendations  
- Gamification with points and badges
- Quiz generation and assessment
- Learning analytics integration

The service uses abstracted storage layers that can be swapped between
in-memory (development) and database (production) implementations.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import datetime
import random
import httpx
import os
from store import InMemoryAITutorStore

# Initialize FastAPI app
app = FastAPI(
    title="CogniFlow AI Tutor Service", 
    description="Intelligent tutoring with spaced repetition and gamification",
    version="1.0.0"
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
store = InMemoryAITutorStore()

# Analytics service URL for event firing
ANALYTICS_SERVICE_URL = os.getenv("ANALYTICS_SERVICE_URL", "http://learning-analytics:8000")

# Pydantic models for request/response validation
class ChatRequest(BaseModel):
    user_id: str
    message: str
    context: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    suggestions: List[str]
    session_id: str
    timestamp: str

class SpacedRepetitionUpdate(BaseModel):
    user_id: str
    item_id: str
    performance: str  # 'easy', 'good', 'hard', 'forgot'

class QuizRequest(BaseModel):
    user_id: str
    topic: str
    difficulty: Optional[str] = "intermediate"
    num_questions: Optional[int] = 5

class QuizResponse(BaseModel):
    quiz_id: str
    questions: List[Dict[str, Any]]
    time_limit_minutes: int

class QuizSubmission(BaseModel):
    user_id: str
    quiz_id: str
    answers: Dict[str, str]

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
        # In production, we might want to queue this for retry


def generate_mock_ai_response(message: str, user_context: Dict = None) -> str:
    """
    Generate a mock AI tutor response.
    In production, this would integrate with an actual LLM.
    """
    message_lower = message.lower()
    
    # Greeting responses
    if any(greeting in message_lower for greeting in ["hello", "hi", "hey", "good morning", "good afternoon"]):
        responses = [
            "Hello! I'm excited to help you learn today. What topic would you like to explore?",
            "Hi there! Ready for an amazing learning session? What can I help you understand better?",
            "Hey! Great to see you back. What would you like to work on today?",
            "Good to see you! I'm here to make learning fun and effective. What's on your mind?"
        ]
        return random.choice(responses)
    
    # Python-related questions
    if "python" in message_lower:
        responses = [
            "Python is fantastic! It's known for its clean syntax and versatility. Would you like to start with basic concepts like variables and data types, or explore something more specific?",
            "Great choice! Python is perfect for beginners and powerful for experts. What aspect interests you most - syntax, data structures, web development, or data science?",
            "Python is one of my favorite languages to teach! Let's break it down step by step. Are you completely new to programming, or do you have some experience?"
        ]
        return random.choice(responses)
    
    # Mathematics questions
    if any(math_term in message_lower for math_term in ["math", "mathematics", "algebra", "calculus", "geometry"]):
        responses = [
            "Mathematics is the language of the universe! What specific area would you like to explore? I can help with algebra, geometry, calculus, statistics, and more.",
            "Math can be really rewarding once you understand the patterns. What's your current level, and what specific concept are you working on?",
            "I love helping with math! The key is breaking complex problems into smaller, manageable steps. What topic should we tackle?"
        ]
        return random.choice(responses)
    
    # Learning and study questions
    if any(term in message_lower for term in ["learn", "study", "understand", "help", "explain"]):
        responses = [
            "I'm here to help you master any topic! The best learning happens when we combine theory with practice. What subject interests you most?",
            "Learning is a journey, and I'm excited to be your guide! What would you like to focus on today? I can adapt to your learning style.",
            "Great attitude! Active learning is the key to retention. What topic would you like to dive into? I can provide explanations, examples, and practice problems."
        ]
        return random.choice(responses)
    
    # Question-asking behavior
    if "?" in message:
        responses = [
            "That's a great question! Let me think about the best way to explain this clearly. Here's how I'd break it down...",
            "Excellent question! I can see you're thinking deeply about this. Let me provide a comprehensive answer...",
            "I'm glad you asked! This is actually a common question that many learners have. Here's what you need to know..."
        ]
        return random.choice(responses)
    
    # Default responses for general conversation
    default_responses = [
        "That's interesting! Tell me more about what you'd like to learn or understand better.",
        "I'm here to help you learn effectively. What specific topic or concept would you like to explore?",
        "Great! I can help you with a wide range of subjects. What would you like to focus on in our session today?",
        "I'm designed to make learning engaging and personalized. What subject or skill would you like to work on?",
        "Learning is most effective when it's interactive. What topic interests you, and how can I help you master it?"
    ]
    
    return random.choice(default_responses)


def generate_mock_quiz(topic: str, difficulty: str = "intermediate", num_questions: int = 5) -> List[Dict[str, Any]]:
    """
    Generate a mock quiz for the given topic.
    In production, this would use AI to generate contextual questions.
    """
    quiz_templates = {
        "python": {
            "beginner": [
                {
                    "question": "What is the correct way to create a variable in Python?",
                    "options": ["var x = 5", "x = 5", "int x = 5", "create x = 5"],
                    "correct": "x = 5",
                    "explanation": "Python uses simple assignment with the = operator."
                },
                {
                    "question": "Which of these is a valid Python data type?",
                    "options": ["string", "int", "list", "all of the above"],
                    "correct": "all of the above",
                    "explanation": "Python supports many built-in data types including strings, integers, and lists."
                },
                {
                    "question": "How do you print 'Hello World' in Python?",
                    "options": ["echo 'Hello World'", "print('Hello World')", "console.log('Hello World')", "printf('Hello World')"],
                    "correct": "print('Hello World')",
                    "explanation": "The print() function is used to output text in Python."
                }
            ],
            "intermediate": [
                {
                    "question": "What does the 'len()' function return for a list?",
                    "options": ["The last element", "The first element", "The number of elements", "The memory size"],
                    "correct": "The number of elements",
                    "explanation": "len() returns the count of items in a sequence or collection."
                },
                {
                    "question": "Which keyword is used to define a function in Python?",
                    "options": ["function", "def", "func", "define"],
                    "correct": "def",
                    "explanation": "The 'def' keyword is used to define functions in Python."
                },
                {
                    "question": "What is the result of '3 == 3' in Python?",
                    "options": ["3", "True", "False", "Error"],
                    "correct": "True",
                    "explanation": "The == operator compares values and returns a boolean result."
                }
            ]
        },
        "mathematics": {
            "beginner": [
                {
                    "question": "What is 15 + 27?",
                    "options": ["41", "42", "43", "44"],
                    "correct": "42",
                    "explanation": "15 + 27 = 42"
                },
                {
                    "question": "What is 8 × 7?",
                    "options": ["54", "55", "56", "57"],
                    "correct": "56",
                    "explanation": "8 × 7 = 56"
                }
            ],
            "intermediate": [
                {
                    "question": "What is the square root of 144?",
                    "options": ["12", "13", "14", "15"],
                    "correct": "12",
                    "explanation": "12 × 12 = 144, so √144 = 12"
                },
                {
                    "question": "If x + 5 = 12, what is x?",
                    "options": ["6", "7", "8", "9"],
                    "correct": "7",
                    "explanation": "x = 12 - 5 = 7"
                }
            ]
        }
    }
    
    # Get questions for the topic and difficulty
    questions_pool = quiz_templates.get(topic.lower(), {}).get(difficulty, [])
    
    if not questions_pool:
        # Generate generic questions if topic not found
        questions_pool = [
            {
                "question": f"Which concept is most important in {topic}?",
                "options": ["Foundation concepts", "Advanced techniques", "Practical applications", "All of the above"],
                "correct": "All of the above",
                "explanation": f"All aspects are important for mastering {topic}."
            }
        ]
    
    # Select random questions (with replacement if needed)
    selected_questions = []
    for i in range(min(num_questions, len(questions_pool))):
        question = questions_pool[i % len(questions_pool)].copy()
        question["id"] = f"q_{i+1}"
        selected_questions.append(question)
    
    return selected_questions


# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "AI Tutor Service",
        "status": "healthy",
        "version": "1.0.0",
        "capabilities": [
            "chat_tutoring",
            "spaced_repetition", 
            "adaptive_content",
            "gamification",
            "quiz_generation",
            "analytics_integration"
        ]
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_with_tutor(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    Main chat endpoint for AI tutoring conversations.
    Provides intelligent responses and learning suggestions.
    """
    try:
        # Generate AI response (mock implementation)
        ai_response = generate_mock_ai_response(request.message)
        
        # Store chat history
        store.add_chat_message(request.user_id, request.message, ai_response)
        
        # Get adaptive suggestions based on user profile
        suggestions = store.get_adaptive_suggestions(request.user_id, request.context)
        
        session_id = f"session_{request.user_id}_{datetime.datetime.now().isoformat()}"
        
        # Fire analytics event
        event = AnalyticsEvent(
            user_id=request.user_id,
            event_type="chat_interaction",
            event_data={
                "message_length": len(request.message),
                "response_length": len(ai_response),
                "context": request.context,
                "session_id": session_id
            }
        )
        background_tasks.add_task(fire_analytics_event, event)
        
        return ChatResponse(
            response=ai_response,
            suggestions=suggestions,
            session_id=session_id,
            timestamp=datetime.datetime.now().isoformat()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@app.get("/chat/history/{user_id}")
async def get_chat_history(user_id: str, limit: int = 20):
    """Get chat history for a user"""
    try:
        history = store.get_chat_history(user_id)
        # Return most recent messages first
        return {"chat_history": history[-limit:]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chat history: {str(e)}")

@app.get("/spaced-repetition/{user_id}")
async def get_spaced_repetition_schedule(user_id: str):
    """Get user's spaced repetition schedule"""
    try:
        schedule = store.get_spaced_repetition_schedule(user_id)
        due_items = store.get_items_due_for_review(user_id)
        
        return {
            "schedule": schedule,
            "due_items": due_items,
            "total_items": len(schedule),
            "items_due": len(due_items)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get spaced repetition schedule: {str(e)}")

@app.post("/spaced-repetition/update")
async def update_spaced_repetition(request: SpacedRepetitionUpdate, background_tasks: BackgroundTasks):
    """Update spaced repetition schedule based on user performance"""
    try:
        if request.performance not in ["easy", "good", "hard", "forgot"]:
            raise HTTPException(status_code=400, detail="Performance must be one of: easy, good, hard, forgot")
        
        updated_item = store.update_spaced_repetition(request.user_id, request.item_id, request.performance)
        
        # Fire analytics event
        event = AnalyticsEvent(
            user_id=request.user_id,
            event_type="spaced_repetition_review",
            event_data={
                "item_id": request.item_id,
                "performance": request.performance,
                "new_interval": updated_item["interval"],
                "ease_factor": updated_item["ease_factor"]
            }
        )
        background_tasks.add_task(fire_analytics_event, event)
        
        return {
            "message": "Spaced repetition updated successfully",
            "updated_item": updated_item
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update spaced repetition: {str(e)}")

@app.get("/adaptive-content/{user_id}")
async def get_adaptive_content(user_id: str, topic: Optional[str] = None):
    """Get adaptive content suggestions for user"""
    try:
        suggestions = store.get_adaptive_suggestions(user_id, topic)
        user_profile = store.adaptive_content.get(user_id, {})
        
        return {
            "suggestions": suggestions,
            "user_profile": {
                "learning_style": user_profile.get("learning_style"),
                "difficulty_preference": user_profile.get("difficulty_preference"),
                "topic_interests": user_profile.get("topic_interests", [])
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get adaptive content: {str(e)}")

@app.post("/quiz/generate", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest, background_tasks: BackgroundTasks):
    """Generate a quiz based on topic and difficulty"""
    try:
        quiz_id = f"quiz_{request.user_id}_{datetime.datetime.now().isoformat()}"
        questions = generate_mock_quiz(request.topic, request.difficulty, request.num_questions)
        time_limit = request.num_questions * 2  # 2 minutes per question
        
        # Store quiz in memory for validation
        if not hasattr(store, 'active_quizzes'):
            store.active_quizzes = {}
        
        store.active_quizzes[quiz_id] = {
            "user_id": request.user_id,
            "topic": request.topic,
            "questions": questions,
            "created_at": datetime.datetime.now().isoformat(),
            "time_limit_minutes": time_limit
        }
        
        # Fire analytics event
        event = AnalyticsEvent(
            user_id=request.user_id,
            event_type="quiz_generated",
            event_data={
                "quiz_id": quiz_id,
                "topic": request.topic,
                "difficulty": request.difficulty,
                "num_questions": request.num_questions
            }
        )
        background_tasks.add_task(fire_analytics_event, event)
        
        # Remove correct answers from response (send only to validate later)
        questions_for_response = []
        for q in questions:
            question_copy = q.copy()
            del question_copy["correct"]  # Don't send correct answer to client
            questions_for_response.append(question_copy)
        
        return QuizResponse(
            quiz_id=quiz_id,
            questions=questions_for_response,
            time_limit_minutes=time_limit
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate quiz: {str(e)}")

@app.post("/quiz/submit")
async def submit_quiz(submission: QuizSubmission, background_tasks: BackgroundTasks):
    """Submit quiz answers and get results"""
    try:
        if not hasattr(store, 'active_quizzes') or submission.quiz_id not in store.active_quizzes:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        quiz = store.active_quizzes[submission.quiz_id]
        
        if quiz["user_id"] != submission.user_id:
            raise HTTPException(status_code=403, detail="Not authorized to submit this quiz")
        
        # Grade the quiz
        total_questions = len(quiz["questions"])
        correct_answers = 0
        results = []
        
        for question in quiz["questions"]:
            user_answer = submission.answers.get(question["id"], "")
            is_correct = user_answer == question["correct"]
            if is_correct:
                correct_answers += 1
            
            results.append({
                "question_id": question["id"],
                "question": question["question"],
                "user_answer": user_answer,
                "correct_answer": question["correct"],
                "is_correct": is_correct,
                "explanation": question.get("explanation", "")
            })
        
        score_percentage = (correct_answers / total_questions) * 100
        
        # Award points based on performance
        base_points = total_questions * 10
        bonus_multiplier = score_percentage / 100
        points_awarded = int(base_points * bonus_multiplier)
        
        store.add_points(submission.user_id, points_awarded, f"Quiz: {quiz['topic']} ({score_percentage:.1f}%)")
        
        # Fire analytics event
        event = AnalyticsEvent(
            user_id=submission.user_id,
            event_type="quiz_completed",
            event_data={
                "quiz_id": submission.quiz_id,
                "topic": quiz["topic"],
                "score_percentage": score_percentage,
                "correct_answers": correct_answers,
                "total_questions": total_questions,
                "points_awarded": points_awarded
            }
        )
        background_tasks.add_task(fire_analytics_event, event)
        
        # Clean up quiz from memory
        del store.active_quizzes[submission.quiz_id]
        
        return {
            "quiz_id": submission.quiz_id,
            "score": {
                "correct": correct_answers,
                "total": total_questions,
                "percentage": score_percentage
            },
            "results": results,
            "points_awarded": points_awarded,
            "message": "Great job!" if score_percentage >= 80 else "Keep practicing!" if score_percentage >= 60 else "Review the material and try again!"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit quiz: {str(e)}")

@app.get("/gamification/{user_id}")
async def get_gamification_stats(user_id: str):
    """Get user's gamification statistics"""
    try:
        stats = store.get_user_stats(user_id)
        badges = store.get_user_badges(user_id)
        points_history = store.points_history.get(user_id, [])
        
        return {
            "stats": stats,
            "badges": badges,
            "recent_points": points_history[-10:],  # Last 10 point transactions
            "next_milestone": {
                "points": ((stats["total_points"] // 100) + 1) * 100,
                "progress": stats["total_points"] % 100
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get gamification stats: {str(e)}")

@app.get("/analytics/{user_id}/summary")
async def get_user_analytics_summary(user_id: str):
    """Get comprehensive analytics summary for user"""
    try:
        stats = store.get_user_stats(user_id)
        chat_history = store.get_chat_history(user_id)
        schedule = store.get_spaced_repetition_schedule(user_id)
        
        # Calculate additional metrics
        recent_activity = len([msg for msg in chat_history if 
                              datetime.datetime.fromisoformat(msg["timestamp"]) > 
                              datetime.datetime.now() - datetime.timedelta(days=7)])
        
        mastery_level = "Beginner"
        if stats["topics_mastered"] > 10:
            mastery_level = "Advanced"
        elif stats["topics_mastered"] > 5:
            mastery_level = "Intermediate"
        
        return {
            "user_id": user_id,
            "overview": stats,
            "activity": {
                "recent_chat_messages": recent_activity,
                "items_in_schedule": len(schedule),
                "items_due": len([item for item in schedule if item.get("due", False)]),
                "mastery_level": mastery_level
            },
            "achievements": {
                "total_badges": stats["total_badges"],
                "current_streak": stats["current_streak"],
                "total_points": stats["total_points"]
            },
            "recommendations": store.get_adaptive_suggestions(user_id)[:3]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get analytics summary: {str(e)}")

@app.get("/dashboard/{user_id}")
async def get_user_dashboard(user_id: str):
    """Get comprehensive user dashboard with all learning metrics"""
    try:
        dashboard_data = {
            "user_id": user_id,
            "points": store.get_user_points(user_id),
            "badges": store.get_user_badges(user_id),
            "spaced_repetition": {
                "due_today": len([item for item in store.get_spaced_repetition_schedule(user_id) 
                                if item.get("next_review_date", "").startswith(datetime.datetime.now().strftime("%Y-%m-%d"))]),
                "total_items": len(store.get_spaced_repetition_schedule(user_id)),
                "schedule": store.get_spaced_repetition_schedule(user_id)[:5]  # Next 5 items
            },
            "learning_stats": store.get_user_learning_stats(user_id),
            "recent_activity": store.get_chat_history(user_id)[-5:],  # Last 5 interactions
            "recommendations": store.get_adaptive_content_recommendations(user_id)
        }
        
        return {
            "status": "success",
            "data": dashboard_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
