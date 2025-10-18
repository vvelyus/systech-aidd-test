# Руководство по ручному развертыванию на сервере

> **Sprint D2**: Пошаговая инструкция для развертывания SysTech AI Assistant на production сервере

## Обзор

Это руководство описывает процесс ручного развертывания приложения на удаленном сервере с использованием готовых Docker образов из GitHub Container Registry (GHCR).

**Целевой сервер:**
- IP: `89.223.67.136`
- Пользователь: `systech`
- Рабочая директория: `/opt/systech/vvelyus`
- Порты: `3001` (Frontend), `8001` (API)

**Время выполнения:** ~15-20 минут

---

## Предварительные требования

### На локальной машине

- SSH клиент (OpenSSH, PuTTY или аналог)
- SSH ключ для доступа к серверу (файл `.pem` или `.key`)
- Файлы проекта:
  - `docker-compose.prod.yml`
  - `env.production.example`
  - `prompts/system_prompt.txt`

### На сервере

- ✅ Docker 20.10+ (уже установлен)
- ✅ Docker Compose 2.0+ (уже установлен)
- ✅ SSH доступ настроен (уже настроен)
- Открытые порты: 8001, 3001

---

## Этап 1: Подготовка (локально)

### 1.1. Проверка доступа к серверу

Проверьте SSH подключение к серверу:

```bash
# Замените /path/to/key.pem на путь к вашему SSH ключу
ssh -i /path/to/key.pem systech@89.223.67.136

# Если подключение успешно, выйдите:
exit
```

**Возможные проблемы:**
- "Permission denied" - проверьте права на ключ: `chmod 600 /path/to/key.pem`
- "Connection refused" - проверьте IP адрес и доступность сервера
- "Host key verification failed" - добавьте сервер в known_hosts

### 1.2. Подготовка .env файла

Создайте файл `.env` с реальными учетными данными:

```bash
# Скопируйте шаблон
cp env.production.example .env

# Отредактируйте файл в любом текстовом редакторе
nano .env  # или vim, code, notepad++
```

**Обязательные параметры для заполнения:**

```bash
TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather
OPENROUTER_API_KEY=ваш_ключ_от_OpenRouter
```

**Где получить токены:**
- Telegram Bot Token: https://t.me/BotFather
- OpenRouter API Key: https://openrouter.ai/keys

### 1.3. Проверка файлов

Убедитесь, что у вас есть все необходимые файлы:

```bash
# Проверка наличия файлов
ls -lh docker-compose.prod.yml
ls -lh .env
ls -lh prompts/system_prompt.txt

# Проверка содержимого .env (без вывода секретов)
grep -E "^[A-Z_]+=" .env | head -5
```

Должны быть:
- ✅ `docker-compose.prod.yml` - конфигурация Docker Compose
- ✅ `.env` - переменные окружения с реальными токенами
- ✅ `prompts/system_prompt.txt` - системный промпт для бота

---

## Этап 2: Подключение к серверу

### 2.1. SSH подключение

Подключитесь к серверу с использованием SSH ключа:

```bash
ssh -i /path/to/key.pem systech@89.223.67.136
```

**После подключения вы увидите приглашение командной строки:**
```
systech@server:~$
```

### 2.2. Проверка окружения

Проверьте версии Docker и Docker Compose:

```bash
# Проверка Docker
docker --version
# Ожидается: Docker version 20.10.x или выше

# Проверка Docker Compose
docker-compose --version
# Ожидается: Docker Compose version 2.x.x или выше

# Проверка прав пользователя
docker ps
# Не должно быть ошибок "permission denied"
```

**Если Docker не доступен:** обратитесь к администратору сервера.

### 2.3. Создание рабочей директории

Создайте директорию для проекта:

```bash
# Создание директории с правами для текущего пользователя
sudo mkdir -p /opt/systech/vvelyus
sudo chown -R $USER:$USER /opt/systech/vvelyus

# Переход в рабочую директорию
cd /opt/systech/vvelyus

# Проверка текущей директории
pwd
# Должно вывести: /opt/systech/vvelyus
```

