# Database Guide

Руководство по работе с базой данных в проекте systech-aidd-test.

## Содержание

1. [Обзор](#обзор)
2. [Схема базы данных](#схема-базы-данных)
3. [Работа с миграциями](#работа-с-миграциями)
4. [Примеры запросов](#примеры-запросов)
5. [Troubleshooting](#troubleshooting)

---

## Обзор

### Технологии

- **СУБД:** SQLite 3 (встроенная файловая БД)
- **Python драйвер:** aiosqlite (асинхронный)
- **ORM:** SQLAlchemy 2.0 (async API)
- **Миграции:** Alembic

### Расположение БД

- **Локально:** `./data/messages.db`
- **В Docker:** `/app/data/messages.db` (монтируется через volume)

### Принципы

- **Soft delete:** Данные не удаляются физически, используется флаг `is_deleted`
- **Асинхронность:** Весь доступ к БД асинхронный (async/await)
- **Автоматические метаданные:** Дата создания, длина сообщения

---

## Схема базы данных

### ER-диаграмма

См. [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) для полной диаграммы.

### Таблица `messages`

Хранит историю диалогов с пользователями.

| Поле        | Тип       | Ограничения         | Описание                          |
|-------------|-----------|---------------------|-----------------------------------|
| `id`        | INTEGER   | PRIMARY KEY, AUTO   | Уникальный идентификатор          |
| `user_id`   | INTEGER   | NOT NULL, INDEX     | Telegram ID пользователя          |
| `role`      | VARCHAR(20) | NOT NULL          | Роль: 'user' или 'assistant'      |
| `content`   | TEXT      | NOT NULL            | Текст сообщения                   |
| `length`    | INTEGER   | NOT NULL            | Длина сообщения в символах        |
| `created_at`| TIMESTAMP | NOT NULL, DEFAULT   | Дата и время создания             |
| `is_deleted`| BOOLEAN   | NOT NULL, DEFAULT FALSE, INDEX | Флаг мягкого удаления |

### Индексы

```sql
-- Композитный индекс для эффективной выборки последних сообщений пользователя
CREATE INDEX idx_user_id_created_at ON messages(user_id, created_at);

-- Индекс для фильтрации удаленных сообщений
CREATE INDEX idx_is_deleted ON messages(is_deleted);
```

---

## Работа с миграциями

### Инициализация БД

При первом запуске примените миграции:

```bash
make migrate-up
```

или

```bash
uv run alembic upgrade head
```

### Создание новой миграции

Если вы изменили модели SQLAlchemy в `src/models.py`:

```bash
make migrate-create MSG='Описание изменения'
```

или

```bash
uv run alembic revision --autogenerate -m "Описание изменения"
```

Alembic автоматически обнаружит изменения и создаст файл миграции в `alembic/versions/`.

### Просмотр истории миграций

```bash
make migrate-history
```

или

```bash
uv run alembic history
```

Вывод:
```
798d96052738 -> <current> (head), Create messages table
<base> -> 798d96052738, Create messages table
```

### Откат миграции

Откатить последнюю миграцию:

```bash
make migrate-down
```

или

```bash
uv run alembic downgrade -1
```

### Миграция к конкретной версии

```bash
uv run alembic upgrade <revision_id>
uv run alembic downgrade <revision_id>
```

---

## Примеры запросов

### Получение активных сообщений пользователя

```python
from sqlalchemy import select
from src.models import Message

# Последние 20 активных сообщений пользователя
stmt = (
    select(Message)
    .where(Message.user_id == user_id)
    .where(Message.is_deleted == False)
    .order_by(Message.created_at.desc())
    .limit(20)
)

result = await session.execute(stmt)
messages = result.scalars().all()
```

### Soft delete всех сообщений пользователя

```python
from sqlalchemy import update
from src.models import Message

stmt = (
    update(Message)
    .where(Message.user_id == user_id)
    .where(Message.is_deleted == False)
    .values(is_deleted=True)
)

await session.execute(stmt)
await session.commit()
```

### Добавление нового сообщения

```python
from src.models import Message

message = Message(
    user_id=user_id,
    role="user",
    content="Привет, бот!",
    length=len("Привет, бот!")
)

session.add(message)
await session.flush()  # Получить ID без коммита
await session.commit()
```

### Статистика по пользователю

```python
from sqlalchemy import select, func
from src.models import Message

# Количество активных сообщений
stmt = (
    select(func.count(Message.id))
    .where(Message.user_id == user_id)
    .where(Message.is_deleted == False)
)

count = await session.scalar(stmt)

# Общая длина всех сообщений
stmt = (
    select(func.sum(Message.length))
    .where(Message.user_id == user_id)
    .where(Message.is_deleted == False)
)

total_length = await session.scalar(stmt)
```

---

## Troubleshooting

### БД не создается

**Проблема:** Файл `data/messages.db` не создается при запуске.

**Решение:**
1. Убедитесь что директория `data/` существует:
   ```bash
   mkdir -p data
   ```

2. Примените миграции:
   ```bash
   make migrate-up
   ```

### Ошибка "no such table: messages"

**Проблема:** Таблица `messages` не существует.

**Решение:** Примените миграции:
```bash
uv run alembic upgrade head
```

### Ошибка "database is locked"

**Проблема:** SQLite блокирует БД при одновременном доступе.

**Решение:**
1. Убедитесь что не запущено несколько экземпляров бота
2. Проверьте что нет "зависших" процессов:
   ```bash
   ps aux | grep python
   ```
3. Перезапустите бот

### Как сбросить БД полностью

**Внимание:** Это удалит все данные!

```bash
# Удалить БД
rm data/messages.db

# Создать заново
uv run alembic upgrade head
```

### Проблемы с миграциями

**Ошибка:** "Can't locate revision identified by '<id>'"

**Решение:** Проверьте что все файлы миграций на месте:
```bash
ls -la alembic/versions/
```

Если миграции потеряны, пересоздайте БД:
```bash
rm data/messages.db
uv run alembic upgrade head
```

### Docker volume проблемы

**Проблема:** Данные не сохраняются после перезапуска Docker контейнера.

**Решение:** Убедитесь что volume правильно смонтирован:
```bash
docker-compose down
docker-compose up -d
docker-compose logs bot | grep "Database"
```

Проверьте `docker-compose.yml`:
```yaml
volumes:
  - ./data:/app/data  # Корректный маунт
```

---

## Best Practices

### Разработка

1. **Всегда используйте миграции** - не создавайте таблицы вручную
2. **Проверяйте миграции** - просматривайте сгенерированные файлы перед применением
3. **Тестируйте откаты** - убедитесь что `downgrade()` работает
4. **Используйте транзакции** - группируйте связанные операции

### Production

1. **Бэкапы** - регулярно создавайте копии `data/messages.db`
2. **Мониторинг** - следите за размером БД
3. **Soft delete** - не удаляйте данные физически
4. **Docker volumes** - используйте volumes для персистентности

### Тестирование

1. **In-memory БД** - используйте `:memory:` для юнит-тестов
2. **Изоляция** - создавайте свежую БД для каждого теста
3. **Фикстуры** - переиспользуйте общие настройки

Пример тестовой фикстуры:

```python
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

@pytest.fixture
async def db_session():
    """Создает in-memory БД для тестов."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )

    async with async_session() as session:
        yield session

    await engine.dispose()
```

---

## Дополнительные ресурсы

- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Alembic Tutorial](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) - Полная схема БД с диаграммами
- [docs/ADR.md](../ADR.md) - Архитектурные решения по БД (ADR-022 до ADR-025)

---

**Обновлено:** Sprint S1
**Автор:** systech-aidd-test team
