# Sprint 4 - Реализация ИИ-чата

**Статус:** В процессе реализации
**Дата начала:** 2025-10-17
**Финальный срок:** 2025-10-22 (5-6 дней)

---

## Обзор спринта

**Цель:** Создать полнофункциональный веб-интерфейс для ИИ-чата с двумя режимами работы и интегрировать его в дашборд.

**Основные компоненты:**
- Backend API для обработки чата со streaming ответами (SSE)
- Text-to-SQL pipeline для админ-режима
- Frontend компоненты (Floating Button, Chat Window, Chat Page)
- Интеграция в дашборд
- Сохранение истории в БД
- Переключение между режимами (normal/admin)

**Ключевые режимы:**

1. **Обычный режим (normal):** Общение с LLM-ассистентом с сохранением контекста
2. **Режим администратора (admin):**
   - Вопрос → Text2SQL → SQL выполнение → Результаты → LLM анализ → Ответ
   - Отображение SQL запросов для отладки
   - Доступ к статистике диалогов

---

## Фаза 1: Backend API и Text-to-SQL Pipeline ✅ НАЧАТА

### 1.1. Расширение моделей данных ✅

**Файлы:** `src/api/models.py`, `src/models.py`

#### Pydantic модели (API):
- ✅ `ChatMode` (enum) - normal/admin
- ✅ `MessageRole` (enum) - user/assistant
- ✅ `ChatMessage` - сообщение чата
- ✅ `TextToSqlRequest` - запрос конвертации
- ✅ `TextToSqlResponse` - результат конвертации
- ✅ `SuggestedQuestion` - рекомендуемый вопрос

#### SQLAlchemy модели (БД):
- ✅ `ChatSession` - сессии чата (id, user_id, mode, created_at)
- ✅ `ChatMessage` - сообщения (id, user_session_id, content, role, mode, sql_query, created_at)

#### Миграция:
- ✅ `alembic/versions/*_create_chat_tables.py` - создание таблиц chat_sessions и chat_messages

### 1.2. Text-to-SQL сервис ✅

**Файл:** `src/text2sql.py`

**Класс `Text2SqlConverter`:**
- ✅ `__init__(llm_client, db_manager, logger)` - инициализация
- ✅ `async convert(question, context)` - преобразование вопроса в SQL
- ✅ `async execute_and_format(sql)` - выполнение и форматирование результатов
- ✅ `_extract_sql(response)` - парсинг ответа LLM
- ✅ `_extract_explanation(response)` - извлечение объяснения
- ✅ `_format_table(rows)` - форматирование в таблицу Markdown

**Особенности:**
- Использует existing `LLMClient`
- Содержит схему БД для prompts
- Поддерживает SQLite
- Логирует все операции

### 1.3. Chat Service ✅

**Файл:** `src/api/chat_service.py`

**Класс `ChatService`:**
- ✅ `__init__(llm_client, db_manager, logger)` - инициализация
- ✅ `async process_message(message, session_id, mode, context_storage)` - основной метод с AsyncGenerator
- ✅ `async _process_normal_mode()` - обработка обычного режима
- ✅ `async _process_admin_mode()` - Text-to-SQL pipeline для админ-режима
- ✅ `async save_message(message)` - сохранение в БД
- ✅ `async get_history(session_id, limit)` - получение истории
- ✅ `async create_session(user_id, mode)` - создание сессии
- ✅ `async get_session(session_id)` - получение информации о сессии

**Особенности:**
- Streaming через AsyncGenerator
- Оба режима полностью реализованы
- История сохраняется автоматически
- SQL запросы хранятся в админ-режиме

### 1.4. API endpoints ✅

**Файл:** `src/api/chat.py` (новый)

**Routes:**
- ✅ `POST /api/chat/message` - обработка сообщения (StreamingResponse SSE)
- ✅ `GET /api/chat/history` - получение истории
- ✅ `POST /api/chat/debug/sql` - debug SQL без выполнения
- ✅ `POST /api/chat/session` - создание сессии

**Интеграция:**
- ❌ **TODO:** Подключить router в `src/api/main.py` (app.include_router)
- ❌ **TODO:** Заменить заглушки на реальные методы ChatService
- ❌ **TODO:** Добавить exception handling и валидацию

---

## Фаза 2: Frontend компоненты чата ⏳ К НАЧАЛУ

### 2.1. Типы и структуры данных

**Новый файл:** `frontend/web/src/types/chat.ts`