---

## Этап 3: Копирование файлов на сервер

### 3.1. Копирование через SCP

**Откройте НОВЫЙ терминал на локальной машине** (не закрывая SSH сессию).

Скопируйте файлы на сервер:

```bash
# Убедитесь, что вы в директории проекта локально
cd /путь/к/проекту/systech-aidd-test

# Копирование docker-compose.prod.yml
scp -i /path/to/key.pem docker-compose.prod.yml systech@89.223.67.136:/opt/systech/vvelyus/

# Копирование .env файла
scp -i /path/to/key.pem .env systech@89.223.67.136:/opt/systech/vvelyus/

# Копирование системного промпта
scp -i /path/to/key.pem prompts/system_prompt.txt systech@89.223.67.136:/opt/systech/vvelyus/
```

**Альтернатива для Windows (PowerShell):**
```powershell
# Используйте полные пути
scp -i C:\path\to\key.pem docker-compose.prod.yml systech@89.223.67.136:/opt/systech/vvelyus/
scp -i C:\path\to\key.pem .env systech@89.223.67.136:/opt/systech/vvelyus/
scp -i C:\path\to\key.pem prompts\system_prompt.txt systech@89.223.67.136:/opt/systech/vvelyus/
```

### 3.2. Проверка файлов на сервере

Вернитесь в SSH терминал и проверьте файлы:

```bash
# Проверка наличия файлов
ls -lh /opt/systech/vvelyus/

# Должно быть:
# -rw-r--r-- docker-compose.prod.yml
# -rw-r--r-- .env
# -rw-r--r-- system_prompt.txt

# Проверка содержимого docker-compose
head -10 docker-compose.prod.yml

# Проверка .env (без вывода секретов)
grep -c "TELEGRAM_BOT_TOKEN" .env
# Должно вывести: 1
```

---

## Этап 4: Подготовка структуры директорий

### 4.1. Создание директорий

Создайте необходимые директории для volumes:

```bash
# В директории /opt/systech/vvelyus
cd /opt/systech/vvelyus

# Создание директорий
mkdir -p data logs prompts

# Перемещение system_prompt.txt в prompts
mv system_prompt.txt prompts/

# Проверка структуры
tree -L 2
# Или без tree:
ls -la
```

**Должна получиться структура:**
```
/opt/systech/vvelyus/
├── data/                  # SQLite база данных
├── logs/                  # Логи приложений
├── prompts/               # Системные промпты
│   └── system_prompt.txt
├── docker-compose.prod.yml
└── .env
```

### 4.2. Установка прав доступа

```bash
# Установка прав на директории
chmod 755 data logs prompts
chmod 644 prompts/system_prompt.txt
chmod 600 .env  # Защита секретов

# Проверка прав
ls -la
```

---

## Этап 5: Загрузка Docker образов

### 5.1. Pull образов из GHCR

Загрузите образы из GitHub Container Registry:

```bash
# Образы публичные, авторизация не требуется
docker pull ghcr.io/vvelyus/systech-aidd-test/bot:latest
docker pull ghcr.io/vvelyus/systech-aidd-test/api:latest
docker pull ghcr.io/vvelyus/systech-aidd-test/frontend:latest
```

**Время выполнения:** 2-5 минут (зависит от скорости интернета)

### 5.2. Проверка образов

```bash
# Список загруженных образов
docker images | grep systech-aidd-test

# Должно вывести 3 образа:
# ghcr.io/vvelyus/systech-aidd-test/bot       latest   ...
# ghcr.io/vvelyus/systech-aidd-test/api       latest   ...
# ghcr.io/vvelyus/systech-aidd-test/frontend  latest   ...
```

---

## Этап 6: Запуск сервисов

### 6.1. Запуск Docker Compose

