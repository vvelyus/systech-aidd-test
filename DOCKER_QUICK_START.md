# 🐳 Быстрый старт с Docker

## Предварительные требования

✅ Docker Desktop установлен и запущен
✅ Файл `.env` настроен (с токенами Telegram и OpenRouter)

## 🚀 Запуск всех сервисов (3 команды)

### 1. Остановить локальные процессы (если запущены)

```powershell
# Если у вас запущен локальный Next.js на порту 3000
# Найдите и остановите процесс
Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess -ErrorAction SilentlyContinue | Stop-Process -Force
```

### 2. Собрать и запустить контейнеры

```powershell
docker-compose up --build -d
```

**Что происходит:**
- Собираются 3 Docker образа (Bot, API, Frontend)
- Запускаются 3 контейнера
- Применяются миграции базы данных
- Создается сеть для взаимодействия сервисов

**Время:**
- Первый раз: ~2-3 минуты
- С кэшем: ~30 секунд

### 3. Проверить статус

```powershell
docker-compose ps
```

Должно быть **все Running**:
```
NAME                    STATUS      PORTS
systech-aidd-api        Up          0.0.0.0:8000->8000/tcp
systech-aidd-bot        Up
systech-aidd-frontend   Up          0.0.0.0:3000->3000/tcp
```

## ✅ Проверка работы

### API Server
```powershell
# Открыть в браузере
start http://localhost:8000

# Или через curl
curl http://localhost:8000/stats
```

### Frontend
```powershell
# Открыть в браузере
start http://localhost:3000
```

### Telegram Bot
Отправьте сообщение боту в Telegram - он должен ответить!

## 📊 Просмотр логов

### Все сервисы сразу
```powershell
docker-compose logs -f
```

### Отдельные сервисы
```powershell
docker-compose logs -f bot       # Telegram Bot
docker-compose logs -f api       # API Server
docker-compose logs -f frontend  # Frontend
```

**Выход из просмотра логов:** `Ctrl+C`

## 🛑 Остановка

### Остановить с сохранением данных
```powershell
docker-compose stop
```

### Остановить и удалить контейнеры
```powershell
docker-compose down
```

### Полная очистка (с удалением volumes)
```powershell
docker-compose down -v
# ⚠️ ВНИМАНИЕ: Удалит базу данных!
```

## 🔄 Перезапуск после изменений

### После изменения кода Python или конфигурации
```powershell
docker-compose restart bot api
```

### После изменения Frontend
```powershell
docker-compose restart frontend
```

### Пересобрать все образы
```powershell
docker-compose up --build -d
```

## 🔍 Диагностика проблем

### Проверить, запущен ли Docker Desktop
```powershell
docker ps
```

### Проверить, какие порты заняты
```powershell
# Порт 3000 (Frontend)
Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue

# Порт 8000 (API)
Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
```

### Посмотреть использование ресурсов
```powershell
docker stats
```

### Зайти внутрь контейнера
```powershell
# Bash в контейнере API
docker exec -it systech-aidd-api bash

# Проверить базу данных
docker exec -it systech-aidd-bot ls -la /app/data/
```

## 📁 Структура проекта

```
systech-aidd-test/
├── docker-compose.yml         # Главная конфигурация
├── .env                       # Ваши переменные окружения
├── devops/
│   ├── Dockerfile.bot         # Bot образ
│   ├── Dockerfile.api         # API образ
│   └── Dockerfile.frontend    # Frontend образ
├── data/
│   └── messages.db           # SQLite база (создается автоматически)
└── logs/
    ├── bot.log               # Логи бота
    └── test.log              # Логи тестов
```

## 🎯 Полезные команды

### Информация о контейнерах
```powershell
docker-compose ps              # Статус
docker-compose top             # Процессы внутри
docker-compose images          # Размеры образов
```

### Очистка Docker
```powershell
# Удалить неиспользуемые образы
docker image prune -a

# Удалить неиспользуемые volumes
docker volume prune

# Полная очистка системы
docker system prune -a
```

## 💡 Советы

1. **Первый запуск:** Займет больше времени из-за скачивания зависимостей
2. **Кэш:** Docker кэширует слои, последующие сборки быстрее
3. **Логи:** Смотрите логи, если что-то не работает: `docker-compose logs -f`
4. **База данных:** Находится в `./data/messages.db`, общая для всех контейнеров
5. **Hot Reload:** Frontend поддерживает hot reload в dev режиме

## 🆘 Частые проблемы

### "Port is already allocated"
**Решение:** Остановите процесс, занимающий порт:
```powershell
# Для порта 3000
Get-Process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess | Stop-Process -Force
```

### "Database is locked"
**Решение:** Остановите все контейнеры и запустите заново:
```powershell
docker-compose down
docker-compose up -d
```

### Контейнер постоянно перезапускается
**Решение:** Посмотрите логи:
```powershell
docker-compose logs bot
```

### Нужно обновить зависимости
**Решение:** Пересоберите образы без кэша:
```powershell
docker-compose build --no-cache
docker-compose up -d
```

## 🌐 Использование готовых образов из Registry

Вместо локальной сборки можно использовать готовые образы из GitHub Container Registry.

### Преимущества
- ✅ **Быстрый старт** - не нужно собирать образы (~10x быстрее)
- ✅ **Тестирование CI** - те же образы, что в production
- ✅ **Экономия ресурсов** - не тратится время на сборку

### Запуск из готовых образов

```powershell
# Использовать специальный compose файл
docker-compose -f docker-compose.registry.yml up -d
```

**Что происходит:**
- Скачиваются готовые образы из ghcr.io
- Запускаются контейнеры (без сборки)
- Применяются миграции и стартуют сервисы

**Время:** ~30 секунд (зависит от скорости интернета)

### Pull конкретных образов

```powershell
# Скачать все образы
docker pull ghcr.io/username/systech-aidd-test/bot:latest
docker pull ghcr.io/username/systech-aidd-test/api:latest
docker pull ghcr.io/username/systech-aidd-test/frontend:latest

# Конкретная версия (по commit SHA)
docker pull ghcr.io/username/systech-aidd-test/bot:abc1234
```

### Управление

Все команды работают с registry образами:

```powershell
# Статус
docker-compose -f docker-compose.registry.yml ps

# Логи
docker-compose -f docker-compose.registry.yml logs -f

# Остановка
docker-compose -f docker-compose.registry.yml down
```

### Переключение между режимами

```powershell
# Режим 1: Локальная сборка (разработка)
docker-compose down
docker-compose up -d

# Режим 2: Registry образы (тестирование/production)
docker-compose down
docker-compose -f docker-compose.registry.yml up -d
```

### Примечание

⚠️ **Замените `username` в `docker-compose.registry.yml`** на ваш GitHub username перед использованием.

---

## 📖 Дополнительная информация

- [DOCKER_TESTING_REPORT.md](DOCKER_TESTING_REPORT.md) - Полный отчет о тестировании
- [docker-compose.yml](docker-compose.yml) - Конфигурация для локальной сборки
- [docker-compose.registry.yml](docker-compose.registry.yml) - Конфигурация для registry образов
- [devops/README.md](devops/README.md) - DevOps документация
- [devops/doc/github-actions-guide.md](devops/doc/github-actions-guide.md) - CI/CD с GitHub Actions

---

**Готово!** Теперь все три сервиса работают в Docker контейнерах 🎉
