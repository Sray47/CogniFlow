import React, { useState, useEffect, useCallback } from 'react';
import './App.css';

// --- Interfaces for Type Safety ---
interface User {
  user_id: string;
  username: string;
  email: string;
  full_name: string;
  role: string;
  status: string;
}

interface Course {
  id: number;
  title: string;
  description: string;
  instructor_name: string;
  difficulty: string;
  status: string;
  category: string;
  estimated_duration_hours: number;
  enrollment_count: number;
  rating: number;
  total_ratings: number;
  tags: string[];
  price: number;
  image_url: string;
}

interface Lesson {
  id: number;
  title: string;
  type: string;
  duration_minutes: number;
  order_index: number;
}

interface CourseWithLessons extends Course {
  lessons: Lesson[];
}

interface UserPreferences {
  learning_style: string;
  difficulty_preference: string;
  ui_preferences: {
    theme: string;
  };
  notification_settings: {
    email_notifications: boolean;
  };
}

interface LearningAnalytics {
  user_id: string;
  total_events: number;
  learning_patterns: {
    most_active_hour: number | null;
    most_active_day: string | null;
    session_frequency: number;
    learning_consistency: number;
  };
  performance: {
    total_quizzes: number;
    average_quiz_score: number;
    quiz_improvement_trend: string;
  };
  engagement: {
    events_last_week: number;
    favorite_activity: string;
  }
}

interface AuthTokens {
  access_token: string;
  refresh_token: string;
}

interface ChatMessage {
  id: string;
  sender: string; // 'user' or 'ai'
  message: string;
  timestamp: Date;
}

interface Notification {
  id: string;
  user_id: string;
  type: string;
  title: string;
  message: string;
  read: boolean;
  created_at: Date;
}

