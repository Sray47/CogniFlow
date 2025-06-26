#!/usr/bin/env python3
"""
CogniFlow Prototype Verification Script
=====================================

This script tests the refactored CogniFlow services to ensure all store abstractions
are working correctly and the core learning features are functional.

Usage: python verify_prototype.py
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any

# Service endpoints
SERVICES = {
    "auth": "http://localhost:8002",
    "users": "http://localhost:8001", 
    "courses": "http://localhost:8003",
    "ai_tutor": "http://localhost:8000",
    "analytics": "http://localhost:8004"
}

class PrototypeVerifier:
    def __init__(self):
        self.results = {}
        
    async def verify_service_health(self, service_name: str, url: str) -> bool:
        """Check if service is running and healthy"""
        try:
            async with httpx.AsyncClient() as client:
                # Try both /health and / endpoints
                endpoints = ["/health", "/"]
                for endpoint in endpoints:
                    try:
                        response = await client.get(f"{url}{endpoint}", timeout=5.0)
                        if response.status_code == 200:
                            print(f"✅ {service_name.upper()} Service: Healthy")
                            return True
                    except:
                        continue
                        
                print(f"❌ {service_name.upper()} Service: Not responding")
                return False
        except Exception as e:
            print(f"❌ {service_name.upper()} Service: Error - {e}")
            return False

    async def test_course_enrollment_flow(self) -> bool:
        """Test the complete course enrollment and progress flow"""
        print("\n🎓 Testing Course Enrollment Flow...")
        try:
            async with httpx.AsyncClient() as client:
                # 1. List available courses
                response = await client.get(f"{SERVICES['courses']}/courses/")
                if response.status_code != 200:
                    print("❌ Failed to list courses")
                    return False
                
                courses = response.json()
                if not courses:
                    print("❌ No courses available")
                    return False
                
                course_id = courses[0]["id"]
                print(f"✅ Found {len(courses)} courses, using course {course_id}")
                
                # 2. Enroll user in course
                enrollment_data = {"user_id": "test_user", "course_id": course_id}
                response = await client.post(
                    f"{SERVICES['courses']}/courses/{course_id}/enroll",
                    json=enrollment_data
                )
                
                if response.status_code not in [200, 201]:
                    print(f"❌ Enrollment failed: {response.text}")
                    return False
                
                print(f"✅ Successfully enrolled user in course {course_id}")
                
                # 3. Get user enrollments
                response = await client.get(f"{SERVICES['courses']}/users/test_user/enrollments")
                if response.status_code != 200:
                    print("❌ Failed to get user enrollments")
                    return False
                
                enrollments = response.json()
                if not enrollments:
                    print("❌ No enrollments found")
                    return False
                
                print(f"✅ User has {len(enrollments)} enrollments")
                
                # 4. Complete a lesson
                lesson_id = 1  # Assume first lesson
                response = await client.post(
                    f"{SERVICES['courses']}/users/test_user/progress/{course_id}/lessons/{lesson_id}"
                )
                
                if response.status_code not in [200, 201]:
                    print(f"❌ Lesson completion failed: {response.text}")
                    return False
                
                print(f"✅ Successfully completed lesson {lesson_id}")
                
                # 5. Check course progress
                response = await client.get(
                    f"{SERVICES['courses']}/users/test_user/progress/{course_id}"
                )
                
                if response.status_code != 200:
                    print("❌ Failed to get course progress")
                    return False
                
                progress = response.json()
                print(f"✅ Course progress: {progress.get('progress_percentage', 0)}%")
                
                return True
                
        except Exception as e:
            print(f"❌ Course enrollment flow failed: {e}")
            return False

    async def test_ai_tutor_features(self) -> bool:
        """Test AI tutor chat, spaced repetition, and gamification"""
        print("\n🤖 Testing AI Tutor Features...")
        try:
            async with httpx.AsyncClient() as client:
                # 1. Test chat functionality
                chat_data = {
                    "user_id": "test_user",
                    "message": "Hello, can you help me learn Python?",
                    "context": "programming"
                }
                response = await client.post(f"{SERVICES['ai_tutor']}/chat", json=chat_data)
                
                if response.status_code != 200:
                    print(f"❌ Chat failed: {response.text}")
                    return False
                
                chat_response = response.json()
                print(f"✅ Chat response: {chat_response['response'][:50]}...")
                
                # 2. Test spaced repetition schedule
                response = await client.get(f"{SERVICES['ai_tutor']}/spaced-repetition/test_user")
                
                if response.status_code != 200:
                    print(f"❌ Spaced repetition failed: {response.text}")
                    return False
                
                schedule = response.json()
                print(f"✅ Spaced repetition: {schedule.get('items_due', 0)} items due")
                
                # 3. Test gamification stats
                response = await client.get(f"{SERVICES['ai_tutor']}/gamification/test_user")
                
                if response.status_code != 200:
                    print(f"❌ Gamification failed: {response.text}")
                    return False
                
                stats = response.json()
                print(f"✅ Gamification: {stats['stats']['total_points']} points, {len(stats['badges'])} badges")
                
                # 4. Test quiz generation
                quiz_data = {
                    "user_id": "test_user",
                    "topic": "python",
                    "difficulty": "beginner",
                    "num_questions": 3
                }
                response = await client.post(f"{SERVICES['ai_tutor']}/quiz/generate", json=quiz_data)
                
                if response.status_code != 200:
                    print(f"❌ Quiz generation failed: {response.text}")
                    return False
                
                quiz = response.json()
                print(f"✅ Generated quiz with {len(quiz['questions'])} questions")
                
                return True
                
        except Exception as e:
            print(f"❌ AI tutor features failed: {e}")
            return False

    async def test_analytics_events(self) -> bool:
        """Test analytics event recording and retrieval"""
        print("\n📈 Testing Analytics Events...")
        try:
            async with httpx.AsyncClient() as client:
                # 1. Record a test event
                event_data = {
                    "user_id": "test_user",
                    "course_id": 1,
                    "lesson_id": 1,
                    "event_type": "lesson_complete",
                    "event_data": {
                        "duration_minutes": 15,
                        "completion_rate": 0.95
                    }
                }
                response = await client.post(f"{SERVICES['analytics']}/events", json=event_data)
                
                if response.status_code not in [200, 201]:
                    print(f"❌ Event recording failed: {response.text}")
                    return False
                
                print("✅ Successfully recorded analytics event")
                
                # 2. Get user analytics
                response = await client.get(f"{SERVICES['analytics']}/analytics/user/test_user")
                
                if response.status_code != 200:
                    print(f"❌ User analytics failed: {response.text}")
                    return False
                
                analytics = response.json()
                print(f"✅ User analytics: {analytics['analytics']['total_events']} total events")
                
                # 3. Get system analytics
                response = await client.get(f"{SERVICES['analytics']}/analytics/system")
                
                if response.status_code != 200:
                    print(f"❌ System analytics failed: {response.text}")
                    return False
                
                system_analytics = response.json()
                print(f"✅ System analytics: {system_analytics['analytics']['total_events']} total events")
                
                return True
                
        except Exception as e:
            print(f"❌ Analytics events failed: {e}")
            return False

    async def run_verification(self):
        """Run complete verification suite"""
        print("🚀 CogniFlow Prototype Verification")
        print("=" * 50)
        
        # Check service health
        print("\n🏥 Checking Service Health...")
        health_results = {}
        for service_name, url in SERVICES.items():
            health_results[service_name] = await self.verify_service_health(service_name, url)
        
        unhealthy_services = [name for name, healthy in health_results.items() if not healthy]
        if unhealthy_services:
            print(f"\n⚠️  Some services are not running: {unhealthy_services}")
            print("Please start all services before running verification.")
            return
        
        # Run feature tests
        test_results = {}
        
        test_results["enrollment_flow"] = await self.test_course_enrollment_flow()
        test_results["ai_tutor"] = await self.test_ai_tutor_features()
        test_results["analytics"] = await self.test_analytics_events()
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 VERIFICATION SUMMARY")
        print("=" * 50)
        
        passed_tests = sum(1 for result in test_results.values() if result)
        total_tests = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name.upper().replace('_', ' ')}: {status}")
        
        print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("\n🎉 All tests passed! The refactored prototype is working correctly.")
            print("\n🚀 Ready for frontend integration and demonstration!")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} tests failed. Please check the service logs.")


async def main():
    verifier = PrototypeVerifier()
    await verifier.run_verification()


if __name__ == "__main__":
    asyncio.run(main())
