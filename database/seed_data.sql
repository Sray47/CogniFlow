-- CogniFlow Development Seed Data
-- This file populates the database with sample data for development and testing

-- Insert sample users
INSERT INTO users (id, username, email, full_name, role, status, password_hash, email_verified, learning_style_preferences, preferred_difficulty_level) VALUES
('550e8400-e29b-41d4-a716-446655440001', 'alice_learner', 'alice@example.com', 'Alice Johnson', 'student', 'active', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/Lj8CwZbfr6o8.5Ayi', true, '{"preferred_pace": "normal", "learning_style": "visual", "notification_preferences": {"email": true, "push": false}}', 2),
('550e8400-e29b-41d4-a716-446655440002', 'bob_instructor', 'bob@example.com', 'Bob Smith', 'instructor', 'active', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/Lj8CwZbfr6o8.5Ayi', true, '{}', 3),
('550e8400-e29b-41d4-a716-446655440003', 'admin_user', 'admin@cogniflow.com', 'System Administrator', 'admin', 'active', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/Lj8CwZbfr6o8.5Ayi', true, '{}', 4),
('550e8400-e29b-41d4-a716-446655440004', 'emma_student', 'emma@example.com', 'Emma Wilson', 'student', 'active', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/Lj8CwZbfr6o8.5Ayi', true, '{"preferred_pace": "fast", "learning_style": "kinesthetic", "optimal_study_time": "morning"}', 3);

-- Insert user profiles
INSERT INTO user_profiles (user_id, bio, occupation, education_level, interests, goals, working_memory_capacity, attention_span_minutes, optimal_study_time) VALUES
('550e8400-e29b-41d4-a716-446655440001', 'Passionate about learning new technologies and improving my skills.', 'Software Developer', 'Bachelor''s Degree', ARRAY['Programming', 'AI', 'Web Development'], ARRAY['Master Python', 'Learn Machine Learning', 'Build a portfolio project'], 6, 30, 'evening'),
('550e8400-e29b-41d4-a716-446655440002', 'Experienced instructor with a passion for teaching programming.', 'Senior Developer & Instructor', 'Master''s Degree', ARRAY['Teaching', 'Python', 'Data Science'], ARRAY['Create engaging courses', 'Help students succeed'], 8, 45, 'morning'),
('550e8400-e29b-41d4-a716-446655440004', 'Computer science student eager to learn practical skills.', 'Student', 'Currently pursuing Bachelor''s', ARRAY['Machine Learning', 'Algorithms', 'Mobile Development'], ARRAY['Complete CS degree', 'Get internship', 'Build mobile app'], 7, 25, 'morning');

-- Insert sample courses
INSERT INTO courses (id, title, description, short_description, instructor_id, status, difficulty_level, estimated_duration_hours, learning_objectives, prerequisites, tags) VALUES
('650e8400-e29b-41d4-a716-446655440001', 'Introduction to Python Programming', 'A comprehensive course covering Python fundamentals, data structures, and basic algorithms. Perfect for beginners who want to start their programming journey.', 'Learn Python from scratch with hands-on exercises and real-world projects.', '550e8400-e29b-41d4-a716-446655440002', 'published', 'beginner', 40, ARRAY['Understand Python syntax and semantics', 'Work with data structures (lists, dictionaries, sets)', 'Write functions and classes', 'Handle files and exceptions', 'Build a simple command-line application'], ARRAY['Basic computer literacy', 'No prior programming experience required'], ARRAY['python', 'programming', 'beginner', 'fundamentals']),
('650e8400-e29b-41d4-a716-446655440002', 'Machine Learning Fundamentals', 'Dive into the world of machine learning with practical examples using Python and popular libraries like scikit-learn and pandas.', 'Master the basics of ML algorithms and data science workflows.', '550e8400-e29b-41d4-a716-446655440002', 'published', 'intermediate', 60, ARRAY['Understand supervised and unsupervised learning', 'Implement classification and regression algorithms', 'Perform data preprocessing and feature engineering', 'Evaluate model performance', 'Build end-to-end ML pipelines'], ARRAY['Python programming knowledge', 'Basic statistics and mathematics'], ARRAY['machine-learning', 'data-science', 'python', 'algorithms']),
('650e8400-e29b-41d4-a716-446655440003', 'Advanced AI and Deep Learning', 'Explore cutting-edge AI techniques including neural networks, deep learning, and modern architectures like transformers.', 'Build sophisticated AI models for real-world applications.', '550e8400-e29b-41d4-a716-446655440002', 'draft', 'advanced', 80, ARRAY['Design and train neural networks', 'Implement CNNs and RNNs', 'Work with transformer architectures', 'Deploy AI models to production', 'Understand AI ethics and best practices'], ARRAY['Machine learning experience', 'Strong Python skills', 'Linear algebra and calculus'], ARRAY['deep-learning', 'neural-networks', 'ai', 'tensorflow', 'pytorch']);

-- Insert course modules
INSERT INTO course_modules (id, course_id, title, description, order_index) VALUES
-- Python Course Modules
('750e8400-e29b-41d4-a716-446655440001', '650e8400-e29b-41d4-a716-446655440001', 'Getting Started with Python', 'Introduction to Python, installation, and your first program', 1),
('750e8400-e29b-41d4-a716-446655440002', '650e8400-e29b-41d4-a716-446655440001', 'Python Basics', 'Variables, data types, operators, and control structures', 2),
('750e8400-e29b-41d4-a716-446655440003', '650e8400-e29b-41d4-a716-446655440001', 'Data Structures', 'Lists, dictionaries, sets, and tuples', 3),
('750e8400-e29b-41d4-a716-446655440004', '650e8400-e29b-41d4-a716-446655440001', 'Functions and Classes', 'Defining functions, object-oriented programming basics', 4),
('750e8400-e29b-41d4-a716-446655440005', '650e8400-e29b-41d4-a716-446655440001', 'Final Project', 'Build a complete Python application', 5),

-- ML Course Modules
('750e8400-e29b-41d4-a716-446655440006', '650e8400-e29b-41d4-a716-446655440002', 'Introduction to Machine Learning', 'What is ML, types of learning, and the ML workflow', 1),
('750e8400-e29b-41d4-a716-446655440007', '650e8400-e29b-41d4-a716-446655440002', 'Data Preprocessing', 'Cleaning data, handling missing values, feature scaling', 2),
('750e8400-e29b-41d4-a716-446655440008', '650e8400-e29b-41d4-a716-446655440002', 'Supervised Learning', 'Classification and regression algorithms', 3),
('750e8400-e29b-41d4-a716-446655440009', '650e8400-e29b-41d4-a716-446655440002', 'Unsupervised Learning', 'Clustering and dimensionality reduction', 4);

-- Insert sample course content
INSERT INTO course_content (id, module_id, title, content_type, order_index, content_data, estimated_time_minutes, cognitive_load_level) VALUES
-- Python Course Content
('850e8400-e29b-41d4-a716-446655440001', '750e8400-e29b-41d4-a716-446655440001', 'What is Python?', 'lesson', 1, '{"type": "text", "content": "Python is a high-level, interpreted programming language...", "summary": "Introduction to Python and its applications"}', 15, 2),
('850e8400-e29b-41d4-a716-446655440002', '750e8400-e29b-41d4-a716-446655440001', 'Installing Python', 'lesson', 2, '{"type": "video", "video_url": "/videos/python-installation.mp4", "transcript": "In this video, we will install Python..."}', 20, 3),
('850e8400-e29b-41d4-a716-446655440003', '750e8400-e29b-41d4-a716-446655440001', 'Your First Python Program', 'lesson', 3, '{"type": "interactive", "code_editor": true, "starter_code": "print(\"Hello, World!\")", "instructions": "Run your first Python program"}', 25, 4),
('850e8400-e29b-41d4-a716-446655440004', '750e8400-e29b-41d4-a716-446655440001', 'Python Basics Quiz', 'quiz', 4, '{"questions": [{"question": "What is Python?", "type": "multiple_choice", "options": ["A snake", "A programming language", "A food"], "correct": 1}]}', 10, 3),

-- ML Course Content  
('850e8400-e29b-41d4-a716-446655440005', '750e8400-e29b-41d4-a716-446655440006', 'What is Machine Learning?', 'lesson', 1, '{"type": "text", "content": "Machine Learning is a subset of artificial intelligence...", "examples": ["Email spam detection", "Recommendation systems"]}', 30, 5),
('850e8400-e29b-41d4-a716-446655440006', '750e8400-e29b-41d4-a716-446655440006', 'Types of Machine Learning', 'lesson', 2, '{"type": "interactive_diagram", "diagram_type": "ml_types", "content": "Explore supervised, unsupervised, and reinforcement learning"}', 25, 6);

-- Insert course enrollments
INSERT INTO course_enrollments (id, user_id, course_id, status, progress_percentage) VALUES
('950e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', '650e8400-e29b-41d4-a716-446655440001', 'enrolled', 35.50),
('950e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440004', '650e8400-e29b-41d4-a716-446655440001', 'enrolled', 15.25),
('950e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440001', '650e8400-e29b-41d4-a716-446655440002', 'enrolled', 0.00);

-- Insert content progress
INSERT INTO content_progress (id, user_id, content_id, enrollment_id, status, completion_percentage, time_spent_minutes, interaction_data, performance_score) VALUES
('a50e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', '850e8400-e29b-41d4-a716-446655440001', '950e8400-e29b-41d4-a716-446655440001', 'completed', 100.00, 18, '{"clicks": 15, "scrolls": 8, "time_per_section": [300, 450, 630], "revisits": 2}', 95.00),
('a50e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440001', '850e8400-e29b-41d4-a716-446655440002', '950e8400-e29b-41d4-a716-446655440001', 'completed', 100.00, 22, '{"video_pauses": 3, "video_rewinds": 1, "completion_rate": 1.0}', 88.50),
('a50e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440001', '850e8400-e29b-41d4-a716-446655440003', '950e8400-e29b-41d4-a716-446655440001', 'in_progress', 60.00, 15, '{"code_executions": 5, "syntax_errors": 2, "help_requests": 1}', null);

-- Insert user statistics
INSERT INTO user_stats (user_id, total_courses_enrolled, total_courses_completed, total_learning_time_minutes, current_streak_days, total_points, average_cognitive_load, preferred_learning_pace) VALUES
('550e8400-e29b-41d4-a716-446655440001', 2, 0, 280, 5, 150, 4.2, 'normal'),
('550e8400-e29b-41d4-a716-446655440004', 1, 0, 45, 2, 25, 3.8, 'fast');

-- Insert sample achievements
INSERT INTO user_achievements (user_id, achievement_type, achievement_data, points_awarded) VALUES
('550e8400-e29b-41d4-a716-446655440001', 'first_lesson_completed', '{"lesson_id": "850e8400-e29b-41d4-a716-446655440001", "course_id": "650e8400-e29b-41d4-a716-446655440001"}', 10),
('550e8400-e29b-41d4-a716-446655440001', 'quiz_master', '{"quiz_id": "850e8400-e29b-41d4-a716-446655440004", "score": 95.0, "attempts": 1}', 25),
('550e8400-e29b-41d4-a716-446655440001', 'learning_streak', '{"days": 5, "start_date": "2025-06-12"}', 50);

-- Insert spaced repetition cards for active learning
INSERT INTO spaced_repetition_cards (user_id, content_id, ease_factor, interval_days, repetitions, next_review_date) VALUES
('550e8400-e29b-41d4-a716-446655440001', '850e8400-e29b-41d4-a716-446655440001', 2.5, 1, 0, CURRENT_TIMESTAMP + INTERVAL '1 day'),
('550e8400-e29b-41d4-a716-446655440001', '850e8400-e29b-41d4-a716-446655440002', 2.8, 3, 1, CURRENT_TIMESTAMP + INTERVAL '3 days');

-- Insert sample AI conversation (virtual tutor interaction)
INSERT INTO ai_conversations (id, user_id, course_id, content_id, conversation_title, messages, context_data, ai_model_used, total_tokens_used) VALUES
('b50e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', '650e8400-e29b-41d4-a716-446655440001', '850e8400-e29b-41d4-a716-446655440003', 'Help with Python Syntax', 
'[
  {"role": "user", "content": "I''m getting a syntax error in my Python code. Can you help?", "timestamp": "2025-06-17T10:30:00Z"},
  {"role": "assistant", "content": "I''d be happy to help you with the syntax error! Can you share the code that''s causing the issue?", "timestamp": "2025-06-17T10:30:15Z"},
  {"role": "user", "content": "print(Hello, World!)", "timestamp": "2025-06-17T10:31:00Z"},
  {"role": "assistant", "content": "I see the issue! You''re missing quotes around the string. In Python, strings need to be enclosed in quotes. Try this: print(\"Hello, World!\") or print(''Hello, World!'')", "timestamp": "2025-06-17T10:31:30Z"}
]'::jsonb, 
'{"current_lesson": "Your First Python Program", "user_progress": "60%", "difficulty_level": "beginner"}', 
'gpt-4-turbo', 
185);

-- Insert emotion logs for affective computing
INSERT INTO emotion_logs (user_id, content_id, detected_emotion, confidence_score, detection_method, session_time_elapsed, content_difficulty_level) VALUES
('550e8400-e29b-41d4-a716-446655440001', '850e8400-e29b-41d4-a716-446655440003', 'confused', 0.75, 'behavioral', 15, 4),
('550e8400-e29b-41d4-a716-446655440001', '850e8400-e29b-41d4-a716-446655440003', 'engaged', 0.85, 'behavioral', 25, 4),
('550e8400-e29b-41d4-a716-446655440004', '850e8400-e29b-41d4-a716-446655440001', 'excited', 0.92, 'self_reported', 5, 2);

-- Update last_updated timestamp for user_stats
UPDATE user_stats SET last_updated = CURRENT_TIMESTAMP;
