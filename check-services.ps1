# Quick Services Check Script
# Sprint D1 - Manual Verification Helper

Write-Host "🔍 Sprint D1 Services Check" -ForegroundColor Cyan
Write-Host "=" * 50

# 1. Check containers
Write-Host "`n📦 Container Status:" -ForegroundColor Yellow
docker-compose -f docker-compose.registry.yml ps

# 2. Check API
Write-Host "`n🚀 API Health Check:" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri http://localhost:8000/health -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ API is UP (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "❌ API is DOWN" -ForegroundColor Red
}

# 3. Check Frontend
Write-Host "`n🎨 Frontend Check:" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri http://localhost:3000 -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Frontend is UP (Status: $($response.StatusCode))" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend is DOWN" -ForegroundColor Red
}

# 4. Check Database
Write-Host "`n💾 Database Check:" -ForegroundColor Yellow
if (Test-Path "data\messages.db") {
    $size = (Get-Item "data\messages.db").Length / 1KB
    Write-Host "✅ Database exists (Size: $([math]::Round($size, 2)) KB)" -ForegroundColor Green
} else {
    Write-Host "❌ Database not found" -ForegroundColor Red
}

# 5. Check GHCR images
Write-Host "`n🐳 GHCR Images:" -ForegroundColor Yellow
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | Select-String "ghcr.io/vvelyus"

# 6. Recent logs summary
Write-Host "`n📋 Recent Logs (last 3 lines per service):" -ForegroundColor Yellow
Write-Host "`nBot:" -ForegroundColor Cyan
docker-compose -f docker-compose.registry.yml logs --tail 3 bot

Write-Host "`nAPI:" -ForegroundColor Cyan
docker-compose -f docker-compose.registry.yml logs --tail 3 api

Write-Host "`nFrontend:" -ForegroundColor Cyan
docker-compose -f docker-compose.registry.yml logs --tail 3 frontend

Write-Host "`n" + ("=" * 50)
Write-Host "✅ Check complete!" -ForegroundColor Green
Write-Host "`n📌 Quick Actions:"
Write-Host "  - API Docs:    http://localhost:8000/docs"
Write-Host "  - Frontend:    http://localhost:3000"
Write-Host "  - View logs:   docker-compose -f docker-compose.registry.yml logs -f"
