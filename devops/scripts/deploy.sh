#!/bin/bash
# ==============================================================================
# Automated Deployment Script
# ==============================================================================
# Скрипт автоматического развертывания на production сервере
# Sprint D2: Manual Deploy
#
# Использование:
#   ./deploy.sh <ssh_key_path>
#
# Пример:
#   ./deploy.sh ~/.ssh/id_rsa
#
# Примечание:
#   - .env файл должен быть подготовлен локально
#   - Следует детальной инструкции из docs/guides/MANUAL_DEPLOY.md
# ==============================================================================

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Параметры сервера
SERVER_IP="89.223.67.136"
SERVER_USER="systech"
SERVER_DIR="/opt/systech/vvelyus"

# Локальные файлы
LOCAL_COMPOSE="docker-compose.prod.yml"
LOCAL_ENV=".env"
LOCAL_PROMPT="prompts/system_prompt.txt"

# Функции для вывода
print_header() {
    echo ""
    echo -e "${BLUE}==========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}==========================================${NC}"
}

print_step() {
    echo -e "\n${BLUE}→${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}!${NC} $1"
}

print_info() {
    echo "  $1"
}

# Обработка ошибок
error_exit() {
    print_error "$1"
    exit 1
}

# Проверка аргументов
if [ "$#" -ne 1 ]; then
    echo "Использование: $0 <ssh_key_path>"
    echo "Пример: $0 ~/.ssh/id_rsa"
    exit 1
fi

SSH_KEY="$1"

# Проверка наличия SSH ключа
if [ ! -f "$SSH_KEY" ]; then
    error_exit "SSH ключ не найден: $SSH_KEY"
fi

print_header "🚀 Развертывание SysTech AI Assistant"
echo "Сервер: $SERVER_USER@$SERVER_IP"
echo "Директория: $SERVER_DIR"

# ==============================================================================
# Этап 1: Проверка локальных файлов
# ==============================================================================
print_header "Этап 1: Проверка локальных файлов"

print_step "Проверка docker-compose.prod.yml"
if [ ! -f "$LOCAL_COMPOSE" ]; then
    error_exit "Файл не найден: $LOCAL_COMPOSE"
fi
print_success "Найден: $LOCAL_COMPOSE"

print_step "Проверка .env файла"
if [ ! -f "$LOCAL_ENV" ]; then
    error_exit "Файл не найден: $LOCAL_ENV"
fi

# Проверка обязательных переменных
if ! grep -q "TELEGRAM_BOT_TOKEN=.*[^_here]$" "$LOCAL_ENV"; then
    print_warning ".env содержит placeholder для TELEGRAM_BOT_TOKEN"
    print_info "Убедитесь, что вы заполнили реальный токен!"
    read -p "Продолжить? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        error_exit "Развертывание отменено"
    fi
fi

if ! grep -q "OPENROUTER_API_KEY=.*[^_here]$" "$LOCAL_ENV"; then
    print_warning ".env содержит placeholder для OPENROUTER_API_KEY"
    print_info "Убедитесь, что вы заполнили реальный ключ!"
    read -p "Продолжить? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        error_exit "Развертывание отменено"
    fi
fi

print_success "Найден: $LOCAL_ENV"

print_step "Проверка system_prompt.txt"
if [ ! -f "$LOCAL_PROMPT" ]; then
    error_exit "Файл не найден: $LOCAL_PROMPT"
fi
print_success "Найден: $LOCAL_PROMPT"

# ==============================================================================
# Этап 2: Проверка доступа к серверу
# ==============================================================================
print_header "Этап 2: Подключение к серверу"

print_step "Проверка SSH подключения"
if ssh -i "$SSH_KEY" -o ConnectTimeout=10 -o BatchMode=yes "$SERVER_USER@$SERVER_IP" exit 2>/dev/null; then
    print_success "SSH подключение успешно"
else
    error_exit "Не удалось подключиться к серверу"
fi

print_step "Проверка Docker"
if ! ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "docker --version >/dev/null 2>&1"; then
    error_exit "Docker не установлен на сервере"
fi
DOCKER_VERSION=$(ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "docker --version")
print_success "$DOCKER_VERSION"

print_step "Проверка Docker Compose"
if ! ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "docker-compose --version >/dev/null 2>&1"; then
    error_exit "Docker Compose не установлен на сервере"
fi
COMPOSE_VERSION=$(ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "docker-compose --version")
print_success "$COMPOSE_VERSION"

# ==============================================================================
# Этап 3: Создание директорий на сервере
# ==============================================================================
print_header "Этап 3: Подготовка директорий"

print_step "Создание рабочей директории"
ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "sudo mkdir -p $SERVER_DIR && sudo chown -R \$USER:\$USER $SERVER_DIR"
print_success "Директория создана: $SERVER_DIR"

print_step "Создание поддиректорий"
ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "cd $SERVER_DIR && mkdir -p data logs prompts"
print_success "Созданы: data/, logs/, prompts/"

# ==============================================================================
# Этап 4: Копирование файлов
# ==============================================================================
print_header "Этап 4: Копирование файлов на сервер"

print_step "Копирование docker-compose.prod.yml"
scp -i "$SSH_KEY" "$LOCAL_COMPOSE" "$SERVER_USER@$SERVER_IP:$SERVER_DIR/" >/dev/null 2>&1
print_success "Скопирован: docker-compose.prod.yml"