```bash
# В директории с docker-compose.prod.yml
cd /opt/systech/vvelyus

# Запуск всех сервисов в фоновом режиме
docker-compose -f docker-compose.prod.yml up -d

# Ожидается вывод:
# Creating network "vvelyus_systech-network" ...
# Creating systech-aidd-bot-prod ... done
# Creating systech-aidd-api-prod ... done
# Creating systech-aidd-frontend-prod ... done
```

**Время запуска:** ~30-60 секунд

### 6.2. Проверка статуса контейнеров

```bash
# Проверка запущенных контейнеров
docker-compose -f docker-compose.prod.yml ps

# Все сервисы должны быть в статусе "Up" или "Up (healthy)"
# NAME                         STATE    PORTS
# systech-aidd-api-prod        Up       0.0.0.0:8001->8000/tcp
# systech-aidd-bot-prod        Up       
# systech-aidd-frontend-prod   Up       0.0.0.0:3001->3000/tcp

# Альтернативная проверка
docker ps
```

### 6.3. Просмотр логов

```bash
# Логи всех сервисов
docker-compose -f docker-compose.prod.yml logs

# Логи конкретного сервиса
docker-compose -f docker-compose.prod.yml logs api
docker-compose -f docker-compose.prod.yml logs bot
docker-compose -f docker-compose.prod.yml logs frontend

# Следить за логами в реальном времени
docker-compose -f docker-compose.prod.yml logs -f

# Выход: Ctrl+C
```

---

## Этап 7: Миграции базы данных

### 7.1. Запуск миграций

Выполните миграции через API контейнер:

```bash
# Запуск миграций Alembic
docker exec systech-aidd-api-prod alembic upgrade head

# Ожидается вывод:
# INFO  [alembic.runtime.migration] Running upgrade ...
```

**Если команда alembic не найдена**, попробуйте альтернативный вариант:

```bash
# Через Python модуль
docker exec systech-aidd-api-prod python -m alembic upgrade head
```

### 7.2. Проверка таблиц в БД

```bash
# Проверка наличия базы данных
ls -lh data/messages.db

# Проверка структуры БД через SQLite
docker exec systech-aidd-api-prod python -c "
import sqlite3
conn = sqlite3.connect('/app/data/messages.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')
print('Tables:', [row[0] for row in cursor.fetchall()])
conn.close()
"

# Должно вывести список таблиц:
# Tables: ['users', 'chat_messages', 'alembic_version', ...]
```

### 7.3. Проверка логов миграций

```bash
# Проверка логов API на наличие ошибок
docker-compose -f docker-compose.prod.yml logs api | grep -i error
docker-compose -f docker-compose.prod.yml logs api | grep -i migration

# Если нет вывода - миграции прошли успешно
```

---

## Этап 8: Проверка работоспособности

### 8.1. Проверка здоровья сервисов

```bash
# Health check для API
curl http://localhost:8001/health

# Ожидается:
# {"status":"healthy"}

# Health check для Frontend
curl http://localhost:3001

# Ожидается: HTML страница
```

### 8.2. Проверка логов каждого сервиса

```bash
# API - последние 20 строк
docker-compose -f docker-compose.prod.yml logs --tail=20 api

# Bot - последние 20 строк
docker-compose -f docker-compose.prod.yml logs --tail=20 bot

# Frontend - последние 20 строк
docker-compose -f docker-compose.prod.yml logs --tail=20 frontend

# Проверка на наличие ошибок
docker-compose -f docker-compose.prod.yml logs | grep -i "error\|critical\|exception"
```

### 8.3. Проверка доступа извне

**На локальной машине** проверьте доступность через публичный IP:

```bash
# API
curl http://89.223.67.136:8001/health

# Frontend
curl http://89.223.67.136:3001

# Или откройте в браузере:
# http://89.223.67.136:8001/health
# http://89.223.67.136:3001
```

**Ожидается:**
- API возвращает JSON с health статусом
- Frontend возвращает HTML страницу

