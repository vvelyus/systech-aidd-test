# Автоматическое обновление Frontend на production сервере
# Sprint D2: Frontend Fix

$SSH_KEY = "C:\Users\v.velyus\.ssh\systech-key.pem"
$SERVER = "systech@89.223.67.136"
$WORK_DIR = "/opt/systech/vvelyus"

Write-Host "🔄 Обновление Frontend на production сервере..." -ForegroundColor Cyan
Write-Host ""

# Команды для выполнения на сервере
$COMMANDS = @"
cd $WORK_DIR && \
echo '📥 Загрузка нового образа Frontend...' && \
docker compose -f docker-compose.prod.yml pull frontend && \
echo '' && \
echo '🔄 Перезапуск Frontend...' && \
docker compose -f docker-compose.prod.yml up -d frontend && \
echo '' && \
echo '⏳ Ожидание запуска (30 секунд)...' && \
sleep 30 && \
echo '' && \
echo '📊 Статус контейнеров:' && \
docker compose -f docker-compose.prod.yml ps && \
echo '' && \
echo '📝 Логи Frontend:' && \
docker logs systech-aidd-frontend-prod --tail 20
"@

# Выполнение команд на сервере
Write-Host "Подключение к серверу $SERVER..." -ForegroundColor Yellow
ssh -i $SSH_KEY $SERVER $COMMANDS

Write-Host ""
Write-Host "✅ Обновление завершено!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Открытие Dashboard..." -ForegroundColor Cyan
Start-Sleep -Seconds 2
Start-Process "http://89.223.67.136:3001/dashboard"

Write-Host ""
Write-Host "Dashboard открыт в браузере: http://89.223.67.136:3001/dashboard" -ForegroundColor Green