print_step "Копирование .env"
scp -i "$SSH_KEY" "$LOCAL_ENV" "$SERVER_USER@$SERVER_IP:$SERVER_DIR/" >/dev/null 2>&1
ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "chmod 600 $SERVER_DIR/.env"
print_success "Скопирован: .env (права: 600)"

print_step "Копирование system_prompt.txt"
scp -i "$SSH_KEY" "$LOCAL_PROMPT" "$SERVER_USER@$SERVER_IP:$SERVER_DIR/prompts/" >/dev/null 2>&1
print_success "Скопирован: prompts/system_prompt.txt"

# Проверка файлов на сервере
print_step "Проверка файлов на сервере"
ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "ls -lh $SERVER_DIR/" | while read line; do
    print_info "$line"
done

# ==============================================================================
# Этап 5: Загрузка Docker образов
# ==============================================================================
print_header "Этап 5: Загрузка Docker образов"

print_step "Загрузка образов из GHCR"
print_info "Это может занять несколько минут..."

ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" << 'EOF'
    docker pull ghcr.io/vvelyus/systech-aidd-test/bot:latest
    docker pull ghcr.io/vvelyus/systech-aidd-test/api:latest
    docker pull ghcr.io/vvelyus/systech-aidd-test/frontend:latest
EOF

print_success "Все образы загружены"

# Проверка образов
print_step "Проверка загруженных образов"
ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "docker images | grep systech-aidd-test" | while read line; do
    print_info "$line"
done

# ==============================================================================
# Этап 6: Запуск сервисов
# ==============================================================================
print_header "Этап 6: Запуск сервисов"

print_step "Запуск Docker Compose"
ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "cd $SERVER_DIR && docker-compose -f docker-compose.prod.yml up -d"
print_success "Сервисы запущены"

# Ожидание запуска
print_step "Ожидание запуска контейнеров (30 секунд)"
sleep 30

print_step "Проверка статуса контейнеров"
ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "cd $SERVER_DIR && docker-compose -f docker-compose.prod.yml ps"

# ==============================================================================
# Этап 7: Миграции базы данных
# ==============================================================================
print_header "Этап 7: Миграции базы данных"

print_step "Запуск миграций Alembic"
if ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "docker exec systech-aidd-api-prod alembic upgrade head 2>/dev/null"; then
    print_success "Миграции выполнены успешно"
else
    print_warning "Миграции не выполнены (возможно, уже применены)"
fi

print_step "Проверка базы данных"
if ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "[ -f $SERVER_DIR/data/messages.db ]"; then
    DB_SIZE=$(ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "du -h $SERVER_DIR/data/messages.db | cut -f1")
    print_success "База данных создана (размер: $DB_SIZE)"
else
    print_warning "База данных не найдена"
fi

# ==============================================================================
# Этап 8: Проверка работоспособности
# ==============================================================================
print_header "Этап 8: Проверка работоспособности"

print_step "Проверка API (healthcheck)"
sleep 5  # Даем API время запуститься
if ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "curl -s http://localhost:8001/health | grep -q healthy"; then
    print_success "API работает: http://$SERVER_IP:8001/health"
else
    print_warning "API не отвечает (может еще запускаться)"
fi

print_step "Проверка Frontend"
if ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "curl -s http://localhost:3001 >/dev/null"; then
    print_success "Frontend работает: http://$SERVER_IP:3001"
else
    print_warning "Frontend не отвечает (может еще запускаться)"
fi

print_step "Проверка логов на ошибки"
ERROR_COUNT=$(ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "cd $SERVER_DIR && docker-compose -f docker-compose.prod.yml logs --tail=50 2>&1 | grep -i 'error\|critical' | wc -l")

if [ "$ERROR_COUNT" -eq 0 ]; then
    print_success "Критических ошибок не обнаружено"
else
    print_warning "Обнаружено $ERROR_COUNT ошибок в логах"
    print_info "Проверьте логи: ssh $SERVER_USER@$SERVER_IP 'cd $SERVER_DIR && docker-compose -f docker-compose.prod.yml logs'"
fi

# ==============================================================================
# Итоговая сводка
# ==============================================================================
print_header "✅ Развертывание завершено"

echo ""
print_info "Доступ к сервисам:"
echo -e "  ${GREEN}API:${NC}      http://$SERVER_IP:8001"
echo -e "  ${GREEN}Frontend:${NC} http://$SERVER_IP:3001"
echo -e "  ${GREEN}Health:${NC}   http://$SERVER_IP:8001/health"
echo ""

print_info "Управление сервисами:"
echo "  # Просмотр логов"
echo "  ssh -i $SSH_KEY $SERVER_USER@$SERVER_IP 'cd $SERVER_DIR && docker-compose -f docker-compose.prod.yml logs -f'"
echo ""
echo "  # Перезапуск"
echo "  ssh -i $SSH_KEY $SERVER_USER@$SERVER_IP 'cd $SERVER_DIR && docker-compose -f docker-compose.prod.yml restart'"
echo ""
echo "  # Остановка"
echo "  ssh -i $SSH_KEY $SERVER_USER@$SERVER_IP 'cd $SERVER_DIR && docker-compose -f docker-compose.prod.yml down'"
echo ""

print_info "Следующие шаги:"
echo "  1. Проверьте работу Telegram бота (отправьте сообщение)"
echo "  2. Откройте Frontend в браузере и протестируйте интерфейс"
echo "  3. Проверьте логи на наличие ошибок"
echo "  4. Настройте автоматический backup"
echo ""

print_success "Полная инструкция: docs/guides/MANUAL_DEPLOY.md"
echo ""

exit 0

