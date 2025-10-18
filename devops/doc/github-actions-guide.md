# GitHub Actions - Руководство

## Введение

**GitHub Actions** - это платформа CI/CD (Continuous Integration/Continuous Deployment), встроенная в GitHub. Она позволяет автоматизировать процессы сборки, тестирования и развертывания прямо в репозитории.

### Основные преимущества

- ✅ **Интеграция с GitHub** - нативная поддержка, ничего не нужно настраивать отдельно
- ✅ **Бесплатно для публичных репозиториев** - неограниченные минуты
- ✅ **Free tier для приватных** - 2000 минут/месяц
- ✅ **GitHub Container Registry** - встроенный registry для Docker образов
- ✅ **Богатый Marketplace** - тысячи готовых actions

---

## Основные концепции

### Workflow (рабочий процесс)

YAML файл в `.github/workflows/` который описывает автоматизацию.

**Пример структуры:**
```yaml
name: Build and Publish          # Название workflow
on: [push, pull_request]         # Когда запускать
jobs:                            # Что делать
  build:
    runs-on: ubuntu-latest       # На чем запускать
    steps:                       # Шаги выполнения
      - uses: actions/checkout@v4
      - run: echo "Hello World"
```

### Jobs (задачи)

Набор шагов, выполняемых на одном runner (виртуальной машине).

**Особенности:**
- Выполняются параллельно (по умолчанию)
- Могут зависеть друг от друга через `needs:`
- Каждый job = отдельная VM (чистое окружение)

### Steps (шаги)

Отдельные команды или actions внутри job.

**Два типа:**
- `uses:` - использовать готовый action
- `run:` - выполнить shell команду

### Actions (действия)

Переиспользуемые компоненты. Берутся из:
- GitHub Marketplace
- Вашего репозитория
- Других публичных репозиториев

---

## Matrix Strategy - Параллельная сборка

**Matrix strategy** позволяет запускать один job с разными параметрами параллельно.

### Пример: сборка 3 сервисов

```yaml
jobs:
  build:
    strategy:
      matrix:
        service: [bot, api, frontend]  # 3 параллельных job
    steps:
      - name: Build ${{ matrix.service }}
        run: echo "Building ${{ matrix.service }}"
```

**Результат:** Создаются 3 отдельных job:
- `build (bot)`
- `build (api)`
- `build (frontend)`

Все выполняются **одновременно**, экономя время.

### Преимущества для Docker

- Быстрая сборка всех образов
- DRY принцип (один код для всех сервисов)
- Легко добавить новый сервис

---

## Secrets и Permissions

### GitHub Token

`GITHUB_TOKEN` - автоматически создается для каждого workflow.

**Использование:**
```yaml
- name: Login to GHCR
  uses: docker/login-action@v3
  with:
    registry: ghcr.io
    username: ${{ github.actor }}
    password: ${{ secrets.GITHUB_TOKEN }}
```

### Permissions

По умолчанию `GITHUB_TOKEN` имеет ограниченные права. Для записи в GHCR нужно добавить:

```yaml
permissions:
  contents: read
  packages: write
```

---

## GitHub Container Registry (GHCR)

### Что это?

**ghcr.io** - Docker registry от GitHub для хранения образов.

**Адрес образа:**
```
ghcr.io/<username>/<repository>/<image>:<tag>
```

**Пример:**
```
ghcr.io/johndoe/systech-aidd-test/bot:latest
ghcr.io/johndoe/systech-aidd-test/api:v1.0.0
```

### Преимущества

- ✅ **Бесплатно** для публичных образов
- ✅ **Интеграция** с GitHub Actions
- ✅ **Автоматическая авторизация** через GITHUB_TOKEN
- ✅ **Unlimited storage** для публичных образов
- ✅ **Package management** - связь с репозиторием

### Публикация образа

```yaml
- name: Build and push
  uses: docker/build-push-action@v5
  with:
    push: true
    tags: |
      ghcr.io/${{ github.repository }}/bot:latest
      ghcr.io/${{ github.repository }}/bot:${{ github.sha }}
```

