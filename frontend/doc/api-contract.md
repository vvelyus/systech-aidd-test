# Stats API Contract

## Базовая информация

- **Базовый URL:** `http://localhost:8000`
- **Версия:** 1.0.0
- **Формат:** JSON
- **Документация:**
  - Swagger UI: http://localhost:8000/docs
  - ReDoc: http://localhost:8000/redoc
  - OpenAPI Schema: http://localhost:8000/openapi.json

## Endpoints

### Health Check

**GET /**

Проверка доступности API.

**Ответ:**
```json
{
  "status": "ok",
  "message": "Stats API is running"
}
```

---

### Получение статистики

**GET /stats**

Получить статистику диалогов за указанный период.

**Параметры запроса:**

| Параметр | Тип | Обязательный | По умолчанию | Описание |
|----------|-----|--------------|--------------|----------|
| `period` | string (enum) | Нет | `week` | Период для статистики: `day`, `week`, `month` |

**Примеры запросов:**

```bash
# Статистика за неделю (по умолчанию)
curl http://localhost:8000/stats

# Статистика за день
curl http://localhost:8000/stats?period=day

# Статистика за месяц
curl http://localhost:8000/stats?period=month
```

**Структура ответа:**

```json
{
  "summary": {
    "total_messages": 1250,
    "total_messages_change": 12.5,
    "active_users": 45,
    "active_users_change": -5.2,
    "avg_dialog_length": 8.3,
    "avg_dialog_length_change": 3.1,
    "messages_per_day": 125.0,
    "messages_per_day_change": 15.8
  },
  "activity_timeline": [
    {
      "date": "2025-10-10",
      "user_messages": 65,
      "bot_messages": 58,
      "total": 123
    },
    {
      "date": "2025-10-11",
      "user_messages": 72,
      "bot_messages": 68,
      "total": 140
    }
  ],
  "top_users": [
    {
      "user_id": 100001,
      "username": "user1",
      "first_name": "Иван",
      "message_count": 150,
      "last_activity": "2025-10-17T10:30:00"
    },
    {
      "user_id": 100002,
      "username": null,
      "first_name": "Петр",
      "message_count": 142,
      "last_activity": "2025-10-17T09:15:00"
    }
  ],
  "recent_dialogs": [
    {
      "user_id": 200001,
      "username": "user1",
      "first_name": "Петр",
      "last_message": "Привет! Как дела?",
      "message_count": 12,
      "last_activity": "2025-10-17T10:30:00"
    },
    {
      "user_id": 200002,
      "username": null,
      "first_name": "Сергей",
      "last_message": "Спасибо за помощь",
      "message_count": 8,
      "last_activity": "2025-10-17T10:15:00"
    }
  ]
}
```

## Модели данных

### SummaryStats

Общая статистика для карточек дашборда.

| Поле | Тип | Описание |
|------|-----|----------|
| `total_messages` | integer | Всего сообщений |
| `total_messages_change` | float | Изменение в % относительно предыдущего периода |
| `active_users` | integer | Активные пользователи |
| `active_users_change` | float | Изменение в % |
| `avg_dialog_length` | float | Средняя длина диалога (сообщений) |
| `avg_dialog_length_change` | float | Изменение в % |
| `messages_per_day` | float | Среднее сообщений в день |
| `messages_per_day_change` | float | Изменение в % |

### TimelinePoint

Точка на временной шкале активности.

| Поле | Тип | Описание |
|------|-----|----------|
| `date` | string | Дата в формате ISO (YYYY-MM-DD) |
| `user_messages` | integer | Количество сообщений от пользователей |
| `bot_messages` | integer | Количество сообщений от бота |
| `total` | integer | Общее количество сообщений |

### UserActivity

Информация об активности пользователя.

| Поле | Тип | Описание |
|------|-----|----------|
| `user_id` | integer | ID пользователя |
| `username` | string\|null | Username пользователя (может отсутствовать) |
| `first_name` | string\|null | Имя пользователя |
| `message_count` | integer | Количество сообщений |
| `last_activity` | string | Последняя активность (ISO datetime) |

### DialogPreview

Превью диалога.

| Поле | Тип | Описание |
|------|-----|----------|
| `user_id` | integer | ID пользователя |
| `username` | string\|null | Username пользователя (может отсутствовать) |
| `first_name` | string\|null | Имя пользователя |
| `last_message` | string | Превью последнего сообщения |
| `message_count` | integer | Количество сообщений в диалоге |
| `last_activity` | string | Последняя активность (ISO datetime) |

## Коды ответов

| Код | Описание |
|-----|----------|
| 200 | Успешный запрос |
| 422 | Ошибка валидации параметров |
| 500 | Внутренняя ошибка сервера |

## CORS

API настроен для приема запросов с любых доменов (в production следует ограничить).

## Особенности текущей версии

- **Mock данные:** Текущая версия использует MockStatCollector, генерирующий случайные тестовые данные
- **Независимость:** API работает независимо от основного Telegram бота
- **Автогенерация документации:** OpenAPI схема генерируется автоматически из Pydantic моделей

## Переход на реальные данные

В будущей версии (спринт F5) Mock реализация будет заменена на Real реализацию с получением данных из базы данных. Контракт API при этом останется неизменным.

## Связанные документы

- [API Examples](api-examples.md) - Практические примеры использования
- [Frontend Roadmap](frontend-roadmap.md) - План развития frontend
