// services/api-gateway/index.js
const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 8000;

// Middleware
app.use(cors()); // Allow requests from our frontend
app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'API Gateway is running', timestamp: new Date().toISOString() });
});

// Define routes to microservices
// These URLs point to the service names defined in docker-compose.yml

// Users Service - User management, profiles, authentication
app.use('/api/users', createProxyMiddleware({ 
    target: 'http://localhost:8001', 
    changeOrigin: true,
    pathRewrite: {
        '^/api/users': '', // Remove /api/users prefix when forwarding
    },
}));

// Courses Service - Course content, lessons, enrollment
app.use('/api/courses', createProxyMiddleware({ 
    target: 'http://localhost:8003', 
    changeOrigin: true,
    pathRewrite: {
        '^/api/courses': '', // Remove /api/courses prefix when forwarding
    },
}));

// Learning Analytics Service - Progress tracking, learning metrics, analytics
app.use('/api/analytics', createProxyMiddleware({ 
    target: 'http://localhost:8004', 
    changeOrigin: true,
    pathRewrite: {
        '^/api/analytics': '', // Remove /api/analytics prefix when forwarding
    },
}));

// Authentication Service - JWT authentication, RBAC, session management
app.use('/api/auth', createProxyMiddleware({ 
    target: 'http://localhost:8005', 
    changeOrigin: true,
    pathRewrite: {
        '^/api/auth': '', // Remove /api/auth prefix when forwarding
    },
}));

// Notifications Service - Real-time notifications, email, push notifications
app.use('/api/notifications', createProxyMiddleware({ 
    target: 'http://localhost:8006', 
    changeOrigin: true,
    pathRewrite: {
        '^/api/notifications': '', // Remove /api/notifications prefix when forwarding
    },
}));

// AI Tutor Service - Conversational AI, spaced repetition, adaptive content
app.use('/api/ai-tutor', createProxyMiddleware({ 
    target: 'http://localhost:8002', 
    changeOrigin: true,
    pathRewrite: {
        '^/api/ai-tutor': '', // Remove /api/ai-tutor prefix when forwarding
    },
}));

// WebSocket proxy for real-time notifications
app.use('/api/notifications/ws', createProxyMiddleware({ 
    target: 'ws://localhost:8006', 
    changeOrigin: true,
    ws: true, // Enable WebSocket proxying
    pathRewrite: {
        '^/api/notifications/ws': '/ws', // Rewrite to /ws endpoint
    },
}));

// Default route
app.get('/', (req, res) => {
    res.json({ 
        message: 'CogniFlow API Gateway',
        version: '1.0.0',
        services: [
            'users-service (port 8001)',
            'courses-service (port 8003)',
            'authentication-service (port 8005)',
            'learning-analytics-service (port 8004)',
            'notifications-service (port 8006)',
            'ai-tutor-service (port 8002)'
        ]
    });
});

app.listen(PORT, () => {
    console.log(`🚀 API Gateway listening on port ${PORT}`);
    console.log(`📋 Available services:`);
    console.log(`   - Users Service: /api/users`);
    console.log(`   - Courses Service: /api/courses`);
    console.log(`   - Authentication Service: /api/auth`);
    console.log(`   - Learning Analytics Service: /api/analytics`);
    console.log(`   - Notifications Service: /api/notifications`);
    console.log(`   - Real-time Notifications: /api/notifications/ws`);
    console.log(`   - AI Tutor Service: /api/ai-tutor`);
});