**Переменные:**
- `github.repository` → `username/repo-name`
- `github.sha` → полный commit SHA
- `github.actor` → пользователь, запустивший workflow

---

## Настройка Public доступа

### Почему это важно?

По умолчанию образы в GHCR **приватные** - требуют авторизации для pull.

**Public образы** можно скачивать без логина:
```bash
docker pull ghcr.io/username/repo/bot:latest  # Работает сразу
```

### Как сделать образ публичным

После первой публикации образа через workflow:

**Шаг 1:** Перейти в Repository → **Packages** (правая панель)

**Шаг 2:** Выбрать package (например, `bot`)

**Шаг 3:** Package Settings → **Change visibility**

**Шаг 4:** Выбрать **Public** → Подтвердить

**Шаг 5:** Повторить для всех образов (bot, api, frontend)

### Проверка

```bash
# Должно работать БЕЗ docker login
docker pull ghcr.io/username/systech-aidd-test/bot:latest
docker pull ghcr.io/username/systech-aidd-test/api:latest
docker pull ghcr.io/username/systech-aidd-test/frontend:latest
```

---

## Triggers - Когда запускать workflow

### Push в ветку

```yaml
on:
  push:
    branches:
      - main
      - develop
```

Запускается при каждом push в указанные ветки.

### Pull Request

```yaml
on:
  pull_request:
    branches: [main]
```

Запускается при создании/обновлении PR в main.

### Manual Dispatch (ручной запуск)

```yaml
on:
  workflow_dispatch:
```

Позволяет запустить workflow вручную через UI:
1. Перейти в **Actions**
2. Выбрать workflow
3. Нажать **Run workflow**
4. Выбрать ветку
5. Запустить

### Комбинация

```yaml
on:
  push:
    branches: [main]
  workflow_dispatch:
```

- Автоматически при push в main
- Вручную для любой ветки

---

## Docker Build с Cache

### Зачем нужен кэш?

Docker layers кэшируются между сборками, что значительно ускоряет процесс:
- Первая сборка: ~5-10 минут
- Последующие: ~1-3 минуты

### Настройка кэша

```yaml
- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    cache-from: type=registry,ref=ghcr.io/${{ github.repository }}/bot:buildcache
    cache-to: type=registry,ref=ghcr.io/${{ github.repository }}/bot:buildcache,mode=max
```

**Типы кэша:**
- `type=registry` - хранится в container registry
- `type=gha` - GitHub Actions cache (быстрее, но ограничен 10GB)

---

## Тегирование образов

### Best Practices

Используйте несколько тегов для одного образа:

```yaml
tags: |
  ghcr.io/${{ github.repository }}/bot:latest
  ghcr.io/${{ github.repository }}/bot:${{ github.sha }}
```

### Типы тегов

**1. `latest`** - последняя версия
- ✅ Удобно для тестирования
- ✅ Всегда актуальная версия
- ❌ Не трейсабельно

**2. Commit SHA** - привязка к коммиту
- ✅ Точно знаем код
- ✅ Можно откатиться
- ✅ Трейсабельно
- ❌ Сложно запомнить

**3. Semantic version** (v1.0.0)
- ✅ Понятная версия
- ✅ Production ready
- ❌ Требует процесс версионирования

### Короткий SHA

```yaml
- name: Get short SHA
  id: sha
  run: echo "short=$(echo ${{ github.sha }} | cut -c1-7)" >> $GITHUB_OUTPUT

- name: Build with short SHA
  run: |
    docker build -t myimage:${{ steps.sha.outputs.short }} .
```

---

## Полный пример Workflow

