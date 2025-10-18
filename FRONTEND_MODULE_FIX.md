# Исправление ошибки "Module not found" во фронтенде

## Проблема

При развертывании фронтенда на production сервере возникла ошибка:
```
Module not found: Can't resolve '@/lib/api'
Module not found: Can't resolve '@/lib/utils'
Module not found: Can't resolve '@/lib/chat-store'
```

## Причина

1. **Неправильный Dockerfile**: Старый Dockerfile копировал файлы неправильно и использовал dev-режим вместо production
2. **Отсутствие standalone output**: Next.js не был настроен для создания standalone сборки для Docker
3. **Проблемы с path aliases**: Алиасы `@/*` не резолвились правильно в production сборке

## Исправления

### 1. Обновлен `devops/Dockerfile.frontend`

Создан multi-stage Dockerfile с правильной production сборкой:
- **Stage 1 (deps)**: Устанавливает зависимости с frozen-lockfile
- **Stage 2 (builder)**: Собирает Next.js приложение (`pnpm build`)
- **Stage 3 (runner)**: Запускает production сервер с минимальным образом

### 2. Обновлен `frontend/web/next.config.ts`

Добавлены настройки для production:
```typescript
{
  output: "standalone",  // Создает автономную сборку для Docker
  poweredByHeader: false,
  compress: true,
  trailingSlash: false,
}
```

## Развертывание исправлений

### Вариант 1: Автоматическая пересборка через GitHub Actions

1. **Закоммитить изменения:**
```bash
git add devops/Dockerfile.frontend frontend/web/next.config.ts
git commit -m "fix: Исправление Dockerfile фронтенда для production сборки"
git push origin main
```

2. **Дождаться сборки образа:**
   - GitHub Actions автоматически соберет новый образ
   - Образ будет опубликован в GHCR с тегом `latest`
   - Проверить прогресс: https://github.com/vvelyus/systech-aidd-test/actions

3. **На сервере обновить образы:**
```bash
cd /root/systech-aidd-test

# Остановить контейнеры
docker-compose -f docker-compose.prod.yml down

# Скачать новые образы
docker-compose -f docker-compose.prod.yml pull

# Запустить с новыми образами
docker-compose -f docker-compose.prod.yml up -d

# Проверить логи
docker-compose -f docker-compose.prod.yml logs -f frontend
```

### Вариант 2: Локальная сборка на сервере (быстрее)

Если нужно быстро исправить без ожидания GitHub Actions:

1. **На сервере:**
```bash
cd /root/systech-aidd-test

# Убедиться, что код обновлен
git pull origin main

# Остановить контейнеры
docker-compose -f docker-compose.prod.yml down

# Использовать конфигурацию с локальной сборкой
docker-compose -f docker-compose.prod-rebuild.yml up -d --build frontend

# Проверить логи сборки
docker-compose -f docker-compose.prod-rebuild.yml logs -f frontend
```

2. **После успешной сборки:**
```bash
# Проверить что frontend работает
curl http://localhost:3001

# Проверить что нет ошибок модулей в браузере
# Открыть: http://89.223.67.136:3001/dashboard
```

## Проверка исправления

### 1. Проверить статус контейнера:
```bash
docker ps | grep frontend
docker logs systech-aidd-frontend-prod
```

### 2. Проверить health check:
```bash
docker inspect systech-aidd-frontend-prod | grep -A 10 Health
```

### 3. Открыть в браузере:
- Главная страница: http://89.223.67.136:3001
- Dashboard: http://89.223.67.136:3001/dashboard
- Чат: http://89.223.67.136:3001/chat

### 4. Проверить в консоли браузера (F12):
- ❌ Не должно быть ошибок "Module not found"
- ❌ Не должно быть ошибок "Can't resolve '@/lib/...'"
- ✅ Должна загрузиться страница dashboard
- ✅ Должны работать все компоненты

## Технические детали

### Что изменилось в Dockerfile:

**Было (dev-режим):**
```dockerfile
COPY package.json ./
RUN pnpm install
COPY . .
CMD ["pnpm", "dev"]
```

**Стало (production):**
```dockerfile
# Stage 1: Install deps
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

# Stage 2: Build
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN pnpm build

# Stage 3: Run
COPY --from=builder /app/.next/standalone ./
CMD ["node", "server.js"]
```

### Преимущества новой сборки:

1. ✅ **Правильная production сборка**: Next.js оптимизирует код
2. ✅ **Standalone output**: Все зависимости включены в образ
3. ✅ **Multi-stage build**: Меньший размер финального образа
4. ✅ **Воспроизводимость**: frozen-lockfile гарантирует одинаковые версии
5. ✅ **Безопасность**: Запуск от непривилегированного пользователя

## Устранение проблем

### Если сборка не удалась:

```bash
# Посмотреть логи сборки
docker-compose -f docker-compose.prod-rebuild.yml logs frontend

# Очистить кэш Docker и пересобрать
docker-compose -f docker-compose.prod-rebuild.yml build --no-cache frontend
docker-compose -f docker-compose.prod-rebuild.yml up -d frontend
```

### Если ошибки модулей остались:

1. Проверить, что образ собран с новым Dockerfile:
```bash
docker image inspect systech-aidd-frontend-prod | grep Created
```

2. Проверить, что используется правильный образ:
```bash
docker-compose -f docker-compose.prod.yml config | grep image
```

3. Пересобрать с нуля:
```bash
docker-compose -f docker-compose.prod-rebuild.yml down
docker system prune -f
docker-compose -f docker-compose.prod-rebuild.yml build --no-cache
docker-compose -f docker-compose.prod-rebuild.yml up -d
```

## Следующие шаги

После успешного исправления:

1. ✅ Проверить работу всех страниц фронтенда
2. ✅ Проверить работу dashboard и статистики
3. ✅ Проверить работу чата
4. ✅ Создать новый образ через GitHub Actions для production
5. ✅ Обновить документацию развертывания

## Время развертывания

- **Вариант 1 (GitHub Actions)**: ~5-10 минут (сборка) + 2 минуты (развертывание)
- **Вариант 2 (Локальная сборка)**: ~3-5 минут (сборка + развертывание)

Рекомендуется использовать **Вариант 2** для немедленного исправления, затем **Вариант 1** для production образа.
