# Frontend Development

Этот раздел содержит документацию и ресурсы для разработки frontend части проекта SysTech AIDD.

## Структура директории

```
frontend/
├── doc/                    # Документация
│   ├── plans/             # Планы выполнения спринтов
│   │   ├── s1-mock-api-plan.md
│   │   └── s2-init-plan.md
│   ├── api-contract.md    # Контракт API
│   ├── api-examples.md    # Примеры использования API
│   ├── dashboard.jpg      # Референс дизайна дашборда
│   ├── frontend-roadmap.md # Roadmap развития frontend
│   └── frontend-vision.md  # Видение UI (будет создан)
├── web/                   # Next.js приложение
│   ├── src/               # Исходный код
│   ├── public/            # Статические файлы
│   └── README.md          # Документация frontend
└── README.md              # Этот файл
```

## Текущий статус

**✅ Спринт F1 завершен** - Mock API для дашборда статистики

### Что реализовано

- ✅ Mock API на FastAPI с endpoint `/stats`
- ✅ Pydantic модели для типизации данных
- ✅ Автогенерация OpenAPI документации
- ✅ Интерфейс StatCollector с Mock реализацией
- ✅ Comprehensive тесты (100% покрытие API кода)
- ✅ Команды в Makefile для работы с API
- ✅ Полная документация контракта и примеров

### Быстрый старт с API

```bash
# 1. Убедитесь, что зависимости установлены
make install

# 2. Запустите API сервер
make api-run
# API будет доступен на http://localhost:8000

# 3. Откройте документацию в браузере
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc

# 4. Протестируйте API (в другом терминале)
make api-test
```

### Примеры запросов

```bash
# Health check
curl http://localhost:8000/

# Получить статистику за неделю
curl http://localhost:8000/stats?period=week

# Получить статистику за день
curl http://localhost:8000/stats?period=day

# Получить статистику за месяц
curl http://localhost:8000/stats?period=month
```

### Структура ответа API

API возвращает JSON с четырьмя основными секциями:

1. **summary** - Общая статистика (4 карточки для дашборда)
2. **activity_timeline** - Временной ряд активности (для графика)
3. **top_users** - Топ 5 активных пользователей
4. **recent_dialogs** - 10 последних диалогов

Подробнее см. [API Contract](doc/api-contract.md)

## Документация

- 📋 [Frontend Roadmap](doc/frontend-roadmap.md) - План развития
- 📜 [API Contract](doc/api-contract.md) - Описание контракта API
- 💡 [API Examples](doc/api-examples.md) - Примеры использования на разных языках
- 📝 [Plan F1](doc/plans/s1-mock-api-plan.md) - Детальный план спринта F1

## Web Приложение

**Директория**: `frontend/web/`

Next.js приложение с дашбордом статистики и ИИ-чатом.

### Быстрый старт

```bash
# Установить зависимости
make frontend-install

# Запустить dev server
make frontend-dev
# Frontend доступен на http://localhost:3000
```

Подробная документация: [frontend/web/README.md](web/README.md)

## Следующие шаги

**Спринт F3** - Реализация dashboard

Задачи:
- Разработка компонентов визуализации данных
- Реализация графиков и диаграмм
- Адаптивная верстка
- Оптимизация производительности

## Полезные команды

```bash
# API Server
make api-run          # Запустить API сервер
make api-test         # Тестировать API endpoints
make api-docs         # Показать URL документации

# Frontend
make frontend-install     # Установить зависимости frontend
make frontend-dev         # Запустить dev server (port 3000)
make frontend-build       # Production build
make frontend-lint        # Запустить ESLint
make frontend-type-check  # Проверка TypeScript

# Backend Development
make install          # Установить зависимости backend
make test             # Запустить все тесты
make ci               # Полная CI проверка
```

## Технологии (Backend API)

- **FastAPI** - Web framework
- **Pydantic** - Data validation
- **Uvicorn** - ASGI server
- **OpenAPI** - API documentation

## Дополнительная информация

- Основной проект: [README.md](../README.md)
- Общий roadmap: [docs/roadmap.md](../docs/roadmap.md)
- Архитектура: [docs/guides/ARCHITECTURE.md](../docs/guides/ARCHITECTURE.md)