### 8.4. Тест работы Telegram бота

1. Откройте Telegram
2. Найдите вашего бота (имя из BotFather)
3. Отправьте команду `/start`
4. Отправьте тестовое сообщение "Привет!"

**На сервере** проверьте логи бота:

```bash
docker-compose -f docker-compose.prod.yml logs -f bot

# Должны увидеть:
# - Получение сообщения от пользователя
# - Запрос к OpenRouter API
# - Отправку ответа пользователю
```

---

## Этап 9: Финальная проверка

### 9.1. Чек-лист работоспособности

- [ ] Все контейнеры запущены (docker ps показывает 3 контейнера)
- [ ] API отвечает на http://89.223.67.136:8001/health
- [ ] Frontend доступен на http://89.223.67.136:3001
- [ ] База данных создана (data/messages.db существует)
- [ ] Миграции выполнены (таблицы созданы)
- [ ] Bot получает и отвечает на сообщения в Telegram
- [ ] Логи не содержат критических ошибок
- [ ] Healthcheck'и проходят успешно

### 9.2. Мониторинг и логи

```bash
# Мониторинг в реальном времени
watch -n 2 'docker-compose -f docker-compose.prod.yml ps'

# Проверка использования ресурсов
docker stats

# Просмотр логов приложения (на хосте)
tail -f logs/bot.log

# Размер базы данных
du -h data/messages.db
```

---

## Управление сервисами

### Остановка

```bash
# Остановка всех сервисов
docker-compose -f docker-compose.prod.yml stop

# Остановка конкретного сервиса
docker-compose -f docker-compose.prod.yml stop bot
```

### Перезапуск

```bash
# Перезапуск всех сервисов
docker-compose -f docker-compose.prod.yml restart

# Перезапуск конкретного сервиса
docker-compose -f docker-compose.prod.yml restart api
```

### Остановка и удаление

```bash
# Остановка и удаление контейнеров (данные сохраняются)
docker-compose -f docker-compose.prod.yml down

# Полное удаление (включая volumes)
docker-compose -f docker-compose.prod.yml down -v
```

### Обновление образов

```bash
# Загрузка новых версий образов
docker-compose -f docker-compose.prod.yml pull

# Пересоздание контейнеров с новыми образами
docker-compose -f docker-compose.prod.yml up -d
```

---

## Troubleshooting

### Проблема: Контейнер не запускается

**Симптомы:**
```bash
docker-compose ps
# Статус: Restarting или Exit 1
```

**Решение:**
```bash
# 1. Проверьте логи
docker-compose -f docker-compose.prod.yml logs <service_name>

# 2. Проверьте .env файл
cat .env | grep -E "TOKEN|KEY"

# 3. Проверьте наличие volumes
ls -la data/ logs/ prompts/

# 4. Перезапустите с чистого листа
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d
```

### Проблема: API не отвечает

**Симптомы:**
```bash
curl http://localhost:8001/health
# Connection refused или timeout
```

**Решение:**
```bash
# 1. Проверьте, что контейнер запущен
docker ps | grep api

# 2. Проверьте порты
docker port systech-aidd-api-prod

# 3. Проверьте логи
docker logs systech-aidd-api-prod

# 4. Проверьте базу данных
ls -lh data/messages.db

# 5. Попробуйте зайти в контейнер
docker exec -it systech-aidd-api-prod /bin/sh
curl http://localhost:8000/health
```

### Проблема: Bot не отвечает в Telegram

**Симптомы:** Бот не реагирует на сообщения

**Решение:**
```bash
# 1. Проверьте логи бота
docker logs systech-aidd-bot-prod -f

# 2. Проверьте TELEGRAM_BOT_TOKEN
docker exec systech-aidd-bot-prod env | grep TELEGRAM

# 3. Проверьте соединение с Telegram API
docker exec systech-aidd-bot-prod ping -c 3 api.telegram.org

# 4. Проверьте OPENROUTER_API_KEY
docker exec systech-aidd-bot-prod env | grep OPENROUTER
```

