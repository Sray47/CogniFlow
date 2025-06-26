#!/bin/bash

# CogniFlow Development Setup Script
# This script helps set up the development environment

echo "🧠 CogniFlow Development Setup"
echo "==============================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Function to install Node.js dependencies
install_node_deps() {
    echo "📦 Installing Node.js dependencies..."
    
    # API Gateway
    echo "Installing API Gateway dependencies..."
    cd services/api-gateway
    npm install
    cd ../..
    
    # Frontend
    echo "Installing Frontend dependencies..."
    cd frontend
    npm install
    cd ..
    
    echo "✅ Node.js dependencies installed"
}

# Function to install Python dependencies
install_python_deps() {
    echo "🐍 Installing Python dependencies..."
    
    # Users Service
    echo "Installing Users Service dependencies..."
    cd services/users-service
    if command -v python3 &> /dev/null; then
        python3 -m pip install -r requirements.txt
    elif command -v python &> /dev/null; then
        python -m pip install -r requirements.txt
    else
        echo "⚠️  Python not found. Skipping Python dependencies."
    fi
    cd ../..
    
    # Courses Service
    echo "Installing Courses Service dependencies..."
    cd services/courses-service
    if command -v python3 &> /dev/null; then
        python3 -m pip install -r requirements.txt
    elif command -v python &> /dev/null; then
        python -m pip install -r requirements.txt
    else
        echo "⚠️  Python not found. Skipping Python dependencies."
    fi
    cd ../..
    
    echo "✅ Python dependencies installed"
}

# Function to start services with Docker
start_docker() {
    echo "🚀 Starting all services with Docker Compose..."
    docker-compose up --build -d
    
    echo ""
    echo "🎉 CogniFlow is starting up!"
    echo ""
    echo "📋 Service URLs:"
    echo "   Frontend:    http://localhost:3000"
    echo "   API Gateway: http://localhost:8000"
    echo "   API Docs:    http://localhost:8000/docs"
    echo ""
    echo "📊 To view logs: docker-compose logs -f"
    echo "🛑 To stop:      docker-compose down"
}

# Function to start services locally
start_local() {
    echo "🔧 Starting services locally..."
    echo "Note: You'll need to start each service in separate terminals:"
    echo ""
    echo "Terminal 1 - API Gateway:"
    echo "cd services/api-gateway && npm start"
    echo ""
    echo "Terminal 2 - Users Service:"
    echo "cd services/users-service && uvicorn main:app --reload --port 8001"
    echo ""
    echo "Terminal 3 - Courses Service:"
    echo "cd services/courses-service && uvicorn main:app --reload --port 8002"
    echo ""
    echo "Terminal 4 - Frontend:"
    echo "cd frontend && npm start"
}

# Main menu
echo ""
echo "Choose setup option:"
echo "1) Full Docker setup (recommended)"
echo "2) Local development setup"
echo "3) Install dependencies only"
echo "4) Docker start (if already set up)"

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        install_node_deps
        install_python_deps
        start_docker
        ;;
    2)
        install_node_deps
        install_python_deps
        start_local
        ;;
    3)
        install_node_deps
        install_python_deps
        echo "✅ Dependencies installed. Use option 1 or 2 to start services."
        ;;
    4)
        start_docker
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "🎓 Happy learning with CogniFlow!"