```typescript
export type ChatMode = 'normal' | 'admin';
export type MessageRole = 'user' | 'assistant';

export interface ChatMessage {
  id: string;
  content: string;
  role: MessageRole;
  mode: ChatMode;
  sqlQuery?: string;
  timestamp: Date;
}

export interface ChatSession {
  id: string;
  messages: ChatMessage[];
  mode: ChatMode;
  createdAt: Date;
}
```

### 2.2. API клиент для чата

**Файл:** `frontend/web/src/lib/api.ts` (расширение)

```typescript
export async function* chatMessage(
  message: string,
  mode: ChatMode = 'normal',
  sessionId: string
): AsyncGenerator<string> {
  // Использовать fetch с streaming (EventSource для SSE)
}

export async function getChatHistory(
  sessionId: string,
  limit?: number
): Promise<ChatMessage[]> {
  // GET /api/chat/history
}

export async function debugSql(
  question: string,
  context?: dict
): Promise<{sql: string; explanation: string}> {
  // POST /api/chat/debug/sql
}
```

### 2.3. Компоненты чата

**Папка:** `frontend/web/src/components/chat/`

1. **`chat-window.tsx`** - Основное окно чата
   - История сообщений (scrollable)
   - Поле ввода с кнопкой отправки
   - Loading indicator
   - Скелетон при загрузке

2. **`chat-message.tsx`** - Отдельное сообщение
   - Стилизация user/assistant
   - Markdown поддержка
   - SQL отображение (админ)
   - Avatar и timestamp

3. **`chat-input.tsx`** - Поле ввода
   - Textarea autoexpand
   - Enter для отправки (Shift+Enter для новой строки)
   - Suggested questions
   - Disabled во время загрузки

4. **`mode-toggle.tsx`** - Переключатель режимов
   - Normal/Admin toggle
   - Индикатор режима
   - Warning при смене

5. **`floating-chat-button.tsx`** - Плавающая кнопка
   - Правый нижний угол
   - Badge счетчик
   - Smooth animation

6. **`chat-container.tsx`** - Контейнер floating chat
   - Управление открытием/закрытием
   - Position fixed
   - Responsive (mobile = fullscreen)

### 2.4. Страница `/chat`

**Новый файл:** `frontend/web/src/app/chat/page.tsx`

- Layout: Header + ChatWindow + Sidebar (история сессий)
- Загрузка истории при входе
- Переключение между сессиями
- Responsive дизайн

### 2.5. Интеграция в дашборд

**Файл:** `frontend/web/src/app/dashboard/page.tsx` (изменение)

- Добавить `<FloatingChatButton />` компонент
- Использовать session_id дашборда
- Инициализировать ChatService

---

## Фаза 3: State Management ⏳ К НАЧАЛУ

### 3.1. Chat Store

**Новый файл:** `frontend/web/src/lib/chat-store.ts`

```typescript
interface ChatStore {
  sessionId: string;
  messages: ChatMessage[];
  currentMode: ChatMode;
  isLoading: boolean;
  error: string | null;

  setSessionId(id: string): void;
  addMessage(msg: ChatMessage): void;
  setMode(mode: ChatMode): void;
  setLoading(loading: boolean): void;
  setError(error: string | null): void;
  reset(): void;
}
```

Использовать React Context или Zustand.

### 3.2. Hooks

**Новый файл:** `frontend/web/src/hooks/use-chat.ts`

```typescript
export function useChat(sessionId: string) {
  // Управление состоянием
  // Отправка сообщений
  // Streaming обработка
  // Error handling
}

export function useChatMode(sessionId: string) {
  // Переключение режимов
  // Загрузка истории
}
```

---

## Фаза 4: Дополнительные функции и Polish ⏳ К НАЧАЛУ

### 4.1. Улучшения UI
- Dark mode поддержка
- Animations при появлении сообщений
- Copy кнопки для SQL
- Экспорт диалога (опционально)

### 4.2. Error Handling & Validation
- Timeout для запросов
- Retry logic
- Валидация на backend
- Rate limiting

### 4.3. Документация
- API документация (Swagger)
- Комментарии в коде
- README примеры

---

## Критерии готовности

### Backend ✅ ГОТОВ (с TODO)
- ✅ Chat endpoints структурированы
- ✅ Text-to-SQL реализован
- ✅ ChatService готов
- ⏳ Интеграция endpoints в main.py
- ⏳ Exception handling
- ⏳ API документация

### Frontend ⏳ В ОЧЕРЕДИ
- ⏳ Floating button открывает/закрывает чат
- ⏳ Сообщения отправляются и отображаются
- ⏳ Streaming ответы по chunks
- ⏳ Переключение режимов
- ⏳ История загружается
- ⏳ Responsive дизайн
- ⏳ No TypeScript errors
- ⏳ No ESLint errors