### Проблема: Нет места на диске

**Симптомы:**
```bash
df -h
# /dev/sda1  95%  ...
```

**Решение:**
```bash
# 1. Очистка неиспользуемых образов
docker system prune -a

# 2. Очистка логов
docker-compose -f docker-compose.prod.yml logs > /dev/null
rm -f logs/*.log

# 3. Ротация логов Docker
# Настроена в docker-compose.prod.yml (max-size: 10m, max-file: 5)

# 4. Проверка размера базы данных
du -h data/messages.db
```

### Проблема: Ошибка "permission denied"

**Симптомы:** Контейнеры не могут писать в volumes

**Решение:**
```bash
# Проверка прав
ls -la data/ logs/ prompts/

# Установка правильных прав
sudo chown -R $USER:$USER data logs prompts
chmod 755 data logs prompts
```

### Команды для диагностики

```bash
# Полная информация о контейнерах
docker-compose -f docker-compose.prod.yml ps -a

# Инспекция контейнера
docker inspect systech-aidd-api-prod

# Процессы внутри контейнера
docker top systech-aidd-api-prod

# Использование ресурсов
docker stats --no-stream

# Сетевые подключения
docker network inspect vvelyus_systech-network

# Логи Docker daemon
sudo journalctl -u docker -n 50
```

---

## Backup и восстановление

### Создание backup

```bash
# Остановка сервисов (опционально, для консистентности)
docker-compose -f docker-compose.prod.yml stop

# Backup базы данных и конфигурации
tar -czf backup-$(date +%Y%m%d-%H%M%S).tar.gz \
  data/ \
  .env \
  docker-compose.prod.yml \
  prompts/

# Запуск сервисов
docker-compose -f docker-compose.prod.yml start

# Копирование backup в безопасное место
scp backup-*.tar.gz user@backup-server:/backups/
```

### Восстановление из backup

```bash
# Остановка и удаление текущих данных
docker-compose -f docker-compose.prod.yml down

# Распаковка backup
tar -xzf backup-YYYYMMDD-HHMMSS.tar.gz

# Запуск сервисов
docker-compose -f docker-compose.prod.yml up -d
```

---

## Мониторинг и обслуживание

### Регулярные проверки

```bash
# Ежедневно: проверка статуса
docker-compose -f docker-compose.prod.yml ps

# Еженедельно: проверка логов
docker-compose -f docker-compose.prod.yml logs --tail=100 | grep -i error

# Еженедельно: проверка размера БД
du -h data/messages.db

# Ежемесячно: обновление образов
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Ежемесячно: backup
./scripts/backup.sh  # (создать скрипт по примеру выше)
```

### Полезные алиасы

Добавьте в `~/.bashrc`:

```bash
alias dc='docker-compose -f /opt/systech/vvelyus/docker-compose.prod.yml'
alias dcl='dc logs -f'
alias dcp='dc ps'
alias dcr='dc restart'
```

После:
```bash
source ~/.bashrc
dcl api  # Быстрый просмотр логов API
```

---

## Контакты и поддержка

При возникновении проблем:

1. Проверьте раздел [Troubleshooting](#troubleshooting)
2. Изучите логи: `docker-compose logs`
3. Обратитесь к [документации проекта](../README.md)
4. Создайте issue в GitHub репозитории

---

## Следующие шаги

После успешного развертывания:

- [ ] Настроить автоматический backup
- [ ] Настроить мониторинг (Prometheus + Grafana)
- [ ] Настроить алерты (при падении сервисов)
- [ ] Настроить домен и SSL сертификат (Sprint D3)
- [ ] Автоматизировать развертывание (Sprint D3)

---

**Документ обновлен:** 18 октября 2025
**Версия:** 1.0
**Sprint:** D2 - Manual Deploy