// --- Main Application Component ---
function App() {
  // State Management
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<CourseWithLessons | null>(null);
  const [users, setUsers] = useState<User[]>([
    {
      user_id: "demo_user",
      username: "demo_user",
      email: "demo@cogniflow.ai",
      full_name: "Demo User",
      role: "student",
      status: "active"
    }
  ]);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [userPreferences, setUserPreferences] = useState<UserPreferences | null>({
    learning_style: "visual",
    difficulty_preference: "intermediate",
    ui_preferences: {
      theme: "dark"
    },
    notification_settings: {
      email_notifications: true
    }
  });
  const [userAnalytics, setUserAnalytics] = useState<LearningAnalytics | null>({
    user_id: "demo_user",
    total_events: 27,
    learning_patterns: {
      most_active_hour: 15,
      most_active_day: "Tuesday",
      session_frequency: 3.5,
      learning_consistency: 0.8
    },
    performance: {
      total_quizzes: 12,
      average_quiz_score: 82.5,
      quiz_improvement_trend: "positive"
    },
    engagement: {
      events_last_week: 14,
      favorite_activity: "video_lessons"
    }
  });
  const [platformStats, setPlatformStats] = useState<any>({
    total_users: 150,
    total_courses: courses.length || 0,
    total_events: 2450,
    system_health: {
      active_users_last_24h: 42
    }
  });
  const [activeTab, setActiveTab] = useState('dashboard');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [enrolledCourses, setEnrolledCourses] = useState<number[]>([]);
  
  // Authentication state
  const [authTokens, setAuthTokens] = useState<AuthTokens | null>(null);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showRegisterModal, setShowRegisterModal] = useState(false);
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [registerEmail, setRegisterEmail] = useState('');
  const [registerUsername, setRegisterUsername] = useState('');
  const [registerFullName, setRegisterFullName] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');
  
  // Chat state
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  
  // Notifications state
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [unreadNotifications, setUnreadNotifications] = useState(0);
  const [showNotificationsDropdown, setShowNotificationsDropdown] = useState(false);
  
  // WebSocket connection for real-time notifications
  const [socket, setSocket] = useState<WebSocket | null>(null);

  // Update API_BASE to point to the API Gateway
  const API_BASE = 'http://localhost:8000/api';
  // --- Data Fetching Logic ---
  const fetchCourses = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_BASE}/courses/`);
      if (!response.ok) throw new Error('Failed to fetch courses');
      const data = await response.json();
      // Ensure data is an array
      const courseArray = Array.isArray(data) ? data : [];
      setCourses(courseArray);
      setPlatformStats((prev: any) => ({...prev, total_courses: courseArray.length}));
      
      // Select first user for demo
      if (users.length > 0 && !selectedUser) {
        setSelectedUser(users[0]);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'An unknown error occurred';
      setError(`Could not connect to backend services. Please ensure all microservices are running. Details: ${errorMessage}`);
      console.error("Failed to fetch courses:", err);
    } finally {
      setLoading(false);
    }
  }, [API_BASE, users, selectedUser]);

  const fetchCourseDetails = async (courseId: number) => {
    try {
      const response = await fetch(`${API_BASE}/courses/${courseId}`);
      if (!response.ok) throw new Error('Failed to fetch course details');
      const data = await response.json();
      setSelectedCourse(data);
      setActiveTab('course');
    } catch (err) {
      console.error('Failed to fetch course details:', err);
    }
  };

  const handleUserSelect = (user: User) => {
    setSelectedUser(user);
  };
  
  useEffect(() => {
    fetchCourses();
  }, [fetchCourses]);

  // --- UI Event Handlers ---
  const handlePreferencesChange = (field: keyof UserPreferences, value: any) => {
    if (userPreferences) {
      setUserPreferences({ ...userPreferences, [field]: value });
    }
  };

  const savePreferences = () => {
    alert('Preferences saved successfully!');
  };
  
  const handleEnroll = async (courseId: number) => {
    if (!selectedUser) {
      alert("Please select a user first.");
      return;
    }
    try {
      const response = await fetch(`${API_BASE}/courses/${courseId}/enroll`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(authTokens ? { 'Authorization': `Bearer ${authTokens.access_token}` } : {})
        },
        body: JSON.stringify({
          user_id: selectedUser.user_id,
          course_id: courseId
        }),
      });
      
      if (response.ok) {
        setEnrolledCourses([...enrolledCourses, courseId]);
        
        // Create a notification about course enrollment
        createNotification({
          type: 'COURSE_ENROLLED',
          title: 'Course Enrollment',
          message: `You've successfully enrolled in a new course!`
        });
        
        alert('Successfully enrolled in course!');
      }
    } catch (err) {
      console.error('Failed to enroll:', err);
      alert('Failed to enroll in course');
    }
  };
  const filteredCourses = Array.isArray(courses) ? courses.filter(course => {
    const categoryMatch = selectedCategory === 'all' || course.category === selectedCategory;
    const difficultyMatch = selectedDifficulty === 'all' || course.difficulty === selectedDifficulty;
    return categoryMatch && difficultyMatch;
  }) : [];

  const categories = Array.isArray(courses) ? Array.from(new Set(courses.map(course => course.category))) : [];
  const difficulties = ['beginner', 'intermediate', 'advanced'];

  // Authentication functions
  const handleLogin = async () => {
    try {
      const response = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: loginEmail,
          password: loginPassword,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setAuthTokens(data);
        setShowLoginModal(false);
        
        // For demo, we'll set the selected user
        if (users.length > 0) {
          const loggedInUser = users.find(u => u.email === loginEmail) || users[0];
          setSelectedUser(loggedInUser);
        }
        
        // Create a welcome notification
        createNotification({
          type: 'AUTH',
          title: 'Welcome Back!',
          message: 'You have successfully logged in to CogniFlow.'
        });
      } else {
        alert('Login failed. Please check your credentials.');
      }
    } catch (error) {
      console.error('Login error:', error);
      alert('Login failed. Server error.');
    }
  };

  const handleRegister = async () => {
    try {
      const response = await fetch(`${API_BASE}/users`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: registerEmail,
          username: registerUsername,
          full_name: registerFullName,
          password: registerPassword,
        }),
      });

      if (response.ok) {
        const newUser = await response.json();
        
        // For the demo, add the new user to our local state
        setUsers([...users, newUser]);
        
        // Auto-login after registration
        setLoginEmail(registerEmail);
        setLoginPassword(registerPassword);
        setShowRegisterModal(false);
        setShowLoginModal(true);
        
        // Create a welcome notification
        createNotification({
          type: 'AUTH',
          title: 'Welcome to CogniFlow!',
          message: 'Your account has been created successfully.'
        });
      } else {
        alert('Registration failed. Please try again.');
      }
    } catch (error) {
      console.error('Registration error:', error);
      alert('Registration failed. Server error.');
    }
  };

  const handleLogout = () => {
    setAuthTokens(null);
    setSelectedUser(null);
  };

  // Notification functions
  const createNotification = (notificationData: { type: string; title: string; message: string }) => {
    const newNotification: Notification = {
      id: Date.now().toString(),
      user_id: selectedUser?.user_id || 'demo_user',
      type: notificationData.type,
      title: notificationData.title,
      message: notificationData.message,
      read: false,
      created_at: new Date(),
    };
    
    setNotifications([newNotification, ...notifications]);
    setUnreadNotifications(unreadNotifications + 1);
    
    // Also send to backend
    if (selectedUser) {
      fetch(`${API_BASE}/notifications`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(authTokens ? { 'Authorization': `Bearer ${authTokens.access_token}` } : {})
        },
        body: JSON.stringify({
          user_id: selectedUser.user_id,
          type: newNotification.type,
          title: newNotification.title,
          message: newNotification.message,
        }),
      }).catch(err => console.error('Failed to send notification:', err));
    }
  };

  const markNotificationAsRead = (id: string) => {
    setNotifications(
      notifications.map(notification => 
        notification.id === id ? { ...notification, read: true } : notification
      )
    );
    setUnreadNotifications(Math.max(0, unreadNotifications - 1));
  };

  // AI Tutor Chat functions
  const sendChatMessage = async () => {
    if (!currentMessage.trim() || !selectedUser) return;
    
    // Add user message to chat
    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      message: currentMessage,
      timestamp: new Date(),
    };
    
    setChatMessages([...chatMessages, userMessage]);
    const messageToSend = currentMessage;
    setCurrentMessage('');
    setChatLoading(true);
    
    try {
      const response = await fetch(`${API_BASE}/ai-tutor/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(authTokens ? { 'Authorization': `Bearer ${authTokens.access_token}` } : {})
        },
        body: JSON.stringify({
          user_id: selectedUser.user_id,
          message: messageToSend,
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // Add AI response to chat
        const aiMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          sender: 'ai',
          message: data.response,
          timestamp: new Date(),
        };
        
        setChatMessages(prevMessages => [...prevMessages, aiMessage]);
      } else {
        // Fallback for demo
        const aiMessage: ChatMessage = {
          id: (Date.now() + 1).toString(),
          sender: 'ai',
          message: "I'm here to help you learn! What would you like to know about today?",
          timestamp: new Date(),
        };
        
        setChatMessages(prevMessages => [...prevMessages, aiMessage]);
      }
    } catch (error) {
      console.error('Chat error:', error);
      
      // Fallback for demo
      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        message: "I'm sorry, I'm having trouble connecting to the server. Please try again later.",
        timestamp: new Date(),
      };
      
      setChatMessages(prevMessages => [...prevMessages, aiMessage]);
    } finally {
      setChatLoading(false);
    }
  };

  // Initialize WebSocket connection for real-time notifications
  useEffect(() => {
    if (selectedUser) {
      const ws = new WebSocket(`ws://localhost:8000/api/notifications/ws/${selectedUser.user_id}`);
      
      ws.onopen = () => {
        console.log('WebSocket connection established');
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          const newNotification: Notification = {
            id: Date.now().toString(),
            user_id: selectedUser.user_id,
            type: data.type,
            title: data.title,
            message: data.message,
            read: false,
            created_at: new Date(),
          };
          
          setNotifications(prev => [newNotification, ...prev]);
          setUnreadNotifications(prev => prev + 1);
        } catch (error) {
          console.error('Error processing WebSocket message:', error);
        }
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
      setSocket(ws);
      
      return () => {
        ws.close();
      };
    }
  }, [selectedUser]);

  const handleCompleteLesson = async (courseId: number, lessonId: number) => {
    if (!selectedUser) return;
    
    try {
      const response = await fetch(`${API_BASE}/users/${selectedUser.user_id}/progress/${courseId}/lessons/${lessonId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(authTokens ? { 'Authorization': `Bearer ${authTokens.access_token}` } : {})
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // Update course with new progress
        if (selectedCourse) {
          // Mark lesson as completed in UI
          alert(`Lesson completed! Progress: ${data.progress_percentage}%`);
          
          // Notification about progress
          createNotification({
            type: 'PROGRESS',
            title: 'Lesson Completed',
            message: `You've completed a lesson and made progress in your course!`
          });
          
          // Check if this triggered an achievement
          if (data.progress_percentage >= 50 && data.progress_percentage < 51) {
            createNotification({
              type: 'ACHIEVEMENT',
              title: 'Achievement Unlocked: Halfway Hero',
              message: `You've completed 50% of a course!`
            });
          } else if (data.progress_percentage === 100) {
            createNotification({
              type: 'ACHIEVEMENT',
              title: 'Achievement Unlocked: Course Conqueror',
              message: `You've completed the entire course!`
            });
          }
        }
      }
    } catch (error) {
      console.error('Failed to update lesson progress:', error);
    }
  };

  // Render UI Components
  if (loading) {
    return (
      <div className="App">
        <div className="loading">
          <h2>🔄 Loading CogniFlow Platform...</h2>
          <p>Preparing your learning experience...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="App">
        <div className="error">
          <h2>❌ Platform Connection Error</h2>
          <p>Could not connect to backend services. Please ensure all microservices are running.</p>
          <code>Error details: {error}</code>
          <button onClick={fetchCourses}>Retry Connection</button>
        </div>
      </div>
    );
  }

  return (
    <div className="App">
      <header className="App-header">
        <div className="header-top">
          <h1>🧠 CogniFlow</h1>
          <p className="subtitle">AI-Powered Learning Platform</p>
        </div>

        <div className="nav-tabs">
          <button className={`tab ${activeTab === 'dashboard' ? 'active' : ''}`} onClick={() => setActiveTab('dashboard')}>📊 Dashboard</button>
          <button className={`tab ${activeTab === 'courses' ? 'active' : ''}`} onClick={() => setActiveTab('courses')}>📚 Courses</button>
          {selectedCourse && (
            <button className={`tab ${activeTab === 'course' ? 'active' : ''}`} onClick={() => setActiveTab('course')}>📖 {selectedCourse.title}</button>
          )}
          <button className={`tab ${activeTab === 'ai-tutor' ? 'active' : ''}`} onClick={() => setActiveTab('ai-tutor')}>🤖 AI Tutor</button>
          <button className={`tab ${activeTab === 'settings' ? 'active' : ''}`} onClick={() => setActiveTab('settings')}>⚙️ Settings</button>
        </div>

        <div className="user-section">
          <div className="notifications-icon" onClick={() => setShowNotificationsDropdown(!showNotificationsDropdown)}>
            🔔 {unreadNotifications > 0 && <span className="notification-badge">{unreadNotifications}</span>}
            
            {showNotificationsDropdown && (
              <div className="notifications-dropdown">
                <h3>Notifications</h3>
                {notifications.length === 0 ? (
                  <p>No notifications yet</p>
                ) : (
                  <div className="notifications-list">
                    {notifications.map(notification => (
                      <div 
                        key={notification.id} 
                        className={`notification-item ${!notification.read ? 'unread' : ''}`}
                        onClick={() => markNotificationAsRead(notification.id)}
                      >
                        <div className="notification-header">
                          <strong>{notification.title}</strong>
                          <span className="notification-time">
                            {notification.created_at.toLocaleTimeString()}
                          </span>
                        </div>
                        <p>{notification.message}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
          
          {selectedUser ? (
            <div className="user-info">
              <span>👤 {selectedUser.full_name}</span>
              <button onClick={handleLogout} className="logout-button">Logout</button>
            </div>
          ) : (
            <div className="auth-buttons">
              <button onClick={() => setShowLoginModal(true)}>Login</button>
              <button onClick={() => setShowRegisterModal(true)}>Register</button>
            </div>
          )}
        </div>
      </header>

      <main className="main-content">
        {/* Dashboard */}
        {activeTab === 'dashboard' && platformStats && (
          <div className="dashboard">
            <h2>My Learning Dashboard</h2>
            <div className="stats-grid">
              <div className="stat-card">
                <h3>Platform Overview</h3>
                <div className="stat-item">
                  <span>👥 Users</span>
                  <span>{platformStats.total_users}</span>
                </div>
                <div className="stat-item">
                  <span>📚 Courses</span>
                  <span>{platformStats.total_courses}</span>
                </div>
                <div className="stat-item">
                  <span>📊 Learning Events</span>
                  <span>{platformStats.total_events}</span>
                </div>
                <div className="stat-item">
                  <span>👥 Active Users (24h)</span>
                  <span>{platformStats.system_health.active_users_last_24h}</span>
                </div>
              </div>
              
              {selectedUser && userAnalytics && (
                <>
                  <div className="stat-card">
                    <h3>My Learning Patterns</h3>
                    <div className="stat-item">
                      <span>🔄 Session Frequency</span>
                      <span>{userAnalytics.learning_patterns.session_frequency} sessions/week</span>
                    </div>
                    <div className="stat-item">
                      <span>⏰ Most Active Hour</span>
                      <span>{userAnalytics.learning_patterns.most_active_hour}:00</span>
                    </div>
                    <div className="stat-item">
                      <span>📅 Most Active Day</span>
                      <span>{userAnalytics.learning_patterns.most_active_day}</span>
                    </div>
                    <div className="stat-item">
                      <span>📊 Learning Consistency</span>
                      <span>{(userAnalytics.learning_patterns.learning_consistency * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                  
                  <div className="stat-card">
                    <h3>My Performance</h3>
                    <div className="stat-item">
                      <span>📝 Total Quizzes</span>
                      <span>{userAnalytics.performance.total_quizzes}</span>
                    </div>
                    <div className="stat-item">
                      <span>💯 Average Score</span>
                      <span>{userAnalytics.performance.average_quiz_score}%</span>
                    </div>
                    <div className="stat-item">
                      <span>📈 Improvement Trend</span>
                      <span>{userAnalytics.performance.quiz_improvement_trend}</span>
                    </div>
                  </div>
                  
                  <div className="stat-card">
                    <h3>My Engagement</h3>
                    <div className="stat-item">
                      <span>📊 Total Events</span>
                      <span>{userAnalytics.total_events}</span>
                    </div>
                    <div className="stat-item">
                      <span>📊 Events Last Week</span>
                      <span>{userAnalytics.engagement.events_last_week}</span>
                    </div>
                    <div className="stat-item">
                      <span>❤️ Favorite Activity</span>
                      <span>{userAnalytics.engagement.favorite_activity.replace('_', ' ')}</span>
                    </div>
                  </div>
                </>
              )}
              
              {selectedUser && userPreferences && (
                <div className="stat-card">
                  <h3>My Preferences</h3>
                  <div className="stat-item">
                    <span>🧠 Learning Style</span>
                    <span>{userPreferences.learning_style}</span>
                  </div>
                  <div className="stat-item">
                    <span>📊 Difficulty</span>
                    <span>{userPreferences.difficulty_preference}</span>
                  </div>
                  <div className="stat-item">
                    <span>🎨 UI Theme</span>
                    <span>{userPreferences.ui_preferences.theme}</span>
                  </div>
                  <div className="stat-item">
                    <span>📧 Email Notifications</span>
                    <span>{userPreferences.notification_settings.email_notifications ? 'Enabled' : 'Disabled'}</span>
                  </div>
                </div>
              )}
            </div>
            
            {/* Due Review Items (Spaced Repetition) */}
            <div className="spaced-repetition-section">
              <h3>🔄 Due for Review</h3>
              <div className="review-items">
                <div className="review-item">
                  <h4>Python Variables</h4>
                  <p>Last reviewed: 3 days ago</p>
                  <button>Review Now</button>
                </div>
                <div className="review-item">
                  <h4>JavaScript Functions</h4>
                  <p>Last reviewed: 5 days ago</p>
                  <button>Review Now</button>
                </div>
                <div className="review-item">
                  <h4>React Hooks</h4>
                  <p>Last reviewed: 7 days ago</p>
                  <button>Review Now</button>
                </div>
              </div>
            </div>
            
            {/* Recent Achievements */}
            <div className="achievements-section">
              <h3>🏆 Recent Achievements</h3>
              <div className="achievements-list">
                <div className="achievement">
                  <div className="achievement-icon">🌟</div>
                  <div className="achievement-details">
                    <h4>First Course Completed</h4>
                    <p>Completed your first full course</p>
                  </div>
                </div>
                <div className="achievement">
                  <div className="achievement-icon">🔥</div>
                  <div className="achievement-details">
                    <h4>3-Day Streak</h4>
                    <p>Studied for 3 consecutive days</p>
                  </div>
                </div>
                <div className="achievement">
                  <div className="achievement-icon">🧠</div>
                  <div className="achievement-details">
                    <h4>Quiz Master</h4>
                    <p>Scored 100% on 3 quizzes</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
        
        {/* Courses List */}
        {activeTab === 'courses' && (
          <div>
            <h2>Available Courses</h2>
            
            <div className="filters-section">
              <div className="filter">
                <label>Category:</label>
                <select 
                  value={selectedCategory} 
                  onChange={(e) => setSelectedCategory(e.target.value)}
                >
                  <option value="all">All Categories</option>
                  {categories.map(category => (
                    <option key={category} value={category}>{category}</option>
                  ))}
                </select>
              </div>
              
              <div className="filter">
                <label>Difficulty:</label>
                <select 
                  value={selectedDifficulty} 
                  onChange={(e) => setSelectedDifficulty(e.target.value)}
                >
                  <option value="all">All Levels</option>
                  {difficulties.map(difficulty => (
                    <option key={difficulty} value={difficulty}>
                      {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="courses-grid">
              {filteredCourses.map(course => (
                <div key={course.id} className="course-card">
                  <div className="course-image" style={{backgroundImage: `url(${course.image_url || 'https://via.placeholder.com/300x150?text=Course+Image'})`}}></div>
                  
                  <div className="course-content">
                    <h3 onClick={() => fetchCourseDetails(course.id)} className="course-title">
                      {course.title}
                    </h3>
                    <p className="course-instructor">By {course.instructor_name}</p>
                    <p className="course-description">{course.description}</p>
                    
                    <div className="course-meta">
                      <span className={`difficulty ${course.difficulty}`}>{course.difficulty}</span>
                      <span>⭐ {course.rating} ({course.total_ratings})</span>
                      <span>👥 {course.enrollment_count} enrolled</span>
                      <span>⏱️ {course.estimated_duration_hours}h</span>
                    </div>
                    
                    <div className="course-tags">
                      {course.tags.map(tag => (
                        <span key={tag} className="tag">{tag}</span>
                      ))}
                    </div>
                    
                    <div className="course-actions">
                      <button 
                        onClick={() => fetchCourseDetails(course.id)}
                        className="btn-secondary"
                      >
                        📖 View Details
                      </button>
                      
                      <button 
                        onClick={() => handleEnroll(course.id)}
                        className={`btn-primary ${enrolledCourses.includes(course.id) ? 'enrolled' : ''}`}
                        disabled={enrolledCourses.includes(course.id) || !selectedUser}
                      >
                        {enrolledCourses.includes(course.id) ? '✅ Enrolled' : '🎯 Enroll Now'}
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        
        {/* Individual Course */}
        {activeTab === 'course' && selectedCourse && (
          <div className="course-detail">
            <div className="course-header" style={{backgroundImage: `url(${selectedCourse.image_url || 'https://via.placeholder.com/1200x300?text=Course+Header'})`}}>
              <div className="course-header-content">
                <h2>{selectedCourse.title}</h2>
                <p className="course-instructor">By {selectedCourse.instructor_name}</p>
                <div className="course-meta">
                  <span className={`difficulty ${selectedCourse.difficulty}`}>{selectedCourse.difficulty}</span>
                  <span>⭐ {selectedCourse.rating} ({selectedCourse.total_ratings})</span>
                  <span>👥 {selectedCourse.enrollment_count} enrolled</span>
                  <span>⏱️ {selectedCourse.estimated_duration_hours}h</span>
                </div>
              </div>
            </div>
            
            <div className="course-body">
              <div className="course-description">
                <h3>About this course</h3>
                <p>{selectedCourse.description}</p>
                
                <div className="course-tags">
                  {selectedCourse.tags.map(tag => (
                    <span key={tag} className="tag">{tag}</span>
                  ))}
                </div>
              </div>
              
              <div className="course-lessons">
                <h3>Course Content</h3>
                {selectedCourse.lessons && selectedCourse.lessons.length > 0 ? (
                  <div className="lessons-list">
                    {selectedCourse.lessons.map(lesson => (
                      <div key={lesson.id} className="lesson-item">
                        <div className="lesson-info">
                          <span className="lesson-type">{lesson.type}</span>
                          <h4>{lesson.title}</h4>
                          <span className="lesson-duration">{lesson.duration_minutes} min</span>
                        </div>
                        <div className="lesson-actions">
                          <button 
                            className="btn-complete-lesson"
                            onClick={() => handleCompleteLesson(selectedCourse.id, lesson.id)}
                          >
                            Mark as Complete
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p>No lessons available for this course yet.</p>
                )}
              </div>
            </div>
          </div>
        )}
        
        {/* AI Tutor Chat */}
        {activeTab === 'ai-tutor' && (
          <div className="ai-tutor-section">
            <h2>🤖 AI Learning Assistant</h2>
            <div className="chat-container">
              <div className="chat-messages">
                {chatMessages.length === 0 ? (
                  <div className="welcome-message">
                    <h3>Welcome to your AI Learning Assistant!</h3>
                    <p>I can help you with:</p>
                    <ul>
                      <li>Answering questions about your courses</li>
                      <li>Explaining difficult concepts</li>
                      <li>Creating practice quizzes</li>
                      <li>Providing additional learning resources</li>
                    </ul>
                    <p>What would you like to learn today?</p>
                  </div>
                ) : (
                  chatMessages.map(msg => (
                    <div key={msg.id} className={`chat-message ${msg.sender}`}>
                      <div className="message-avatar">
                        {msg.sender === 'user' ? '👤' : '🤖'}
                      </div>
                      <div className="message-content">
                        <p>{msg.message}</p>
                        <span className="message-time">
                          {msg.timestamp.toLocaleTimeString()}
                        </span>
                      </div>
                    </div>
                  ))
                )}
                {chatLoading && (
                  <div className="chat-message ai">
                    <div className="message-avatar">🤖</div>
                    <div className="message-content typing">
                      <span>.</span><span>.</span><span>.</span>
                    </div>
                  </div>
                )}
              </div>
              
              <div className="chat-input">
                <input 
                  type="text" 
                  placeholder="Ask your learning assistant anything..." 
                  value={currentMessage}
                  onChange={e => setCurrentMessage(e.target.value)}
                  onKeyPress={e => e.key === 'Enter' && sendChatMessage()}
                  disabled={!selectedUser}
                />
                <button onClick={sendChatMessage} disabled={!selectedUser || !currentMessage.trim()}>
                  Send
                </button>
              </div>
            </div>
          </div>
        )}
        
        {/* Settings */}
        {activeTab === 'settings' && userPreferences && (
          <div className="settings-section">
            <h2>⚙️ User Preferences</h2>
            
            <div className="settings-container">
              <div className="settings-group">
                <h3>Learning Preferences</h3>
                
                <div className="setting-item">
                  <label>Learning Style:</label>
                  <select 
                    value={userPreferences.learning_style}
                    onChange={(e) => handlePreferencesChange('learning_style', e.target.value)}
                  >
                    <option value="visual">Visual</option>
                    <option value="auditory">Auditory</option>
                    <option value="reading">Reading/Writing</option>
                    <option value="kinesthetic">Kinesthetic</option>
                  </select>
                </div>
                
                <div className="setting-item">
                  <label>Difficulty Preference:</label>
                  <select 
                    value={userPreferences.difficulty_preference}
                    onChange={(e) => handlePreferencesChange('difficulty_preference', e.target.value)}
                  >
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>
              </div>
              
              <div className="settings-group">
                <h3>UI Preferences</h3>
                
                <div className="setting-item">
                  <label>Theme:</label>
                  <select 
                    value={userPreferences.ui_preferences.theme}
                    onChange={(e) => handlePreferencesChange('ui_preferences', {...userPreferences.ui_preferences, theme: e.target.value})}
                  >
                    <option value="light">Light</option>
                    <option value="dark">Dark</option>
                    <option value="system">System Default</option>
                  </select>
                </div>
              </div>
              
              <div className="settings-group">
                <h3>Notification Settings</h3>
                
                <div className="setting-item checkbox">
                  <label>
                    <input 
                      type="checkbox" 
                      checked={userPreferences.notification_settings.email_notifications}
                      onChange={(e) => handlePreferencesChange('notification_settings', {
                        ...userPreferences.notification_settings, 
                        email_notifications: e.target.checked
                      })}
                    />
                    Email Notifications
                  </label>
                </div>
              </div>
              
              <div className="settings-actions">
                <button onClick={savePreferences} className="btn-primary">
                  Save Preferences
                </button>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Login Modal */}
      {showLoginModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>Login to CogniFlow</h2>
            <div className="form-group">
              <label>Email:</label>
              <input 
                type="email" 
                value={loginEmail} 
                onChange={(e) => setLoginEmail(e.target.value)} 
                placeholder="Enter your email"
              />
            </div>
            <div className="form-group">
              <label>Password:</label>
              <input 
                type="password" 
                value={loginPassword} 
                onChange={(e) => setLoginPassword(e.target.value)} 
                placeholder="Enter your password"
              />
            </div>
            <div className="modal-actions">
              <button onClick={() => setShowLoginModal(false)} className="btn-secondary">
                Cancel
              </button>
              <button onClick={handleLogin} className="btn-primary">
                Login
              </button>
            </div>
            <p className="auth-switch">
              Don't have an account? <button onClick={() => {
                setShowLoginModal(false);
                setShowRegisterModal(true);
              }}>Register</button>
            </p>
          </div>
        </div>
      )}
      
      {/* Register Modal */}
      {showRegisterModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>Create an Account</h2>
            <div className="form-group">
              <label>Email:</label>
              <input 
                type="email" 
                value={registerEmail} 
                onChange={(e) => setRegisterEmail(e.target.value)} 
                placeholder="Enter your email"
              />
            </div>
            <div className="form-group">
              <label>Username:</label>
              <input 
                type="text" 
                value={registerUsername} 
                onChange={(e) => setRegisterUsername(e.target.value)} 
                placeholder="Choose a username"
              />
            </div>
            <div className="form-group">
              <label>Full Name:</label>
              <input 
                type="text" 
                value={registerFullName} 
                onChange={(e) => setRegisterFullName(e.target.value)} 
                placeholder="Enter your full name"
              />
            </div>
            <div className="form-group">
              <label>Password:</label>
              <input 
                type="password" 
                value={registerPassword} 
                onChange={(e) => setRegisterPassword(e.target.value)} 
                placeholder="Choose a password"
              />
            </div>
            <div className="modal-actions">
              <button onClick={() => setShowRegisterModal(false)} className="btn-secondary">
                Cancel
              </button>
              <button onClick={handleRegister} className="btn-primary">
                Register
              </button>
            </div>
            <p className="auth-switch">
              Already have an account? <button onClick={() => {
                setShowRegisterModal(false);
                setShowLoginModal(true);
              }}>Login</button>
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
