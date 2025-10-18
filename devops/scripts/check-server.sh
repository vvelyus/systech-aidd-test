#!/bin/bash
# ==============================================================================
# Server Readiness Check Script
# ==============================================================================
# Скрипт проверки готовности сервера к развертыванию
# Sprint D2: Manual Deploy
#
# Использование:
#   ./check-server.sh <ssh_key_path>
#
# Пример:
#   ./check-server.sh ~/.ssh/id_rsa
# ==============================================================================

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Параметры сервера
SERVER_IP="89.223.67.136"
SERVER_USER="systech"
SERVER_DIR="/opt/systech/vvelyus"

# Функции для вывода
print_header() {
    echo ""
    echo "=========================================="
    echo "$1"
    echo "=========================================="
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

# Проверка аргументов
if [ "$#" -ne 1 ]; then
    echo "Использование: $0 <ssh_key_path>"
    echo "Пример: $0 ~/.ssh/id_rsa"
    exit 1
fi

SSH_KEY="$1"

# Проверка наличия SSH ключа
if [ ! -f "$SSH_KEY" ]; then
    print_error "SSH ключ не найден: $SSH_KEY"
    exit 1
fi

print_header "🔍 Проверка готовности сервера"

# ==============================================================================
# 1. Проверка SSH подключения
# ==============================================================================
print_header "1. SSH Подключение"

if ssh -i "$SSH_KEY" -o ConnectTimeout=5 -o BatchMode=yes "$SERVER_USER@$SERVER_IP" exit 2>/dev/null; then
    print_success "SSH подключение к $SERVER_IP успешно"
else
    print_error "Не удалось подключиться к серверу через SSH"
    print_info "Проверьте:"
    print_info "  - Корректность SSH ключа"
    print_info "  - Права на ключ (chmod 600 $SSH_KEY)"
    print_info "  - Доступность сервера"
    exit 1
fi

# ==============================================================================
# 2. Проверка Docker
# ==============================================================================
print_header "2. Docker"

DOCKER_VERSION=$(ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "docker --version 2>/dev/null" || echo "not installed")

if [[ "$DOCKER_VERSION" == *"not installed"* ]]; then
    print_error "Docker не установлен на сервере"
    exit 1
else
    print_success "Docker установлен: $DOCKER_VERSION"

    # Проверка минимальной версии (20.10)
    VERSION_NUM=$(echo "$DOCKER_VERSION" | grep -oP '\d+\.\d+' | head -1)
    REQUIRED_VERSION="20.10"

    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$VERSION_NUM" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
        print_success "Версия Docker подходит (>= $REQUIRED_VERSION)"
    else
        print_warning "Версия Docker устарела. Рекомендуется >= $REQUIRED_VERSION"
    fi
fi

# Проверка прав на Docker
if ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "docker ps >/dev/null 2>&1"; then
    print_success "Пользователь имеет права на Docker"
else
    print_error "Пользователь не имеет прав на Docker"
    print_info "Добавьте пользователя в группу docker:"
    print_info "  sudo usermod -aG docker $SERVER_USER"
    exit 1
fi

# ==============================================================================
# 3. Проверка Docker Compose
# ==============================================================================
print_header "3. Docker Compose"

COMPOSE_VERSION=$(ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "docker-compose --version 2>/dev/null" || echo "not installed")

if [[ "$COMPOSE_VERSION" == *"not installed"* ]]; then
    print_error "Docker Compose не установлен на сервере"
    exit 1
else
    print_success "Docker Compose установлен: $COMPOSE_VERSION"

    # Проверка минимальной версии (2.0)
    if [[ "$COMPOSE_VERSION" == *"v2."* ]] || [[ "$COMPOSE_VERSION" == *"version 2."* ]]; then
        print_success "Версия Docker Compose подходит (>= 2.0)"
    else
        print_warning "Версия Docker Compose устарела. Рекомендуется >= 2.0"
    fi
fi

# ==============================================================================
# 4. Проверка портов
# ==============================================================================
print_header "4. Порты"

check_port() {
    local port=$1
    local service=$2

    if ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "netstat -tuln 2>/dev/null | grep -q :$port" || \
       ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "ss -tuln 2>/dev/null | grep -q :$port"; then
        print_warning "Порт $port уже занят (конфликт с $service)"
        return 1
    else
        print_success "Порт $port свободен ($service)"
        return 0
    fi
}

PORTS_OK=true
check_port 8001 "API" || PORTS_OK=false
check_port 3001 "Frontend" || PORTS_OK=false

if [ "$PORTS_OK" = false ]; then
    print_warning "Некоторые порты заняты. Возможны конфликты."
fi

# ==============================================================================
# 5. Проверка директорий
# ==============================================================================
print_header "5. Директории"

if ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "[ -d $SERVER_DIR ]"; then
    print_warning "Рабочая директория уже существует: $SERVER_DIR"

    # Проверка содержимого
    if ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "[ -f $SERVER_DIR/docker-compose.prod.yml ]"; then
        print_warning "  - docker-compose.prod.yml уже существует"
    fi

    if ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "[ -f $SERVER_DIR/.env ]"; then
        print_warning "  - .env уже существует"
    fi

    if ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "[ -d $SERVER_DIR/data ]"; then
        DB_SIZE=$(ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "du -h $SERVER_DIR/data/messages.db 2>/dev/null | cut -f1" || echo "нет")
        print_warning "  - База данных уже существует (размер: $DB_SIZE)"
    fi
else
    print_success "Рабочая директория не существует (будет создана)"
fi

# Проверка прав на создание директории
if ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "sudo test -w /opt/systech || sudo mkdir -p /opt/systech"; then
    print_success "Есть права на создание директории"
else
    print_error "Нет прав на создание директории /opt/systech"
    exit 1
fi

# ==============================================================================
# 6. Проверка сети и DNS
# ==============================================================================
print_header "6. Сеть и DNS"

# Проверка доступности GitHub Container Registry
if ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "ping -c 1 ghcr.io >/dev/null 2>&1"; then
    print_success "Доступ к ghcr.io (GitHub Container Registry)"
else
    print_warning "Нет доступа к ghcr.io через ping (но может работать через HTTPS)"
fi

# Проверка HTTPS доступа к GHCR
if ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "curl -s -o /dev/null -w '%{http_code}' https://ghcr.io | grep -q '200\|301\|302'"; then
    print_success "HTTPS доступ к GitHub Container Registry"
else
    print_error "Нет HTTPS доступа к GitHub Container Registry"
    print_info "Проверьте firewall и прокси настройки"
fi

# ==============================================================================
# 7. Проверка ресурсов
# ==============================================================================
print_header "7. Ресурсы сервера"

# Свободное место на диске
DISK_SPACE=$(ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "df -h / | tail -1 | awk '{print \$4}'")
DISK_USAGE=$(ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "df -h / | tail -1 | awk '{print \$5}'")

print_info "Свободное место: $DISK_SPACE (использовано: $DISK_USAGE)"

DISK_USAGE_NUM=${DISK_USAGE%\%}
if [ "$DISK_USAGE_NUM" -lt 80 ]; then
    print_success "Достаточно места на диске"
elif [ "$DISK_USAGE_NUM" -lt 90 ]; then
    print_warning "Мало места на диске (< 20%)"
else
    print_error "Критически мало места на диске"
fi

# Оперативная память
MEMORY_INFO=$(ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "free -h | grep Mem | awk '{print \$2\" total, \"\$7\" available\"}'")
print_info "Память: $MEMORY_INFO"

# ==============================================================================
# 8. Проверка файрвола
# ==============================================================================
print_header "8. Firewall"

if ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "command -v ufw >/dev/null 2>&1"; then
    UFW_STATUS=$(ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "sudo ufw status 2>/dev/null | head -1" || echo "inactive")

    if [[ "$UFW_STATUS" == *"active"* ]]; then
        print_info "UFW активен"

        # Проверка правил для портов
        if ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "sudo ufw status | grep -q 8001"; then
            print_success "  Порт 8001 открыт в UFW"
        else
            print_warning "  Порт 8001 не открыт в UFW"
            print_info "    Откройте порт: sudo ufw allow 8001/tcp"
        fi

        if ssh -i "$SSH_KEY" "$SERVER_USER@$SERVER_IP" "sudo ufw status | grep -q 3001"; then
            print_success "  Порт 3001 открыт в UFW"
        else
            print_warning "  Порт 3001 не открыт в UFW"
            print_info "    Откройте порт: sudo ufw allow 3001/tcp"
        fi
    else
        print_info "UFW не активен"
    fi
else
    print_info "UFW не установлен"
fi

# ==============================================================================
# Итоговая сводка
# ==============================================================================
print_header "📊 Итоговая сводка"

print_success "Сервер готов к развертыванию!"
echo ""
print_info "Следующие шаги:"
print_info "  1. Подготовьте .env файл с реальными токенами"
print_info "  2. Запустите развертывание:"
print_info "     ./devops/scripts/deploy.sh $SSH_KEY"
echo ""
print_info "Или следуйте ручной инструкции:"
print_info "  docs/guides/MANUAL_DEPLOY.md"
echo ""

exit 0
