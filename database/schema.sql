-- CogniFlow AI Learning Platform Database Schema
-- Designed for scalability and AI feature integration
-- PostgreSQL 14+

-- Enable UUID extension for better distributed IDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable JSONB functions for analytics data
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- =============================================
-- CORE USER MANAGEMENT
-- =============================================

CREATE TYPE user_role AS ENUM ('student', 'instructor', 'admin');
CREATE TYPE user_status AS ENUM ('active', 'inactive', 'pending', 'suspended');

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role user_role DEFAULT 'student',
    status user_status DEFAULT 'pending',
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    email_verified BOOLEAN DEFAULT FALSE,
    
    -- AI Personalization Fields
    learning_style_preferences JSONB DEFAULT '{}',
    timezone VARCHAR(50) DEFAULT 'UTC',
    preferred_difficulty_level INTEGER DEFAULT 1 CHECK (preferred_difficulty_level BETWEEN 1 AND 5),
    
    -- Index for fast lookups
    CONSTRAINT valid_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- User profiles with extended information
CREATE TABLE user_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    avatar_url VARCHAR(500),
    bio TEXT,
    date_of_birth DATE,
    occupation VARCHAR(255),
    education_level VARCHAR(100),
    interests TEXT[],
    goals TEXT[],
    
    -- AI Features - Cognitive Load Management
    working_memory_capacity INTEGER DEFAULT 7 CHECK (working_memory_capacity BETWEEN 1 AND 15),
    attention_span_minutes INTEGER DEFAULT 25,
    optimal_study_time VARCHAR(50), -- e.g., "morning", "afternoon", "evening"
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- COURSE AND CONTENT MANAGEMENT
-- =============================================

CREATE TYPE course_status AS ENUM ('draft', 'published', 'archived');
CREATE TYPE content_type AS ENUM ('lesson', 'quiz', 'assignment', 'discussion', 'simulation', 'ar_vr_experience');
CREATE TYPE difficulty_level AS ENUM ('beginner', 'intermediate', 'advanced', 'expert');

CREATE TABLE courses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    short_description VARCHAR(500),
    instructor_id UUID NOT NULL REFERENCES users(id),
    status course_status DEFAULT 'draft',
    difficulty_level difficulty_level DEFAULT 'beginner',
    estimated_duration_hours INTEGER,
    thumbnail_url VARCHAR(500),
    
    -- AI Enhancement Fields
    ai_summarization_enabled BOOLEAN DEFAULT TRUE,
    adaptive_difficulty_enabled BOOLEAN DEFAULT TRUE,
    gamification_enabled BOOLEAN DEFAULT TRUE,
    
    -- Course Structure
    learning_objectives TEXT[],
    prerequisites TEXT[],
    tags TEXT[],
    category_id UUID,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    published_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE course_modules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    order_index INTEGER NOT NULL,
    is_optional BOOLEAN DEFAULT FALSE,
    unlock_criteria JSONB DEFAULT '{}', -- For adaptive learning paths
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE course_content (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    module_id UUID NOT NULL REFERENCES course_modules(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content_type content_type NOT NULL,
    order_index INTEGER NOT NULL,
    
    -- Content Storage
    content_data JSONB NOT NULL, -- Flexible storage for different content types
    content_url VARCHAR(500), -- For videos, documents, AR/VR files
    
    -- AI Features
    estimated_time_minutes INTEGER,
    cognitive_load_level INTEGER DEFAULT 3 CHECK (cognitive_load_level BETWEEN 1 AND 10),
    spaced_repetition_interval INTEGER DEFAULT 1, -- Days
    
    -- Adaptive Learning
    prerequisite_content_ids UUID[],
    difficulty_adaptation_enabled BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- USER PROGRESS AND LEARNING ANALYTICS
-- =============================================

CREATE TYPE enrollment_status AS ENUM ('enrolled', 'completed', 'dropped', 'paused');

CREATE TABLE course_enrollments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id UUID NOT NULL REFERENCES courses(id) ON DELETE CASCADE,
    status enrollment_status DEFAULT 'enrolled',
    progress_percentage DECIMAL(5,2) DEFAULT 0.00 CHECK (progress_percentage BETWEEN 0 AND 100),
    
    enrolled_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- AI Personalization Data
    current_difficulty_level INTEGER DEFAULT 1,
    learning_path_adaptations JSONB DEFAULT '{}',
    
    UNIQUE(user_id, course_id)
);

CREATE TABLE content_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content_id UUID NOT NULL REFERENCES course_content(id) ON DELETE CASCADE,
    enrollment_id UUID NOT NULL REFERENCES course_enrollments(id) ON DELETE CASCADE,
    
    status VARCHAR(20) DEFAULT 'not_started', -- not_started, in_progress, completed
    completion_percentage DECIMAL(5,2) DEFAULT 0.00,
    time_spent_minutes INTEGER DEFAULT 0,
    attempts_count INTEGER DEFAULT 0,
    
    -- AI Analytics Data
    interaction_data JSONB DEFAULT '{}', -- Clicks, scrolls, pauses, etc.
    performance_score DECIMAL(5,2), -- For quizzes, assignments
    cognitive_load_indicators JSONB DEFAULT '{}', -- Time per section, revisits, etc.
    
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    last_interaction TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(user_id, content_id)
);

-- =============================================
-- AI-POWERED FEATURES
-- =============================================

-- Spaced Repetition System
CREATE TABLE spaced_repetition_cards (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content_id UUID NOT NULL REFERENCES course_content(id) ON DELETE CASCADE,
    
    ease_factor DECIMAL(4,2) DEFAULT 2.5, -- SM-2 algorithm
    interval_days INTEGER DEFAULT 1,
    repetitions INTEGER DEFAULT 0,
    next_review_date TIMESTAMP WITH TIME ZONE NOT NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_reviewed TIMESTAMP WITH TIME ZONE
);

