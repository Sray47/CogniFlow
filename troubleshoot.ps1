# CogniFlow Troubleshooting Script
# This script helps diagnose common issues with the no-database mode

Write-Host "🔧 CogniFlow Troubleshooting" -ForegroundColor Cyan
Write-Host "=============================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 System Check:" -ForegroundColor Yellow
Write-Host ""

# Check Docker
Write-Host "1. Docker Status:" -ForegroundColor White
try {
    $dockerVersion = docker --version
    Write-Host "   ✅ $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Docker not found or not running" -ForegroundColor Red
}

# Check Docker Compose
Write-Host "2. Docker Compose Status:" -ForegroundColor White
try {
    $composeVersion = docker-compose --version
    Write-Host "   ✅ $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Docker Compose not found" -ForegroundColor Red
}

Write-Host ""
Write-Host "📊 Container Status:" -ForegroundColor Yellow
Write-Host ""

# Check running containers
$containers = docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
if ($containers) {
    Write-Host $containers
} else {
    Write-Host "   ⚠️  No containers currently running" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🌐 Test Connectivity:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Testing API Gateway connection..." -ForegroundColor White
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
    Write-Host "   ✅ API Gateway responding" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Cannot connect to API Gateway at localhost:8000" -ForegroundColor Red
    Write-Host "      Make sure containers are running!" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎯 Need more help?" -ForegroundColor Cyan
Write-Host "   1. Check container logs: docker-compose logs" -ForegroundColor White
Write-Host "   2. Run no-db mode: docker-compose -f docker-compose.no-db.yml up" -ForegroundColor White
Write-Host "   3. Run db mode: docker-compose up" -ForegroundColor White