### Интеграция ⏳ В ОЧЕРЕДИ
- ⏳ Чат в дашборде (floating button)
- ⏳ Чат на странице `/chat`
- ⏳ History между сессиями
- ⏳ SQL видны в админ-режиме

---

## Технические решения

### Streaming реализация
- Server-Sent Events (SSE) через FastAPI `StreamingResponse`
- Frontend: `EventSource` API для SSE
- Fallback на polling если SSE недоступны

### Text-to-SQL pipeline (админ-режим)
1. ✅ Загрузить схему БД в памяти
2. ✅ Создать system prompt со схемой
3. ✅ Отправить вопрос в LLM
4. ✅ Парсить ответ (извлечь SQL)
5. ✅ Выполнить SQL
6. ✅ Вернуть результаты

### История сообщений
- ✅ Сохранять каждое сообщение в chat_messages
- Загружать при открытии сессии
- Использовать session_id для группировки

### Адаптивность
- Desktop (>1024px): Floating button + Chat modal (40% width)
- Tablet (768-1024px): Floating button + fullscreen modal
- Mobile (<768px): Fullscreen чат при открытии

---

## Зависимости и интеграция

### Backend
- ✅ Существующий: `LLMClient` (переиспользовать)
- ✅ Существующий: `DatabaseManager`
- ✅ Существующий: FastAPI, SQLAlchemy
- ✅ Существующий: Async generator

### Frontend
- Существующий: Next.js, React, shadcn/ui
- Новое: react-markdown (для markdown ответов)
- Новое: EventSource API (встроено в браузер)
- Существующий: API client

---

## Файловая структура (итог)

```
backend/
├── src/
│   ├── api/
│   │   ├── chat.py          # ✅ NEW
│   │   ├── chat_service.py  # ✅ NEW
│   │   ├── models.py        # ✅ UPDATED
│   │   └── main.py          # ⏳ TODO: подключить router
│   ├── text2sql.py          # ✅ NEW
│   ├── models.py            # ✅ UPDATED: добавлены ChatSession, ChatMessage
│   └── database.py          # (используется как есть)
├── alembic/versions/
│   └── 798d96052738_create_chat_tables.py  # ✅ NEW

frontend/web/src/
├── app/
│   ├── chat/
│   │   └── page.tsx         # ⏳ NEW
│   └── dashboard/
│       └── page.tsx         # ⏳ UPDATE
├── components/
│   └── chat/                # ⏳ NEW
│       ├── chat-window.tsx
│       ├── chat-message.tsx
│       ├── chat-input.tsx
│       ├── mode-toggle.tsx
│       ├── floating-chat-button.tsx
│       └── chat-container.tsx
├── hooks/
│   └── use-chat.ts          # ⏳ NEW
├── lib/
│   ├── api.ts               # ⏳ UPDATE
│   └── chat-store.ts        # ⏳ NEW
└── types/
    └── chat.ts              # ⏳ NEW
```

---

## TODO Интеграция

**Срочно (Blocking):**
- [ ] Подключить chat router в src/api/main.py
- [ ] Заменить заглушки в chat.py на реальные методы ChatService
- [ ] Добавить exception handling в endpoints
- [ ] Создать frontend types (chat.ts)
- [ ] Создать API client функции

**Высокий приоритет:**
- [ ] Создать все chat компоненты
- [ ] Реализовать state management
- [ ] Интегрировать в дашборд (Floating Button)
- [ ] Создать страницу /chat

**Документация:**
- [ ] Актуализировать frontend-roadmap.md
- [ ] Добавить ссылку на план в таблицу спринтов
- [ ] Проверить npm скрипты в package.json

---

## Статус по компонентам

| Компонент | Статус | Примечание |
|-----------|--------|-----------|
| ChatMode, MessageRole enums | ✅ | В models.py |
| ChatMessage модель (Pydantic) | ✅ | Для API |
| ChatMessage модель (SQLAlchemy) | ✅ | Для БД |
| ChatSession модель | ✅ | Для сессий |
| Text-to-SQL pipeline | ✅ | Полная реализация |
| ChatService | ✅ | Оба режима ready |
| API endpoints (chat.py) | ✅ | Структура ready, нужна интеграция |
| Миграция БД | ✅ | Готова к применению |
| Frontend types | ⏳ | В очереди |
| API client | ⏳ | В очереди |
| Chat компоненты | ⏳ | В очереди |
| State management | ⏳ | В очереди |
| Дашборд интеграция | ⏳ | В очереди |

---

**Дата последнего обновления:** 2025-10-17
**Ответственный:** AI Assistant
**Версия плана:** 1.1 (Обновлен с учетом проверки полноты)
