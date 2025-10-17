-- Схема базы данных
-- Sprint S1: Персистентное хранение данных (таблица messages)
-- Sprint S2: Получение данных пользователя из Telegram (таблица users)
-- Дата создания: 2025-10-16
-- Последнее обновление: 2025-10-16
--
-- Этот скрипт можно использовать для ручного создания БД без Alembic
-- (например, для разработки или отладки)
--
-- Использование:
--   sqlite3 data/messages.db < migrations/schema.sql

-- Создание таблицы messages
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    length INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT 0
);

-- Индекс для эффективной выборки последних сообщений пользователя
CREATE INDEX IF NOT EXISTS idx_user_id_created_at ON messages(user_id, created_at);

-- Индекс для фильтрации удаленных сообщений
CREATE INDEX IF NOT EXISTS idx_is_deleted ON messages(is_deleted);

-- Примечания для messages:
-- * is_deleted: 0 = активное сообщение, 1 = удалено (soft delete)
-- * role: 'user' или 'assistant'
-- * length: длина content в символах (вычисляется при вставке)

-- Создание таблицы users (Sprint S2)
CREATE TABLE IF NOT EXISTS users (
    telegram_id INTEGER PRIMARY KEY,
    username VARCHAR(32),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    language_code VARCHAR(10),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Индекс для поиска по username
CREATE INDEX IF NOT EXISTS idx_username ON users(username);

-- Примечания для users:
-- * telegram_id: уникальный ID пользователя в Telegram (используется как PK)
-- * username: может быть NULL (не у всех пользователей есть username)
-- * first_name, last_name, language_code: могут быть NULL
-- * created_at: дата первого обращения пользователя к боту
-- * updated_at: дата последнего обновления данных пользователя
