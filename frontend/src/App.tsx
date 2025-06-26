import React, { useState, useEffect } from 'react';
import './App.css';

interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: string;
  status: string;
  created_at: string;
}

interface Course {
  id: number;
  title: string;
  description: string;
  instructor_id: number;
  difficulty: string;
  status: string;
  category: string;
  estimated_duration_hours: number;
  enrollment_count: number;
  rating: number;
  tags: string[];
}

interface UserPreferences {
  learning_style: string;
  preferred_difficulty: string;
  notifications_enabled: boolean;
  theme: string;
}

interface LearningAnalytics {
  user_id: string;
  total_learning_time_minutes: number;
  learning_streak_days: number;
  completion_rate: number;
  engagement_score: number;
  strengths: string[];
  improvement_areas: string[];
}

function App() {
  const [users, setUsers] = useState<User[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [userPreferences, setUserPreferences] = useState<UserPreferences | null>(null);
  const [userAnalytics, setUserAnalytics] = useState<LearningAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('dashboard');

  const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch users from the API Gateway
      const usersResponse = await fetch(`${API_BASE}/api/users/users/`);
      if (!usersResponse.ok) throw new Error('Failed to fetch users');
      const usersData = await usersResponse.json();
      setUsers(usersData);

      // Fetch courses from the API Gateway
      const coursesResponse = await fetch(`${API_BASE}/api/courses/courses/`);
      if (!coursesResponse.ok) throw new Error('Failed to fetch courses');
      const coursesData = await coursesResponse.json();
      setCourses(coursesData);

      // Select first user for demo
      if (usersData.length > 0) {
        setSelectedUser(usersData[0]);
        await fetchUserData(usersData[0].id);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      console.error("Failed to fetch data:", err);
    } finally {
      setLoading(false);
    }
  };

  const fetchUserData = async (userId: string) => {
    try {
      // Fetch user preferences
      const prefsResponse = await fetch(`${API_BASE}/api/users/${userId}/preferences`);
      if (prefsResponse.ok) {
        const prefsData = await prefsResponse.json();
        setUserPreferences(prefsData);
      }

      // Fetch user analytics
      const analyticsResponse = await fetch(`${API_BASE}/api/users/${userId}/learning-analytics`);
      if (analyticsResponse.ok) {
        const analyticsData = await analyticsResponse.json();
        setUserAnalytics(analyticsData);
      }
    } catch (err) {
      console.error("Failed to fetch user data:", err);
    }
  };

  const updateUserPreferences = async (newPrefs: UserPreferences) => {
    if (!selectedUser) return;
    
    try {
      const response = await fetch(`${API_BASE}/api/users/${selectedUser.id}/preferences`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newPrefs),
      });
      
      if (response.ok) {
        const updatedPrefs = await response.json();
        setUserPreferences(updatedPrefs);
        alert('Preferences updated successfully!');
      }
    } catch (err) {
      console.error("Failed to update preferences:", err);
      alert('Failed to update preferences');
    }
  };

  const enrollInCourse = async (courseId: number) => {
    if (!selectedUser) return;
    
    try {
      const response = await fetch(`${API_BASE}/api/courses/${courseId}/enroll/${selectedUser.id}`, {
        method: 'POST',
      });
      
      if (response.ok) {
        alert('Successfully enrolled in course!');
        // Refresh analytics
        await fetchUserData(selectedUser.id);
      }
    } catch (err) {
      console.error("Failed to enroll:", err);
      alert('Failed to enroll in course');
    }
  };

  if (loading) {
    return (
      <div className="App">
        <div className="loading">
          <h2>🔄 Loading CogniFlow...</h2>
          <p>Connecting to AI-powered learning platform...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="App">
        <div className="error">
          <h2>❌ Connection Error</h2>
          <p>{error}</p>
          <p>Make sure all services are running with: <code>docker-compose -f docker-compose.no-db.yml up</code></p>
          <button onClick={fetchData}>Retry Connection</button>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-top">
          <h1>🧠 CogniFlow</h1>
          <h2>AI-Powered Learning Platform</h2>
          <p className="subtitle">Investor Demonstration - Microservices Architecture</p>
        </div>

        {/* Navigation Tabs */}
        <div className="nav-tabs">
          <button 
            className={activeTab === 'dashboard' ? 'tab active' : 'tab'} 
            onClick={() => setActiveTab('dashboard')}
          >
            📊 Dashboard
          </button>
          <button 
            className={activeTab === 'courses' ? 'tab active' : 'tab'} 
            onClick={() => setActiveTab('courses')}
          >
            📚 Courses
          </button>
          <button 
            className={activeTab === 'analytics' ? 'tab active' : 'tab'} 
            onClick={() => setActiveTab('analytics')}
          >
            📈 Analytics
          </button>
          <button 
            className={activeTab === 'profile' ? 'tab active' : 'tab'} 
            onClick={() => setActiveTab('profile')}
          >
            👤 Profile
          </button>
        </div>

        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div className="tab-content">
            <div className="stats-grid">
              <div className="stat-card">
                <h3>👥 Total Users</h3>
                <div className="stat-number">{users.length}</div>
                <div className="stat-detail">Growing community</div>
              </div>
              <div className="stat-card">
                <h3>📚 Available Courses</h3>
                <div className="stat-number">{courses.length}</div>
                <div className="stat-detail">Multi-category content</div>
              </div>
              <div className="stat-card">
                <h3>✅ Published Courses</h3>
                <div className="stat-number">
                  {courses.filter(c => c.status === 'published').length}
                </div>
                <div className="stat-detail">Ready for learners</div>
              </div>
              <div className="stat-card">
                <h3>🎯 Total Enrollments</h3>
                <div className="stat-number">
                  {courses.reduce((sum, c) => sum + c.enrollment_count, 0)}
                </div>
                <div className="stat-detail">Active engagement</div>
              </div>
            </div>

            <div className="demo-features">
              <h3>🚀 Platform Features Demo</h3>
              <div className="features-grid">
                <div className="feature-card">
                  <h4>🤖 AI-Powered Personalization</h4>
                  <p>Adaptive content delivery based on learning patterns</p>
                  <div className="feature-status">✅ Active</div>
                </div>
                <div className="feature-card">
                  <h4>📊 Real-time Analytics</h4>
                  <p>Comprehensive learning progress tracking</p>
                  <div className="feature-status">✅ Active</div>
                </div>
                <div className="feature-card">
                  <h4>🔗 Microservices Architecture</h4>
                  <p>Scalable, maintainable service-oriented design</p>
                  <div className="feature-status">✅ Active</div>
                </div>
                <div className="feature-card">
                  <h4>⚡ Real-time Notifications</h4>
                  <p>WebSocket-based instant communication</p>
                  <div className="feature-status">✅ Active</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Courses Tab */}
        {activeTab === 'courses' && (
          <div className="tab-content">
            <h3>📚 Course Catalog</h3>
            <div className="courses-grid">
              {courses.map(course => (
                <div key={course.id} className="course-card-detailed">
                  <div className="course-header">
                    <h4>{course.title}</h4>
                    <span className={`difficulty ${course.difficulty}`}>
                      {course.difficulty}
                    </span>
                  </div>
                  <p className="course-description">{course.description}</p>
                  <div className="course-meta">
                    <span className="category">📁 {course.category}</span>
                    <span className="duration">⏱️ {course.estimated_duration_hours}h</span>
                    <span className="rating">⭐ {course.rating}</span>
                    <span className="enrollment">👥 {course.enrollment_count}</span>
                  </div>
                  <div className="course-tags">
                    {course.tags.slice(0, 3).map(tag => (
                      <span key={tag} className="tag">{tag}</span>
                    ))}
                  </div>
                  <div className="course-actions">
                    <button 
                      className="enroll-btn"
                      onClick={() => enrollInCourse(course.id)}
                      disabled={course.status !== 'published'}
                    >
                      {course.status === 'published' ? '🎯 Enroll Now' : '🚧 Coming Soon'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && selectedUser && (
          <div className="tab-content">
            <h3>📈 Learning Analytics for {selectedUser.full_name}</h3>
            {userAnalytics ? (
              <div className="analytics-dashboard">
                <div className="analytics-cards">
                  <div className="analytics-card">
                    <h4>📚 Learning Time</h4>
                    <div className="analytics-number">{userAnalytics.total_learning_time_minutes}min</div>
                  </div>
                  <div className="analytics-card">
                    <h4>🔥 Learning Streak</h4>
                    <div className="analytics-number">{userAnalytics.learning_streak_days} days</div>
                  </div>
                  <div className="analytics-card">
                    <h4>✅ Completion Rate</h4>
                    <div className="analytics-number">{(userAnalytics.completion_rate * 100).toFixed(1)}%</div>
                  </div>
                  <div className="analytics-card">
                    <h4>💪 Engagement Score</h4>
                    <div className="analytics-number">{(userAnalytics.engagement_score * 100).toFixed(1)}%</div>
                  </div>
                </div>

                <div className="analytics-insights">
                  <div className="strengths">
                    <h4>💪 Strengths</h4>
                    <ul>
                      {userAnalytics.strengths.map((strength, index) => (
                        <li key={index}>{strength}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="improvements">
                    <h4>🎯 Areas for Improvement</h4>
                    <ul>
                      {userAnalytics.improvement_areas.map((area, index) => (
                        <li key={index}>{area}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ) : (
              <div className="no-analytics">
                <p>Analytics data loading...</p>
              </div>
            )}
          </div>
        )}

        {/* Profile Tab */}
        {activeTab === 'profile' && selectedUser && (
          <div className="tab-content">
            <h3>👤 User Profile: {selectedUser.full_name}</h3>
            
            <div className="profile-section">
              <h4>📋 User Information</h4>
              <div className="user-info-grid">
                <div className="info-item">
                  <label>Username:</label>
                  <span>{selectedUser.username}</span>
                </div>
                <div className="info-item">
                  <label>Email:</label>
                  <span>{selectedUser.email}</span>
                </div>
                <div className="info-item">
                  <label>Role:</label>
                  <span className={`role-badge ${selectedUser.role}`}>{selectedUser.role}</span>
                </div>
                <div className="info-item">
                  <label>Status:</label>
                  <span className={`status-badge ${selectedUser.status}`}>{selectedUser.status}</span>
                </div>
              </div>
            </div>

            {userPreferences && (
              <div className="profile-section">
                <h4>⚙️ Learning Preferences</h4>
                <div className="preferences-form">
                  <div className="form-group">
                    <label>Learning Style:</label>
                    <select 
                      value={userPreferences.learning_style}
                      onChange={(e) => setUserPreferences({...userPreferences, learning_style: e.target.value})}
                    >
                      <option value="visual">🎨 Visual</option>
                      <option value="auditory">🎵 Auditory</option>
                      <option value="kinesthetic">🤹 Kinesthetic</option>
                      <option value="multimodal">🌈 Multimodal</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Preferred Difficulty:</label>
                    <select 
                      value={userPreferences.preferred_difficulty}
                      onChange={(e) => setUserPreferences({...userPreferences, preferred_difficulty: e.target.value})}
                    >
                      <option value="beginner">🌱 Beginner</option>
                      <option value="intermediate">🌿 Intermediate</option>
                      <option value="advanced">🌳 Advanced</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Theme:</label>
                    <select 
                      value={userPreferences.theme}
                      onChange={(e) => setUserPreferences({...userPreferences, theme: e.target.value})}
                    >
                      <option value="light">☀️ Light</option>
                      <option value="dark">🌙 Dark</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>
                      <input 
                        type="checkbox" 
                        checked={userPreferences.notifications_enabled}
                        onChange={(e) => setUserPreferences({...userPreferences, notifications_enabled: e.target.checked})}
                      />
                      Enable Notifications
                    </label>
                  </div>
                  <button 
                    className="save-preferences-btn"
                    onClick={() => updateUserPreferences(userPreferences)}
                  >
                    💾 Save Preferences
                  </button>
                </div>
              </div>
            )}

            <div className="profile-section">
              <h4>👥 Switch User (Demo)</h4>
              <div className="user-selector">
                {users.map(user => (
                  <button 
                    key={user.id}
                    className={`user-option ${selectedUser.id === user.id ? 'selected' : ''}`}
                    onClick={() => {
                      setSelectedUser(user);
                      fetchUserData(user.id);
                    }}
                  >
                    {user.full_name} ({user.role})
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* API Info */}
        <div className="api-info">
          <h3>🔗 Microservices Architecture Status</h3>
          <div className="services-grid">
            <div className="service active">
              <strong>🌐 API Gateway</strong>
              <span>Port 8000 - Request Routing</span>
            </div>
            <div className="service active">
              <strong>👥 Users Service</strong>
              <span>FastAPI + Python - User Management</span>
            </div>
            <div className="service active">
              <strong>📚 Courses Service</strong>
              <span>FastAPI + Python - Content Management</span>
            </div>
            <div className="service active">
              <strong>🔐 Authentication</strong>
              <span>JWT + RBAC - Security</span>
            </div>
            <div className="service active">
              <strong>📊 Analytics</strong>
              <span>Real-time Learning Insights</span>
            </div>
            <div className="service active">
              <strong>🔔 Notifications</strong>
              <span>WebSocket + Real-time</span>
            </div>
            <div className="service active">
              <strong>🤖 AI Tutor</strong>
              <span>Personalized Learning Assistant</span>
            </div>
          </div>
        </div>
      </header>
    </div>
  );
}

export default App;
