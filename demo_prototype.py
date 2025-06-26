#!/usr/bin/env python3
"""
CogniFlow Prototype Demo Script
==============================

This script demonstrates the key features of the refactored CogniFlow prototype
by simulating a realistic user learning journey.

Usage: python demo_prototype.py
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any

# Service endpoints
SERVICES = {
    "courses": "http://localhost:8003",
    "ai_tutor": "http://localhost:8000",
    "analytics": "http://localhost:8004"
}

class CogniFlowDemo:
    def __init__(self):
        self.user_id = "demo_user"
        
    async def demo_step(self, title: str, description: str):
        """Display a demo step with formatting"""
        print(f"\n{'='*60}")
        print(f"🎯 {title}")
        print(f"{'='*60}")
        print(f"📋 {description}")
        print()
        
        # Small delay for readability
        await asyncio.sleep(1)
    
    async def run_demo(self):
        """Run the complete CogniFlow demo"""
        print("🚀 CogniFlow Prototype Demo")
        print("==========================")
        print("This demo shows how a user interacts with the learning platform.")
        print()
        
        async with httpx.AsyncClient() as client:
            
            # Step 1: Browse and enroll in courses
            await self.demo_step(
                "Step 1: Course Discovery & Enrollment",
                "User browses available courses and enrolls in 'Introduction to AI'"
            )
            
            try:
                # Get available courses
                response = await client.get(f"{SERVICES['courses']}/courses/")
                courses = response.json()
                
                print(f"📚 Available Courses ({len(courses)} found):")
                for course in courses[:3]:  # Show first 3
                    print(f"  • {course['title']} - {course['difficulty']} ({course['enrollment_count']} students)")
                
                # Enroll in first course
                course_id = courses[0]["id"]
                enrollment_data = {"user_id": self.user_id, "course_id": course_id}
                response = await client.post(
                    f"{SERVICES['courses']}/courses/{course_id}/enroll",
                    json=enrollment_data
                )
                
                if response.status_code in [200, 201]:
                    print(f"\n✅ Successfully enrolled in: {courses[0]['title']}")
                else:
                    print(f"\n❌ Enrollment failed: {response.text}")
                    
            except Exception as e:
                print(f"❌ Error in course enrollment: {e}")
            
            # Step 2: AI Tutor Interaction
            await self.demo_step(
                "Step 2: AI Tutor Conversation",
                "User asks the AI tutor for help with learning concepts"
            )
            
            try:
                # Chat with AI tutor
                chat_messages = [
                    "Hello! I just enrolled in the AI course. Can you help me get started?",
                    "What are the main types of machine learning?",
                    "Can you explain what supervised learning is?"
                ]
                
                for message in chat_messages:
                    print(f"👤 User: {message}")
                    
                    chat_data = {
                        "user_id": self.user_id,
                        "message": message,
                        "context": "ai_course"
                    }
                    
                    response = await client.post(f"{SERVICES['ai_tutor']}/chat", json=chat_data)
                    
                    if response.status_code == 200:
                        chat_response = response.json()
                        ai_response = chat_response['response']
                        print(f"🤖 AI Tutor: {ai_response}")
                        
                        if chat_response.get('suggestions'):
                            print(f"💡 Suggestions: {', '.join(chat_response['suggestions'][:2])}")
                    else:
                        print("❌ Chat failed")
                    
                    print()
                    await asyncio.sleep(1)
                    
            except Exception as e:
                print(f"❌ Error in AI chat: {e}")
            
            # Step 3: Learning Progress
            await self.demo_step(
                "Step 3: Learning Progress Tracking",
                "User completes lessons and tracks progress through the course"
            )
            
            try:
                # Complete several lessons
                for lesson_id in [1, 2, 3]:
                    response = await client.post(
                        f"{SERVICES['courses']}/users/{self.user_id}/progress/{course_id}/lessons/{lesson_id}"
                    )
                    
                    if response.status_code in [200, 201]:
                        progress = response.json()
                        print(f"✅ Completed Lesson {lesson_id}")
                        print(f"   Progress: {progress.get('progress_percentage', 0):.1f}% complete")
                        print(f"   Time spent: {progress.get('time_spent_minutes', 0)} minutes")
                    else:
                        print(f"❌ Failed to complete lesson {lesson_id}")
                    
                    await asyncio.sleep(0.5)
                
                # Get overall progress
                response = await client.get(f"{SERVICES['courses']}/users/{self.user_id}/progress/{course_id}")
                if response.status_code == 200:
                    progress = response.json()
                    print(f"\n📊 Overall Course Progress:")
                    print(f"   Completion: {progress.get('progress_percentage', 0):.1f}%")
                    print(f"   Lessons completed: {progress.get('completed_lesson_count', 0)}/{progress.get('total_lessons', 0)}")
                    print(f"   Estimated time remaining: {progress.get('estimated_completion_time_minutes', 0)} minutes")
                    
            except Exception as e:
                print(f"❌ Error in progress tracking: {e}")
            
            # Step 4: Spaced Repetition System
            await self.demo_step(
                "Step 4: Spaced Repetition Learning",
                "User reviews scheduled content using the spaced repetition algorithm"
            )
            
            try:
                # Get spaced repetition schedule
                response = await client.get(f"{SERVICES['ai_tutor']}/spaced-repetition/{self.user_id}")
                
                if response.status_code == 200:
                    schedule = response.json()
                    print(f"📅 Spaced Repetition Schedule:")
                    print(f"   Total items: {schedule.get('total_items', 0)}")
                    print(f"   Items due today: {schedule.get('items_due', 0)}")
                    
                    if schedule.get('due_items'):
                        print(f"\n📝 Items due for review:")
                        for item in schedule['due_items'][:2]:  # Show first 2
                            print(f"   • {item.get('topic', 'Unknown topic')}")
                    
                    # Simulate review session
                    if schedule.get('due_items'):
                        item = schedule['due_items'][0]
                        update_data = {
                            "user_id": self.user_id,
                            "item_id": item['item_id'],
                            "performance": "good"
                        }
                        
                        response = await client.post(
                            f"{SERVICES['ai_tutor']}/spaced-repetition/update",
                            json=update_data
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            updated_item = result['updated_item']
                            print(f"\n✅ Reviewed: {item.get('topic')}")
                            print(f"   Performance: Good")
                            print(f"   Next review: {updated_item['next_review'][:10]}")
                            
            except Exception as e:
                print(f"❌ Error in spaced repetition: {e}")
            
            # Step 5: Gamification & Achievements
            await self.demo_step(
                "Step 5: Gamification & Achievement System",
                "User earns points and badges for learning activities"
            )
            
            try:
                # Get gamification stats
                response = await client.get(f"{SERVICES['ai_tutor']}/gamification/{self.user_id}")
                
                if response.status_code == 200:
                    stats = response.json()
                    user_stats = stats.get('stats', {})
                    badges = stats.get('badges', [])
                    
                    print(f"🏆 Achievement Progress:")
                    print(f"   Total Points: {user_stats.get('total_points', 0)}")
                    print(f"   Current Streak: {user_stats.get('current_streak', 0)} days")
                    print(f"   Topics Mastered: {user_stats.get('topics_mastered', 0)}")
                    print(f"   Sessions Completed: {user_stats.get('total_sessions', 0)}")
                    
                    if badges:
                        print(f"\n🎖️  Earned Badges ({len(badges)}):")
                        for badge in badges[:3]:  # Show first 3
                            badge_info = stats.get('available_badges', {}).get(badge, {})
                            print(f"   • {badge_info.get('name', badge)}")
                    
                    # Show next milestone
                    next_milestone = stats.get('next_milestone', {})
                    if next_milestone:
                        print(f"\n🎯 Next Milestone:")
                        print(f"   Target: {next_milestone.get('points', 0)} points")
                        print(f"   Progress: {next_milestone.get('progress', 0)}/100")
                        
            except Exception as e:
                print(f"❌ Error in gamification: {e}")
            
            # Step 6: Quiz Generation & Assessment
            await self.demo_step(
                "Step 6: Adaptive Quiz System",
                "User takes an AI-generated quiz to test understanding"
            )
            
            try:
                # Generate a quiz
                quiz_data = {
                    "user_id": self.user_id,
                    "topic": "ai",
                    "difficulty": "beginner",
                    "num_questions": 3
                }
                
                response = await client.post(f"{SERVICES['ai_tutor']}/quiz/generate", json=quiz_data)
                
                if response.status_code == 200:
                    quiz = response.json()
                    print(f"📝 Generated Quiz: {quiz['quiz_id']}")
                    print(f"   Topic: AI Fundamentals")
                    print(f"   Questions: {len(quiz['questions'])}")
                    print(f"   Time limit: {quiz['time_limit_minutes']} minutes")
                    
                    # Show first question
                    if quiz['questions']:
                        q = quiz['questions'][0]
                        print(f"\n❓ Sample Question:")
                        print(f"   {q['question']}")
                        for i, option in enumerate(q['options'], 1):
                            print(f"   {i}. {option}")
                    
                    # Simulate quiz submission
                    print(f"\n⏳ Simulating quiz completion...")
                    await asyncio.sleep(2)
                    print(f"✅ Quiz completed with score: 85%")
                    print(f"🏆 Earned 25 points for quiz completion!")
                    
            except Exception as e:
                print(f"❌ Error in quiz generation: {e}")
            
            # Step 7: Analytics Dashboard
            await self.demo_step(
                "Step 7: Learning Analytics Dashboard",
                "System provides insights into learning patterns and progress"
            )
            
            try:
                # Get user analytics
                response = await client.get(f"{SERVICES['analytics']}/analytics/user/{self.user_id}")
                
                if response.status_code == 200:
                    analytics = response.json()['analytics']
                    
                    print(f"📊 Learning Analytics Summary:")
                    print(f"   Total Learning Events: {analytics.get('total_events', 0)}")
                    print(f"   Active Learning Days: {analytics.get('learning_patterns', {}).get('session_frequency', 0)}")
                    print(f"   Average Session Length: {analytics.get('engagement', {}).get('session_length_avg', 0):.1f} minutes")
                    print(f"   Learning Consistency: {analytics.get('learning_patterns', {}).get('learning_consistency', 0):.2f}")
                    
                    # Show activity breakdown
                    event_breakdown = analytics.get('event_breakdown', {})
                    if event_breakdown:
                        print(f"\n📈 Activity Breakdown:")
                        for event_type, count in list(event_breakdown.items())[:3]:
                            print(f"   {event_type.replace('_', ' ').title()}: {count}")
                    
                    # Show performance metrics
                    performance = analytics.get('performance', {})
                    if performance:
                        print(f"\n🎯 Performance Metrics:")
                        print(f"   Quizzes Completed: {performance.get('total_quizzes', 0)}")
                        print(f"   Average Quiz Score: {performance.get('average_quiz_score', 0):.1f}%")
                        print(f"   Improvement Trend: {performance.get('quiz_improvement_trend', 'stable').title()}")
                        
            except Exception as e:
                print(f"❌ Error in analytics: {e}")
            
            # Final Summary
            await self.demo_step(
                "🎉 Demo Complete!",
                "The CogniFlow prototype demonstrates a comprehensive learning platform"
            )
            
            print("🌟 Key Features Demonstrated:")
            print("   ✅ Course enrollment and progress tracking")
            print("   ✅ AI-powered tutoring and conversation")
            print("   ✅ Spaced repetition learning algorithm")
            print("   ✅ Gamification with points and badges")
            print("   ✅ Adaptive quiz generation and assessment")
            print("   ✅ Comprehensive learning analytics")
            print()
            print("🏗️  Architecture Highlights:")
            print("   ✅ Microservices with clean APIs")
            print("   ✅ Store abstraction for easy database migration")
            print("   ✅ Event-driven analytics and insights")
            print("   ✅ Scalable and maintainable code structure")
            print()
            print("🚀 This prototype is ready for:")
            print("   • Frontend integration (React dashboard)")
            print("   • Database migration (PostgreSQL)")
            print("   • Real AI integration (OpenAI, etc.)")
            print("   • Production deployment")


async def main():
    demo = CogniFlowDemo()
    try:
        await demo.run_demo()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        print("Make sure all services are running: ./start_prototype.sh")


if __name__ == "__main__":
    asyncio.run(main())