-- AI Conversation History (Virtual Tutor)
CREATE TABLE ai_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id),
    content_id UUID REFERENCES course_content(id),
    
    conversation_title VARCHAR(255),
    messages JSONB NOT NULL, -- Array of {role: 'user'|'assistant', content: 'text', timestamp}
    context_data JSONB DEFAULT '{}', -- Current lesson, user progress, etc.
    
    -- AI Model Information
    ai_model_used VARCHAR(100),
    total_tokens_used INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Gamification System
CREATE TABLE user_achievements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_type VARCHAR(100) NOT NULL, -- 'course_completion', 'streak', 'quiz_master', etc.
    achievement_data JSONB NOT NULL, -- Specific achievement details
    points_awarded INTEGER DEFAULT 0,
    
    earned_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE user_stats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE UNIQUE,
    
    -- Learning Statistics
    total_courses_enrolled INTEGER DEFAULT 0,
    total_courses_completed INTEGER DEFAULT 0,
    total_learning_time_minutes INTEGER DEFAULT 0,
    current_streak_days INTEGER DEFAULT 0,
    longest_streak_days INTEGER DEFAULT 0,
    total_points INTEGER DEFAULT 0,
    
    -- AI Analytics
    average_cognitive_load DECIMAL(4,2),
    preferred_learning_pace VARCHAR(20), -- 'slow', 'normal', 'fast'
    optimal_session_duration_minutes INTEGER,
    
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- AFFECTIVE COMPUTING (Emotion Recognition)
-- =============================================

CREATE TYPE emotion_state AS ENUM ('confused', 'frustrated', 'engaged', 'bored', 'excited', 'confident', 'overwhelmed');

CREATE TABLE emotion_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content_id UUID REFERENCES course_content(id),
    
    detected_emotion emotion_state NOT NULL,
    confidence_score DECIMAL(4,3), -- 0.000 to 1.000
    detection_method VARCHAR(50), -- 'facial', 'behavioral', 'self_reported'
    
    -- Context
    session_time_elapsed INTEGER, -- Minutes into current session
    content_difficulty_level INTEGER,
    
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- SYSTEM CONFIGURATION AND METADATA
-- =============================================

CREATE TABLE ai_model_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR(100) NOT NULL UNIQUE,
    model_type VARCHAR(50) NOT NULL, -- 'conversational', 'summarization', 'emotion_detection'
    api_endpoint VARCHAR(500),
    configuration JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =============================================
-- INDEXES FOR PERFORMANCE
-- =============================================

-- User-related indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);

-- Course-related indexes
CREATE INDEX idx_courses_instructor ON courses(instructor_id);
CREATE INDEX idx_courses_status ON courses(status);
CREATE INDEX idx_course_content_module ON course_content(module_id);

-- Progress tracking indexes
CREATE INDEX idx_enrollments_user ON course_enrollments(user_id);
CREATE INDEX idx_enrollments_course ON course_enrollments(course_id);
CREATE INDEX idx_content_progress_user ON content_progress(user_id);
CREATE INDEX idx_content_progress_content ON content_progress(content_id);

-- AI feature indexes
CREATE INDEX idx_spaced_repetition_user ON spaced_repetition_cards(user_id);
CREATE INDEX idx_spaced_repetition_next_review ON spaced_repetition_cards(next_review_date);
CREATE INDEX idx_ai_conversations_user ON ai_conversations(user_id);
CREATE INDEX idx_emotion_logs_user ON emotion_logs(user_id);

-- JSONB indexes for analytics queries
CREATE INDEX idx_content_progress_interaction_data ON content_progress USING GIN (interaction_data);
CREATE INDEX idx_user_preferences ON users USING GIN (learning_style_preferences);

-- =============================================
-- FUNCTIONS AND TRIGGERS
-- =============================================

-- Auto-update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to relevant tables
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_profiles_updated_at BEFORE UPDATE ON user_profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_courses_updated_at BEFORE UPDATE ON courses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_course_content_updated_at BEFORE UPDATE ON course_content FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================
-- SAMPLE DATA FOR DEVELOPMENT
-- =============================================

-- Insert sample AI model configurations
INSERT INTO ai_model_configs (model_name, model_type, configuration) VALUES
('gpt-4-turbo', 'conversational', '{"temperature": 0.7, "max_tokens": 1000, "system_prompt": "You are a helpful AI tutor..."}'),
('claude-3-sonnet', 'summarization', '{"temperature": 0.3, "max_tokens": 500}'),
('emotion-detector-v1', 'emotion_detection', '{"confidence_threshold": 0.7, "detection_methods": ["facial", "behavioral"]}');

-- Comments explaining the schema design choices
COMMENT ON TABLE users IS 'Core user table with AI personalization fields for adaptive learning';
COMMENT ON TABLE content_progress IS 'Detailed progress tracking with interaction analytics for AI processing';
COMMENT ON TABLE spaced_repetition_cards IS 'Implements SM-2 algorithm for optimal memory retention';
COMMENT ON TABLE ai_conversations IS 'Stores chat history with virtual AI tutors for context continuity';
COMMENT ON TABLE emotion_logs IS 'Affective computing data for emotional state-aware tutoring';
COMMENT ON COLUMN content_progress.interaction_data IS 'JSONB field storing detailed user interactions: clicks, scrolls, time spent per section, etc.';
COMMENT ON COLUMN users.learning_style_preferences IS 'JSONB field for storing user learning preferences: visual, auditory, kinesthetic, pace, etc.';
