# Скрипт быстрого исправления фронтенда на production сервере
# Использование: .\fix-frontend.ps1

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Исправление фронтенда - Module not found" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Проверяем, что мы в правильной директории
if (-not (Test-Path "docker-compose.prod.yml")) {
    Write-Host "❌ Ошибка: файл docker-compose.prod.yml не найден" -ForegroundColor Red
    Write-Host "Убедитесь, что вы находитесь в директории проекта" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Директория проекта найдена" -ForegroundColor Green
Write-Host ""

# Обновляем код из репозитория
Write-Host "📥 Обновление кода из Git..." -ForegroundColor Yellow
git pull origin main
Write-Host "✅ Код обновлен" -ForegroundColor Green
Write-Host ""

# Коммитим и пушим изменения, если есть
Write-Host "📤 Публикация исправлений в Git..." -ForegroundColor Yellow
git add devops/Dockerfile.frontend frontend/web/next.config.ts FRONTEND_MODULE_FIX.md
git commit -m "fix: Исправление Dockerfile фронтенда для production сборки" -ErrorAction SilentlyContinue
git push origin main -ErrorAction SilentlyContinue
Write-Host "✅ Изменения опубликованы" -ForegroundColor Green
Write-Host ""

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Теперь выполните на сервере:" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "cd /root/systech-aidd-test" -ForegroundColor White
Write-Host "bash fix-frontend.sh" -ForegroundColor White
Write-Host ""
Write-Host "Или скопируйте команды:" -ForegroundColor Yellow
Write-Host ""
Write-Host "git pull origin main" -ForegroundColor White
Write-Host "docker-compose -f docker-compose.prod.yml stop frontend" -ForegroundColor White
Write-Host "docker-compose -f docker-compose.prod-rebuild.yml build --no-cache frontend" -ForegroundColor White
Write-Host "docker-compose -f docker-compose.prod-rebuild.yml up -d frontend" -ForegroundColor White
Write-Host "docker-compose -f docker-compose.prod-rebuild.yml logs -f frontend" -ForegroundColor White
Write-Host ""