```yaml
name: Build and Publish Docker Images

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  packages: write

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [bot, api, frontend]

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to GitHub Container Registry
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Get short SHA
        id: sha
        run: echo "short=$(echo ${{ github.sha }} | cut -c1-7)" >> $GITHUB_OUTPUT

      - name: Build and push ${{ matrix.service }}
        uses: docker/build-push-action@v5
        with:
          context: ${{ matrix.service == 'frontend' && './frontend/web' || '.' }}
          file: devops/Dockerfile.${{ matrix.service }}
          push: true
          tags: |
            ghcr.io/${{ github.repository }}/${{ matrix.service }}:latest
            ghcr.io/${{ github.repository }}/${{ matrix.service }}:${{ steps.sha.outputs.short }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

---

## Работа с образами из GHCR

### Pull образа (public)

```bash
# Без авторизации
docker pull ghcr.io/username/systech-aidd-test/bot:latest
```

### Pull образа (private)

```bash
# Авторизация
echo $GITHUB_TOKEN | docker login ghcr.io -u username --password-stdin

# Pull
docker pull ghcr.io/username/systech-aidd-test/bot:latest
```

### Запуск контейнера

```bash
docker run -d \
  --name my-bot \
  --env-file .env \
  ghcr.io/username/systech-aidd-test/bot:latest
```

### Docker Compose

```yaml
services:
  bot:
    image: ghcr.io/username/systech-aidd-test/bot:latest
    env_file: .env
    volumes:
      - ./data:/app/data
```

---

## Мониторинг и отладка

### Просмотр логов workflow

1. Перейти в **Actions**
2. Выбрать workflow run
3. Кликнуть на job
4. Развернуть step для просмотра логов

### Повторный запуск

Если workflow упал:
1. Открыть failed run
2. Нажать **Re-run jobs**
3. Выбрать **Re-run failed jobs** или **Re-run all jobs**

### Отладка

Добавить debug step:
```yaml
- name: Debug info
  run: |
    echo "Repository: ${{ github.repository }}"
    echo "SHA: ${{ github.sha }}"
    echo "Actor: ${{ github.actor }}"
    docker --version
    docker buildx version
```

---

## Best Practices

### ✅ DO

- Используйте конкретные версии actions (`@v4`, не `@latest`)
- Кэшируйте Docker layers для ускорения
- Используйте matrix для параллельной сборки
- Добавляйте несколько тегов к образу
- Делайте публичными open-source образы
- Минимизируйте размер образов

### ❌ DON'T

- Не храните секреты в коде (используйте GitHub Secrets)
- Не используйте `sudo` без необходимости
- Не собирайте все в одном job (разделяйте)
- Не игнорируйте failed builds

---

## Ресурсы

### Официальная документация

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)

### Marketplace

- [Docker Build-Push Action](https://github.com/marketplace/actions/build-and-push-docker-images)
- [Docker Login Action](https://github.com/marketplace/actions/docker-login)
- [Setup Buildx](https://github.com/marketplace/actions/docker-setup-buildx)

### Лимиты Free Tier

- **Публичные репозитории**: unlimited minutes
- **Приватные репозитории**: 2000 minutes/month
- **Storage**: 500 MB (packages)
- **Concurrent jobs**: 20 (public), 5 (private)

---

## Troubleshooting

### Error: permission denied

**Проблема:** Недостаточно прав для записи в GHCR.

**Решение:** Добавить permissions в workflow:
```yaml
permissions:
  packages: write
```

### Error: authentication required

**Проблема:** Не выполнен login в registry.

**Решение:** Добавить docker/login-action step.

### Cache miss

**Проблема:** Кэш не работает, сборка всегда с нуля.

**Решение:** Проверить cache-from и cache-to настройки.

### Rate limit exceeded

**Проблема:** Docker Hub rate limits для anonymous pulls.

**Решение:** Использовать Docker Hub token или GHCR для базовых образов.

---

## Следующие шаги

После настройки базового CI/CD можно добавить:

- 🧪 **Тесты** - запуск pytest в workflow
- 🔍 **Линтинг** - ruff, mypy проверки
- 🔐 **Security scanning** - Trivy, Snyk
- 🏗️ **Multi-platform builds** - amd64 + arm64
- 🚀 **Auto deployment** - автоматический деплой на сервер
- 📊 **Notifications** - Slack, Telegram уведомления
- 📈 **Metrics** - отслеживание времени сборки

---

**Готово!** Теперь вы знаете основы GitHub Actions и можете настроить CI/CD для вашего проекта.
