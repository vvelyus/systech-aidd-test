# Схема базы данных

Документ описывает структуру базы данных для хранения истории диалогов бота.

---

## Обзор

Используется **SQLite 3** с асинхронным драйвером **aiosqlite** и ORM **SQLAlchemy 2.0**.

Стратегия удаления данных: **soft delete** (физически данные не удаляются, помечаются флагом `is_deleted`).

---

## Таблица: messages

Хранит историю всех сообщений пользователей и ответов бота.

### Структура таблицы

| Поле | Тип | Ограничения | Описание |
|------|-----|-------------|----------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Уникальный идентификатор сообщения |
| `user_id` | INTEGER | NOT NULL | Telegram ID пользователя |
| `role` | VARCHAR(20) | NOT NULL | Роль отправителя: 'user' или 'assistant' |
| `content` | TEXT | NOT NULL | Текст сообщения |
| `length` | INTEGER | NOT NULL | Длина сообщения в символах |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Дата и время создания |
| `is_deleted` | BOOLEAN | NOT NULL, DEFAULT FALSE | Флаг soft delete (0 = активно, 1 = удалено) |

### Индексы

1. **idx_user_id_created_at** - составной индекс на `(user_id, created_at)`
   - Назначение: эффективная выборка последних N сообщений для конкретного пользователя
   - Используется в `get_context()` для получения истории диалога

2. **idx_is_deleted** - индекс на `(is_deleted)`
   - Назначение: быстрая фильтрация неудаленных сообщений
   - Используется во всех запросах для исключения "удаленных" записей

### ER-диаграмма

```
┌─────────────────────────────────────┐
│          messages                   │
├─────────────────────────────────────┤
│ 🔑 id: INTEGER (PK)                 │
│ 👤 user_id: INTEGER                 │
│ 🏷️  role: VARCHAR(20)               │
│ 💬 content: TEXT                    │
│ 📏 length: INTEGER                  │
│ 🕐 created_at: TIMESTAMP            │
│ 🗑️  is_deleted: BOOLEAN             │
└─────────────────────────────────────┘
         │
         │ Связь по user_id
         │ (один пользователь → много сообщений)
         ▼
   [Telegram User]
```

---

## Основные операции

### 1. Добавление сообщения

```sql
INSERT INTO messages (user_id, role, content, length, created_at, is_deleted)
VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, 0);
```

**Параметры:**
- `user_id` - Telegram ID пользователя
- `role` - 'user' или 'assistant'
- `content` - текст сообщения
- `length` - длина текста (вычисляется автоматически)

### 2. Получение контекста (последние N сообщений)

```sql
SELECT role, content
FROM messages
WHERE user_id = ? AND is_deleted = 0
ORDER BY created_at DESC
LIMIT ?;
```

**Параметры:**
- `user_id` - Telegram ID пользователя
- `LIMIT` - количество сообщений (обычно 20)

**Примечание:** результаты нужно развернуть (reverse), чтобы получить хронологический порядок.

### 3. Очистка контекста (soft delete)

```sql
UPDATE messages
SET is_deleted = 1
WHERE user_id = ? AND is_deleted = 0;
```

**Параметры:**
- `user_id` - Telegram ID пользователя

Это помечает все активные сообщения пользователя как удаленные, но физически они остаются в БД.

### 4. Получение статистики

```sql
-- Количество активных сообщений
SELECT COUNT(*) FROM messages WHERE is_deleted = 0;

-- Количество пользователей с активными диалогами
SELECT COUNT(DISTINCT user_id) FROM messages WHERE is_deleted = 0;

-- Средняя длина сообщений
SELECT AVG(length) FROM messages WHERE is_deleted = 0;
```

---

## Миграции

Управление версиями схемы БД осуществляется через **Alembic**.

### Создание миграции

```bash
uv run alembic revision --autogenerate -m "описание изменений"
```

### Применение миграций

```bash
uv run alembic upgrade head
```

### Откат миграции

```bash
uv run alembic downgrade -1
```

### Просмотр истории

```bash
uv run alembic history
```

---

## Конфигурация

### Путь к БД

По умолчанию: `./data/messages.db`

Можно изменить через переменную окружения:
```bash
DATABASE_URL=sqlite+aiosqlite:///./custom/path/db.sqlite
```

### Инициализация

БД инициализируется автоматически при первом запуске приложения через `init_db()`.

---

## Производительность

### Оптимизация запросов

1. **Индексы** - создано 2 индекса для ускорения основных операций
2. **LIMIT** - ограничение количества возвращаемых сообщений
3. **Soft delete** - быстрое "удаление" без физического изменения данных

### Рекомендации

- Для production рекомендуется периодически очищать старые `is_deleted=1` записи (архивирование)
- При росте числа пользователей > 10000 рассмотреть миграцию на PostgreSQL
- Регулярно делать backup файла БД

---

## Расширение схемы (будущее)

Потенциальные улучшения:

1. **Таблица users** - хранение метаданных пользователей (username, settings)
2. **Таблица sessions** - группировка сообщений по сессиям
3. **Таблица feedback** - оценки ответов бота
4. **Full-text search** - индексирование текста для поиска

---

*Последнее обновление: 2025-10-16 (Sprint S1)*
