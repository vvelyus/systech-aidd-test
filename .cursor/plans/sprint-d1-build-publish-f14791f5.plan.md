<!-- f14791f5-b87f-46e3-887d-5cef3bc392a4 e1ef804d-d61d-4aa5-9975-02e4cb4e570d -->
# Sprint D1 - Build & Publish

## Цель

Автоматическая сборка и публикация Docker образов (bot, api, frontend) в GitHub Container Registry при push в main с возможностью ручного запуска.

## Контекст

- **Sprint D0 завершен**: Dockerfile для всех сервисов готовы в `devops/`
- **Текущая сборка**: Локально через `docker-compose build`
- **Следующие спринты**: D2 (ручной deploy), D3 (авто deploy) будут использовать эти образы

## Принятые решения

- **Репозиторий**: `systech-aidd-test`
- **Trigger**: `workflow_dispatch` (ручной) + `push` в `main`
- **Теги**: `latest` + `SHA` (первые 7 символов)
- **Ветки**: только `main` (MVP)
- **Registry**: GitHub Container Registry (ghcr.io)
- **Доступ**: Public (без авторизации для pull)

---

## Задачи

### 1. Документация по GitHub Actions

**Файл**: `devops/doc/github-actions-guide.md`

Создать краткое руководство:

- Что такое GitHub Actions и workflow
- Основные концепции: jobs, steps, actions
- Matrix strategy для параллельной сборки
- Работа с secrets и permissions
- Публикация образов в GHCR
- Настройка public доступа к образам
- Примеры команд для работы с образами

### 2. Подготовка тестовой ветки

**Ветка**: `sprint-d1-ci`

- Создать ветку от текущей `day6-devops-basic`
- Использовать для тестирования workflow
- После успешной проверки - merge в main

### 3. GitHub Actions Workflow

**Файл**: `.github/workflows/build.yml`

Создать workflow с:

**Triggers:**

```yaml
on:
  push:
    branches: [main]
  workflow_dispatch:
```

**Matrix strategy** для 3 сервисов:

```yaml
strategy:
  matrix:
    service: [bot, api, frontend]
```

**Основные шаги:**

- Checkout кода
- Setup Docker Buildx
- Login to GHCR (используя `secrets.GITHUB_TOKEN`)
- Build and push с использованием:
  - Cache для ускорения сборки
  - Теги: `latest` и `${{ github.sha }}` (первые 7 символов)
  - Правильный context для каждого сервиса

**Особенности для сервисов:**

- **bot/api**: context = `.`, dockerfile = `devops/Dockerfile.{service}`
- **frontend**: context = `frontend/web`, dockerfile = `../../devops/Dockerfile.frontend`

### 4. Настройка публичного доступа

**Действия в GitHub UI:**

- После первой сборки образы будут приватными
- Настроить public access для каждого package
- Путь: Repository → Packages → Package settings → Change visibility → Public

**Документировать** в гайде команды для проверки:

```bash
# Без авторизации должно работать
docker pull ghcr.io/username/systech-aidd-test/bot:latest
```

### 5. Docker Compose для Registry образов

**Файл**: `docker-compose.registry.yml`

Создать альтернативную версию с использованием образов из registry:

```yaml
services:
  bot:
    image: ghcr.io/username/systech-aidd-test/bot:latest
    # остальная конфигурация идентична docker-compose.yml
```

**Преимущества:**

- Быстрый запуск без сборки
- Тестирование CI образов локально
- Готовность к D2 (deploy на сервер)

**Использование:**

```bash
# Локальная сборка (как сейчас)
docker-compose up -d

# Образы из registry
docker-compose -f docker-compose.registry.yml up -d
```

### 6. Обновление существующего docker-compose.yml

**Файл**: `docker-compose.yml`

Добавить комментарии для понимания двух режимов:

```yaml
# Режим 1 (по умолчанию): Локальная сборка
# docker-compose up -d

# Режим 2: Использование образов из registry
# docker-compose -f docker-compose.registry.yml up -d
```

### 7. Тестирование

**Последовательность:**

1. **Локальная проверка workflow синтаксиса**

   - Установить `act` (опционально) или проверить в GitHub UI

2. **Push в тестовую ветку и запуск workflow**

   - Push в `sprint-d1-ci`
   - Ручной запуск через UI: Actions → Build and Publish → Run workflow

