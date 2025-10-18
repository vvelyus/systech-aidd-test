#!/bin/bash
# Скрипт быстрого исправления фронтенда на production сервере
# Использование: bash fix-frontend.sh

set -e

echo "================================================"
echo "Исправление фронтенда - Module not found"
echo "================================================"
echo ""

# Проверяем, что мы в правильной директории
if [ ! -f "docker-compose.prod.yml" ]; then
    echo "❌ Ошибка: файл docker-compose.prod.yml не найден"
    echo "Убедитесь, что вы находитесь в директории /root/systech-aidd-test"
    exit 1
fi

echo "✅ Директория проекта найдена"
echo ""

# Обновляем код из репозитория
echo "📥 Обновление кода из Git..."
git pull origin main
echo "✅ Код обновлен"
echo ""

# Останавливаем текущий фронтенд
echo "🛑 Остановка текущего фронтенда..."
docker-compose -f docker-compose.prod.yml stop frontend
docker-compose -f docker-compose.prod.yml rm -f frontend
echo "✅ Фронтенд остановлен"
echo ""

# Очищаем старые образы
echo "🧹 Очистка старых образов..."
docker images | grep frontend | grep none | awk '{print $3}' | xargs -r docker rmi -f || true
echo "✅ Очистка завершена"
echo ""

# Собираем новый образ фронтенда
echo "🔨 Сборка нового образа фронтенда..."
echo "   (это может занять 3-5 минут)"
docker-compose -f docker-compose.prod-rebuild.yml build --no-cache frontend
echo "✅ Образ собран"
echo ""

# Запускаем фронтенд
echo "🚀 Запуск фронтенда..."
docker-compose -f docker-compose.prod-rebuild.yml up -d frontend
echo "✅ Фронтенд запущен"
echo ""

# Ждем запуска
echo "⏳ Ожидание запуска (30 секунд)..."
sleep 30

# Проверяем статус
echo "🔍 Проверка статуса..."
echo ""

if docker ps | grep -q "systech-aidd-frontend-prod"; then
    echo "✅ Контейнер фронтенда запущен"
else
    echo "❌ Контейнер фронтенда не запущен!"
    echo ""
    echo "Логи контейнера:"
    docker-compose -f docker-compose.prod-rebuild.yml logs --tail=50 frontend
    exit 1
fi

# Проверяем health check
echo ""
echo "🏥 Проверка доступности..."
if curl -s -f http://localhost:3000 > /dev/null; then
    echo "✅ Фронтенд отвечает на запросы"
else
    echo "⚠️  Фронтенд пока не отвечает (возможно, еще запускается)"
fi

echo ""
echo "================================================"
echo "✅ Исправление завершено!"
echo "================================================"
echo ""
echo "Проверьте работу фронтенда:"
echo "  - Главная: http://89.223.67.136:3001"
echo "  - Dashboard: http://89.223.67.136:3001/dashboard"
echo "  - Чат: http://89.223.67.136:3001/chat"
echo ""
echo "Проверьте логи:"
echo "  docker-compose -f docker-compose.prod-rebuild.yml logs -f frontend"
echo ""
echo "Проверьте консоль браузера (F12):"
echo "  - Не должно быть ошибок 'Module not found'"
echo ""
