# Скрипт для быстрой проверки Docker запуска

Write-Host "🐳 Проверка Docker сервисов..." -ForegroundColor Cyan
Write-Host ""

# 1. Проверка статуса контейнеров
Write-Host "1️⃣ Статус контейнеров:" -ForegroundColor Yellow
docker-compose ps
Write-Host ""

# 2. Проверка API
Write-Host "2️⃣ Проверка API (http://localhost:8000):" -ForegroundColor Yellow
try {
    $apiResponse = Invoke-RestMethod -Uri "http://localhost:8000" -TimeoutSec 5
    Write-Host "   ✅ API работает: $($apiResponse.message)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ API не отвечает" -ForegroundColor Red
}
Write-Host ""

# 3. Проверка API Stats
Write-Host "3️⃣ Проверка API Stats:" -ForegroundColor Yellow
try {
    $statsResponse = Invoke-RestMethod -Uri "http://localhost:8000/stats" -TimeoutSec 5
    Write-Host "   ✅ Stats работает. Сообщений: $($statsResponse.summary.total_messages)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Stats не отвечает" -ForegroundColor Red
}
Write-Host ""

# 4. Проверка Frontend
Write-Host "4️⃣ Проверка Frontend (http://localhost:3000):" -ForegroundColor Yellow
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -UseBasicParsing
    if ($frontendResponse.StatusCode -eq 200) {
        Write-Host "   ✅ Frontend работает" -ForegroundColor Green
    }
} catch {
    Write-Host "   ❌ Frontend не отвечает" -ForegroundColor Red
}
Write-Host ""

# 5. Проверка базы данных
Write-Host "5️⃣ Проверка базы данных:" -ForegroundColor Yellow
if (Test-Path "data/messages.db") {
    $dbSize = (Get-Item "data/messages.db").Length / 1KB
    Write-Host "   ✅ База данных создана: $([math]::Round($dbSize, 2)) KB" -ForegroundColor Green
} else {
    Write-Host "   ❌ База данных не найдена" -ForegroundColor Red
}
Write-Host ""

# 6. Последние логи бота
Write-Host "6️⃣ Последние логи бота:" -ForegroundColor Yellow
docker-compose logs --tail=5 bot
Write-Host ""

Write-Host "✅ Проверка завершена!" -ForegroundColor Green
Write-Host ""
Write-Host "📖 Команды:" -ForegroundColor Cyan
Write-Host "   docker-compose logs -f        # Смотреть все логи"
Write-Host "   docker-compose logs -f bot    # Логи бота"
Write-Host "   docker-compose stop           # Остановить"
Write-Host "   docker-compose down           # Остановить и удалить"
Write-Host ""
Write-Host "🌐 Открыть в браузере:" -ForegroundColor Cyan
Write-Host "   start http://localhost:8000   # API"
Write-Host "   start http://localhost:3000   # Frontend"
