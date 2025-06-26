# CogniFlow Setup Script for Database Mode
# This script allows you to easily run CogniFlow with PostgreSQL and Redis

Write-Host "🧠 CogniFlow - Database Mode Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "📋 Checking Docker status..." -ForegroundColor Yellow
try {
    docker version | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🚀 Starting CogniFlow in Database Mode..." -ForegroundColor Yellow
Write-Host "This mode uses PostgreSQL and Redis for data persistence." -ForegroundColor Gray
Write-Host ""

# Stop any existing containers
Write-Host "🛑 Stopping any existing containers..." -ForegroundColor Yellow
docker-compose down 2>$null

# Build and start containers with database
Write-Host "🏗️  Building and starting services with database..." -ForegroundColor Yellow
docker-compose up --build

Write-Host ""
Write-Host "🎉 CogniFlow is now running in Database Mode!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Access the application:" -ForegroundColor Cyan
Write-Host "   - Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   - API Gateway: http://localhost:8000" -ForegroundColor White
Write-Host "   - API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   - PostgreSQL: localhost:5432" -ForegroundColor White
Write-Host "   - Redis: localhost:6379" -ForegroundColor White
Write-Host ""
Write-Host "💡 To switch to no-database mode, run: .\start-no-db.ps1" -ForegroundColor Gray
