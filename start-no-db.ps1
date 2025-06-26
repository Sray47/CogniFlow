# CogniFlow Setup Script for No-Database Mode
# This script allows you to easily run CogniFlow in no-database mode

Write-Host "🧠 CogniFlow - No Database Mode Setup" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
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
Write-Host "🚀 Starting CogniFlow in No-Database Mode..." -ForegroundColor Yellow
Write-Host "This mode uses in-memory data structures instead of PostgreSQL/Redis." -ForegroundColor Gray
Write-Host ""

# Stop any existing containers
Write-Host "🛑 Stopping any existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.no-db.yml down 2>$null

# Build and start containers in no-database mode
Write-Host "🏗️  Building and starting services..." -ForegroundColor Yellow
docker-compose -f docker-compose.no-db.yml up --build

Write-Host ""
Write-Host "🎉 CogniFlow is now running in No-Database Mode!" -ForegroundColor Green
Write-Host ""
Write-Host "📍 Access the application:" -ForegroundColor Cyan
Write-Host "   - Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   - API Gateway: http://localhost:8000" -ForegroundColor White
Write-Host "   - API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "💡 To switch to database mode, run: docker-compose up --build" -ForegroundColor Gray
