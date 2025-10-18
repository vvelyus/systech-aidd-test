# Frontend Fix Instructions

## Проблема
Frontend на production сервере показывал ошибку: `Module not found: Can't resolve '@/lib/api'`

## Решение
Образ был пересобран локально с правильным контекстом.

---

## Шаги для загрузки исправленного образа

### 1. Логин в GitHub Container Registry

Вам нужен **Personal Access Token** с правами `write:packages`.

**Создание токена:**
1. Откройте https://github.com/settings/tokens
2. Generate new token (classic)
3. Выберите scope: `write:packages` и `read:packages`
4. Скопируйте токен

**Логин в GHCR:**
```powershell
# Замените YOUR_TOKEN на ваш токен
docker login ghcr.io -u vvelyus
# Пароль: вставьте ваш Personal Access Token
```

### 2. Загрузка образа в GHCR

```powershell
docker push ghcr.io/vvelyus/systech-aidd-test/frontend:latest
```

**Время загрузки:** ~2-5 минут

### 3. Обновление на production сервере

Подключитесь к серверу и обновите Frontend:

```bash
# Подключение
ssh -i C:\Users\v.velyus\.ssh\systech-key.pem systech@89.223.67.136

# Переход в рабочую директорию
cd /opt/systech/vvelyus

# Загрузка нового образа
docker compose -f docker-compose.prod.yml pull frontend

# Перезапуск Frontend
docker compose -f docker-compose.prod.yml up -d frontend

# Проверка логов
docker logs systech-aidd-frontend-prod -f
```

Через 30 секунд Frontend должен запуститься без ошибок.

### 4. Проверка

**С локальной машины:**
```powershell
# Открыть в браузере
Start-Process "http://89.223.67.136:3001/dashboard"
```

Dashboard должен загрузиться и показать статистику!

---

## Альтернативное решение (если нет доступа к GHCR)

Можно пересобрать образ прямо на сервере, но для этого нужны исходники.

**На сервере:**
```bash
# Склонировать репозиторий
git clone https://github.com/vvelyus/systech-aidd-test.git
cd systech-aidd-test

# Собрать образ
docker build -t ghcr.io/vvelyus/systech-aidd-test/frontend:latest \
  -f devops/Dockerfile.frontend frontend/web

# Перезапустить
docker compose -f docker-compose.prod.yml up -d frontend
```

---

## Статус

- [x] Проблема диагностирована
- [x] Образ пересобран локально
- [x] Frontend протестирован (работает ✅)
- [ ] Образ загружен в GHCR
- [ ] Production обновлен

---

**Следующий шаг:** Выполните пункт 1 (логин в GHCR) и покажите результат
