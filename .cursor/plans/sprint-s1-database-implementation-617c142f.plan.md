<!-- 617c142f-e516-43f6-8217-73393e4fbe8b b8cfdc8e-a38b-4f8c-945a-bee268f709bb -->
# План реализации Sprint S1: Персистентное хранение данных

## 1. ADR для выбора технологий

Добавить в `docs/ADR.md` четыре новых решения с явным указанием технологий:

- **ADR-022**: Выбор SQLite как СУБД для хранения истории диалогов
  - ✅ **СУБД:** SQLite 3 (встроенная файловая БД, не требует отдельного сервера)
  - Обоснование: простота, KISS подход, достаточно для малых/средних нагрузок, легко бэкапить

- **ADR-023**: Использование aiosqlite как Python драйвера для SQLite
  - ✅ **Python драйвер СУБД:** aiosqlite (асинхронный драйвер для SQLite)
  - Обоснование: совместимость с async/await, необходим для async SQLAlchemy

- **ADR-024**: Использование SQLAlchemy 2.0 как ORM
  - ✅ **Подход к доступу к данным:** ORM (Object-Relational Mapping) через SQLAlchemy 2.0
  - Обоснование: абстракция от SQL, type safety, удобная работа с моделями, автогенерация миграций

- **ADR-025**: Alembic для управления миграциями схемы БД
  - ✅ **Инструмент миграций:** Alembic
  - Обоснование: стандарт для SQLAlchemy, автогенерация миграций, версионирование схемы

## 2. Настройка зависимостей

Обновить `pyproject.toml`:

- Добавить `sqlalchemy>=2.0` в dependencies
- Добавить `aiosqlite>=0.19.0` в dependencies (асинхронный драйвер для SQLite)
- Добавить `alembic>=1.13` в dependencies

Запустить `uv sync` для установки новых зависимостей.

## 3. Проектирование схемы БД

Создать таблицу `messages` со следующими полями:

- `id` (INTEGER, PRIMARY KEY, AUTOINCREMENT)
- `user_id` (INTEGER, NOT NULL, INDEX) - Telegram ID пользователя
- `role` (VARCHAR(20), NOT NULL) - 'user' или 'assistant'
- `content` (TEXT, NOT NULL) - текст сообщения
- `length` (INTEGER, NOT NULL) - длина сообщения в символах
- `created_at` (TIMESTAMP, NOT NULL, DEFAULT CURRENT_TIMESTAMP)
- `is_deleted` (BOOLEAN, NOT NULL, DEFAULT FALSE) - для soft delete

Индексы:

- `idx_user_id_created_at` на (user_id, created_at) для эффективной выборки последних сообщений
- `idx_is_deleted` на (is_deleted) для фильтрации удаленных сообщений

Создать ER-диаграмму в `docs/guides/DATABASE_SCHEMA.md`.

Создать SQL-скрипт `migrations/schema.sql` для ручного создания таблицы:

```sql
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    length INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT 0
);

CREATE INDEX idx_user_id_created_at ON messages(user_id, created_at);
CREATE INDEX idx_is_deleted ON messages(is_deleted);
```

Этот скрипт можно использовать для быстрой инициализации БД без Alembic (например, для разработки или отладки).

## 4. Инициализация Alembic

Выполнить:

```bash
uv run alembic init alembic
```

Настроить `alembic.ini`:

- Установить `sqlalchemy.url` для SQLite: `sqlite:///./data/messages.db`

Настроить `alembic/env.py`:

- Импортировать модели SQLAlchemy
- Подключить метаданные для автогенерации миграций

## 5. Создание моделей SQLAlchemy

Создать файл `src/models.py` с моделью `Message`:

- Использовать декларативный стиль SQLAlchemy 2.0
- Определить все поля согласно схеме
- Добавить `__repr__` для удобной отладки

## 6. Создание первой миграции

Выполнить:

```bash
uv run alembic revision --autogenerate -m "Create messages table"
uv run alembic upgrade head
```

Проверить создание БД в `data/messages.db`.

## 7. Реализация Database Context Storage

Создать новый класс `DatabaseContextStorage` в `src/context_storage.py`:

- Реализовать протокол `ContextStorage`
- В `add_message()`: сохранять сообщение в БД с автоматическим расчетом length
- В `get_context()`: выбирать последние N сообщений где `is_deleted=False`, упорядочивая по `created_at`
- В `reset_context()`: выполнять soft delete (устанавливать `is_deleted=True`) для всех сообщений пользователя
- Использовать async SQLAlchemy session
- Добавить метод `close()` для корректного закрытия соединения

