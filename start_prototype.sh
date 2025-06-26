#!/bin/bash

# CogniFlow Refactored Prototype Startup Script
# ==============================================

echo "🚀 Starting CogniFlow Refactored Prototype Services"
echo "=================================================="

# Set environment for no-database mode
export NO_DATABASE_MODE=true

# Function to start a service
start_service() {
    local service_name=$1
    local service_dir=$2
    local port=$3
    
    echo "Starting $service_name on port $port..."
    
    # Change to service directory and start
    cd "$service_dir" || exit 1
    
    # Start service in background
    python main.py &
    
    # Store PID for cleanup
    echo $! > "/tmp/cogniflow_${service_name}.pid"
    
    # Return to root directory
    cd - > /dev/null || exit 1
    
    sleep 2
}

# Function to check if service is running
check_service() {
    local service_name=$1
    local port=$2
    
    if curl -s "http://localhost:$port/health" > /dev/null 2>&1 || curl -s "http://localhost:$port/" > /dev/null 2>&1; then
        echo "✅ $service_name: Running on port $port"
        return 0
    else
        echo "❌ $service_name: Not responding on port $port"
        return 1
    fi
}

# Function to stop all services
stop_services() {
    echo "🛑 Stopping all CogniFlow services..."
    
    for service in auth users courses ai_tutor analytics; do
        if [ -f "/tmp/cogniflow_${service}.pid" ]; then
            pid=$(cat "/tmp/cogniflow_${service}.pid")
            if kill "$pid" 2>/dev/null; then
                echo "Stopped $service (PID: $pid)"
            fi
            rm -f "/tmp/cogniflow_${service}.pid"
        fi
    done
    
    # Kill any remaining Python processes running main.py
    pkill -f "python main.py" 2>/dev/null || true
    
    echo "All services stopped."
}

# Handle Ctrl+C
trap stop_services EXIT INT TERM

# Check if we should stop services
if [ "$1" = "stop" ]; then
    stop_services
    exit 0
fi

# Check if we should just check status
if [ "$1" = "status" ]; then
    echo "📊 Checking service status..."
    echo "=========================="
    
    check_service "Authentication" 8002
    check_service "Users" 8001
    check_service "Courses" 8003
    check_service "AI Tutor" 8000
    check_service "Analytics" 8004
    
    exit 0
fi

# Start all services
echo "🎯 Starting all services in development mode..."
echo ""

# Start each service in the background
start_service "authentication" "services/authentication" 8002
start_service "users" "services/users-service" 8001
start_service "courses" "services/courses-service" 8003
start_service "ai_tutor" "services/ai-tutor-service" 8000
start_service "analytics" "services/learning-analytics" 8004

echo ""
echo "⏳ Waiting for services to initialize..."
sleep 5

# Check service health
echo ""
echo "🏥 Checking service health..."
echo "=========================="

all_healthy=true

if ! check_service "Authentication" 8002; then all_healthy=false; fi
if ! check_service "Users" 8001; then all_healthy=false; fi
if ! check_service "Courses" 8003; then all_healthy=false; fi
if ! check_service "AI Tutor" 8000; then all_healthy=false; fi
if ! check_service "Analytics" 8004; then all_healthy=false; fi

if [ "$all_healthy" = true ]; then
    echo ""
    echo "🎉 All services started successfully!"
    echo ""
    echo "📋 Service URLs:"
    echo "  Authentication: http://localhost:8002"
    echo "  Users:          http://localhost:8001"
    echo "  Courses:        http://localhost:8003"
    echo "  AI Tutor:       http://localhost:8000"
    echo "  Analytics:      http://localhost:8004"
    echo ""
    echo "📚 API Documentation:"
    echo "  Authentication: http://localhost:8002/docs"
    echo "  Users:          http://localhost:8001/docs"
    echo "  Courses:        http://localhost:8003/docs"
    echo "  AI Tutor:       http://localhost:8000/docs"
    echo "  Analytics:      http://localhost:8004/docs"
    echo ""
    echo "🧪 To verify the prototype, run:"
    echo "  python verify_prototype.py"
    echo ""
    echo "🛑 To stop all services, press Ctrl+C or run:"
    echo "  ./start_prototype.sh stop"
    echo ""
    echo "Services are running... Press Ctrl+C to stop."
    
    # Keep the script running
    wait
else
    echo ""
    echo "⚠️  Some services failed to start. Check the logs above."
    echo "   Make sure all dependencies are installed:"
    echo "   pip install fastapi uvicorn pydantic httpx"
    stop_services
    exit 1
fi
