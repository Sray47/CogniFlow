# CogniFlow Development Setup Script (PowerShell)
# This script helps set up the development environment on Windows

Write-Host "🧠 CogniFlow Development Setup" -ForegroundColor Blue
Write-Host "===============================" -ForegroundColor Blue

# Check if Docker is installed
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker is installed: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    Write-Host "Visit: https://docs.docker.com/desktop/windows/" -ForegroundColor Yellow
    exit 1
}

# Check if Docker Compose is available
try {
    $composeVersion = docker-compose --version
    Write-Host "✅ Docker Compose is available: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose is not available." -ForegroundColor Red
    exit 1
}

# Function to install Node.js dependencies
function Install-NodeDeps {
    Write-Host "📦 Installing Node.js dependencies..." -ForegroundColor Yellow
    
    # Check if Node.js is installed
    try {
        $nodeVersion = node --version
        Write-Host "✅ Node.js is installed: $nodeVersion" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Node.js not found. Some features may not work locally." -ForegroundColor Yellow
        return
    }
    
    # API Gateway
    Write-Host "Installing API Gateway dependencies..." -ForegroundColor Cyan
    Set-Location "services\api-gateway"
    npm install
    Set-Location "..\..\"
    
    # Frontend
    Write-Host "Installing Frontend dependencies..." -ForegroundColor Cyan
    Set-Location "frontend"
    npm install
    Set-Location ".."
    
    Write-Host "✅ Node.js dependencies installed" -ForegroundColor Green
}

# Function to install Python dependencies
function Install-PythonDeps {
    Write-Host "🐍 Installing Python dependencies..." -ForegroundColor Yellow
    
    # Check if Python is installed
    try {
        $pythonVersion = python --version
        Write-Host "✅ Python is installed: $pythonVersion" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  Python not found. Some features may not work locally." -ForegroundColor Yellow
        return
    }
    
    # Users Service
    Write-Host "Installing Users Service dependencies..." -ForegroundColor Cyan
    Set-Location "services\users-service"
    python -m pip install -r requirements.txt
    Set-Location "..\..\"
    
    # Courses Service
    Write-Host "Installing Courses Service dependencies..." -ForegroundColor Cyan
    Set-Location "services\courses-service"
    python -m pip install -r requirements.txt
    Set-Location "..\..\"
    
    Write-Host "✅ Python dependencies installed" -ForegroundColor Green
}

# Function to start services with Docker
function Start-Docker {
    Write-Host "🚀 Starting all services with Docker Compose..." -ForegroundColor Yellow
    docker-compose up --build -d
    
    Write-Host ""
    Write-Host "🎉 CogniFlow is starting up!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Service URLs:" -ForegroundColor Cyan
    Write-Host "   Frontend:    http://localhost:3000" -ForegroundColor White
    Write-Host "   API Gateway: http://localhost:8000" -ForegroundColor White
    Write-Host "   API Docs:    http://localhost:8000/docs" -ForegroundColor White
    Write-Host ""
    Write-Host "📊 To view logs: docker-compose logs -f" -ForegroundColor Yellow
    Write-Host "🛑 To stop:      docker-compose down" -ForegroundColor Yellow
}

# Function to show local development instructions
function Start-Local {
    Write-Host "🔧 Starting services locally..." -ForegroundColor Yellow
    Write-Host "Note: You'll need to start each service in separate terminals:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Terminal 1 - API Gateway:" -ForegroundColor Cyan
    Write-Host "cd services\api-gateway; npm start" -ForegroundColor White
    Write-Host ""
    Write-Host "Terminal 2 - Users Service:" -ForegroundColor Cyan
    Write-Host "cd services\users-service; uvicorn main:app --reload --port 8001" -ForegroundColor White
    Write-Host ""
    Write-Host "Terminal 3 - Courses Service:" -ForegroundColor Cyan
    Write-Host "cd services\courses-service; uvicorn main:app --reload --port 8002" -ForegroundColor White
    Write-Host ""
    Write-Host "Terminal 4 - Frontend:" -ForegroundColor Cyan
    Write-Host "cd frontend; npm start" -ForegroundColor White
}

# Main menu
Write-Host ""
Write-Host "Choose setup option:" -ForegroundColor Cyan
Write-Host "1) Full Docker setup (recommended)" -ForegroundColor White
Write-Host "2) Local development setup" -ForegroundColor White
Write-Host "3) Install dependencies only" -ForegroundColor White
Write-Host "4) Docker start (if already set up)" -ForegroundColor White

$choice = Read-Host "Enter your choice (1-4)"

switch ($choice) {
    "1" {
        Install-NodeDeps
        Install-PythonDeps
        Start-Docker
    }
    "2" {
        Install-NodeDeps
        Install-PythonDeps
        Start-Local
    }
    "3" {
        Install-NodeDeps
        Install-PythonDeps
        Write-Host "✅ Dependencies installed. Use option 1 or 2 to start services." -ForegroundColor Green
    }
    "4" {
        Start-Docker
    }
    default {
        Write-Host "❌ Invalid choice. Please run the script again." -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "🎓 Happy learning with CogniFlow!" -ForegroundColor Green