## 8. Создание Database Manager

Создать файл `src/database.py`:

- Функция `get_engine()` для создания async engine SQLAlchemy
- Функция `get_session()` для получения async session
- Функция `init_db()` для инициализации БД при старте приложения

## 9. Обновление конфигурации

Обновить `src/config.py`:

- Добавить `database_url` (по умолчанию `sqlite+aiosqlite:///./data/messages.db`)
- Добавить получение из переменной окружения `DATABASE_URL`

## 10. Рефакторинг main.py

Обновить `src/main.py`:

- Импортировать новые модули (database, models)
- Вызывать `init_db()` при старте
- Создавать `DatabaseContextStorage` вместо `InMemoryContextStorage`
- Передавать async session в storage
- Корректно закрывать соединение при завершении

## 11. Docker контейнеризация

Создать файлы:

**Dockerfile**:

- Использовать базовый образ `python:3.11-slim`
- Установить uv
- Скопировать файлы проекта
- Установить зависимости через `uv sync`
- Создать директорию `data/` для SQLite
- Запускать приложение

**docker-compose.yml**:

- Определить сервис `bot`
- Монтировать volume для `data/` (персистентность БД)
- Монтировать volume для `logs/` (персистентность логов)
- Использовать `.env` для переменных окружения
- Настроить restart policy

**.dockerignore**:

- Исключить `.venv/`, `__pycache__/`, `.git/`, и т.д.

## 12. Обновление документации

Создать `docs/guides/DATABASE_GUIDE.md`:

- Описание схемы БД с ER-диаграммой
- Инструкции по работе с миграциями
- Примеры запросов

Обновить `README.md`:

- Добавить раздел о Docker
- Команды для запуска через Docker Compose
- Инструкции по работе с БД

Обновить `Makefile`:

- Добавить команды для Docker: `docker-build`, `docker-up`, `docker-down`
- Добавить команды для миграций: `migrate-create`, `migrate-up`, `migrate-down`

## 13. Обновление тестов

Обновить/создать тесты:

- `tests/test_models.py` - тесты для SQLAlchemy моделей
- `tests/test_database.py` - тесты для database manager
- Обновить `tests/test_context_storage.py` - добавить тесты для `DatabaseContextStorage`
- Использовать in-memory SQLite (`:memory:`) для тестов
- Обеспечить coverage 85%+

Обновить `tests/conftest.py`:

- Добавить фикстуры для async database session
- Добавить фикстуру для in-memory БД

## 14. Создание тасклиста

Создать `docs/tasklists/tasklist-s1.md`:

- Детальный список всех задач спринта
- Чеклисты для каждого этапа
- Критерии завершения спринта

## 15. Запуск и проверка

- Выполнить `make ci` (lint, format, type-check, test)
- Проверить работу приложения локально
- Протестировать Docker контейнер
- Проверить персистентность данных после перезапуска
- Убедиться что soft delete работает корректно

### To-dos

- [x] Добавить ADR-022, ADR-023, ADR-024, ADR-025 в docs/ADR.md
- [x] Обновить pyproject.toml: добавить sqlalchemy, aiosqlite, alembic
- [x] Спроектировать схему БД и создать ER-диаграмму в docs/guides/DATABASE_SCHEMA.md
- [x] Инициализировать Alembic и настроить конфигурацию
- [x] Создать SQLAlchemy модели в src/models.py
- [x] Создать и применить первую миграцию для таблицы messages
- [ ] Создать database manager в src/database.py
- [ ] Реализовать DatabaseContextStorage в src/context_storage.py
- [ ] Обновить src/config.py с настройками БД
- [ ] Рефакторинг src/main.py для использования БД
- [ ] Создать Dockerfile, docker-compose.yml и .dockerignore
- [ ] Обновить документацию (README.md, DATABASE_GUIDE.md, Makefile)
- [ ] Создать/обновить тесты для новой функциональности
- [ ] Создать docs/tasklists/tasklist-s1.md
- [ ] Актуализировать docs/VISION.md: обновить структуру проекта, архитектуру, модель данных
- [ ] Актуализировать docs/IDEA.md на соответствие изменениям (если требуется)
- [ ] Добавить ссылку на план спринта в таблицу спринтов в docs/roadmap.md
- [ ] Выполнить финальную проверку (CI, Docker, персистентность)