3. **Проверка сборки образов**

   - Проверить успешность jobs
   - Проверить наличие образов в Packages

4. **Настройка public доступа**

   - Сделать образы публичными

5. **Тестирование pull без авторизации**
   ```bash
   docker pull ghcr.io/username/systech-aidd-test/bot:latest
   docker pull ghcr.io/username/systech-aidd-test/api:latest
   docker pull ghcr.io/username/systech-aidd-test/frontend:latest
   ```

6. **Запуск через docker-compose.registry.yml**
   ```bash
   docker-compose -f docker-compose.registry.yml up -d
   docker-compose -f docker-compose.registry.yml ps
   docker-compose -f docker-compose.registry.yml logs
   ```

7. **Проверка работоспособности**

   - Bot работает в Telegram
   - API доступен на http://localhost:8000/docs
   - Frontend на http://localhost:3000

### 8. Документация

**Обновить файлы:**

**`README.md`:**

- Добавить badge статуса сборки:
  ```markdown
  ![Build Status](https://github.com/username/systech-aidd-test/workflows/Build%20and%20Publish/badge.svg)
  ```

- Секция "Docker Images":
  - Ссылки на packages
  - Доступные теги
  - Команды pull

**`devops/README.md`:**

- Обновить статус Sprint D1: ✅ Completed
- Добавить ссылку на план

**`devops/doc/reports/d1-summary.md`:**

Создать отчет о выполнении:

- Что сделано
- Результаты тестирования
- Примеры использования
- Готовность к D2

**`DOCKER_QUICK_START.md`:**

- Добавить секцию "Использование готовых образов"
- Команды для работы с registry образами

---

## Критерии готовности (Definition of Done)

✅ Workflow `.github/workflows/build.yml` создан и работает

✅ Сборка запускается автоматически при push в main

✅ Сборка запускается вручную через workflow_dispatch

✅ Matrix strategy собирает 3 образа параллельно

✅ Образы публикуются в GHCR с тегами latest и SHA

✅ Образы доступны публично (public access)

✅ Pull образов работает без авторизации

✅ `docker-compose.registry.yml` создан и протестирован

✅ Локальный запуск через registry образы работает

✅ Все сервисы работают корректно (bot, api, frontend)

✅ README обновлен с badge и инструкциями

✅ Документация по GitHub Actions создана

✅ Отчет о спринте создан

---

## Что НЕ делаем (за рамками MVP)

❌ Lint checks в workflow (добавим в будущем)

❌ Тесты в CI (добавим в будущем)

❌ Security scanning (добавим в будущем)

❌ Multi-platform builds (amd64/arm64)

❌ Automatic versioning (semver)

❌ Deploy в разные environments

---

## Готовность к следующим спринтам

После завершения D1:

**Sprint D2 (Ручной Deploy):**

- ✅ Образы доступны в registry
- ✅ `docker-compose.registry.yml` готов для копирования на сервер
- ✅ Команды для pull образов задокументированы

**Sprint D3 (Auto Deploy):**

- ✅ CI/CD pipeline настроен
- ✅ Образы тегируются автоматически
- ✅ Workflow можно расширить для deployment

---

## Файлы для создания/изменения

**Создать:**

- `.github/workflows/build.yml`
- `docker-compose.registry.yml`
- `devops/doc/github-actions-guide.md`
- `devops/doc/reports/d1-summary.md`

**Изменить:**

- `README.md`
- `devops/README.md`
- `DOCKER_QUICK_START.md`
- `docker-compose.yml` (добавить комментарии)

**Ветки:**

- Создать: `sprint-d1-ci` (для тестирования)
- Merge в: `main` (после проверки)

### To-dos

- [ ] Создать документацию по GitHub Actions (devops/doc/github-actions-guide.md)
- [ ] Создать GitHub Actions workflow (.github/workflows/build.yml) с matrix strategy
- [ ] Создать docker-compose.registry.yml для использования образов из GHCR
- [ ] Протестировать workflow: запуск, сборка образов, публикация в GHCR
- [ ] Настроить public доступ к образам в GitHub Packages
- [ ] Протестировать pull образов без авторизации и запуск через docker-compose.registry.yml
- [ ] Обновить документацию: README.md (badge), devops/README.md, DOCKER_QUICK_START.md
- [ ] Создать отчет о завершении спринта (devops/doc/reports/d1-summary.md)