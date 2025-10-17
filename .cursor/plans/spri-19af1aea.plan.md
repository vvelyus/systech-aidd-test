<!-- 19af1aea-8f27-4908-a6d9-a6166e79e860 50eacaea-5d91-40a8-ab2e-05ce1cb7bb5f -->
# Sprint 5 - Real API Integration

## Обзор спринта

**Цель:** Заменить mock реализацию на real LLM integration, добавить production-ready оптимизации, расширить frontend с улучшениями UI, и обеспечить comprehensive testing.

**Длительность:** 6 дней (Backend 2-3 дня + Frontend 2 дня + Testing 1-2 дня)

**Статус:** 80% → 100% завершение проекта

---

## Фаза 1: Backend Real LLM Integration & Optimizations (2-3 дня)

### 1.1. Расширить Text2SqlConverter с production features

**Файл:** `src/text2sql.py` (расширение)

**Изменения:**

- Добавить SQL validation через `sqlparse` (парсить и проверять keywords)
- Реализовать question caching с TTL 1 час (dict-based с timestamp)
- Security: whitelist операций (SELECT only, no DROP/DELETE/UPDATE/INSERT)
- Timeout для SQL execution: 5 сек max (asyncio.timeout)
- Result limiter: max 1000 rows per query
- Error handling для SQL errors (parse errors, timeout, no results)
- Logging для каждой Text-to-SQL операции

**Код структура:**

```python
class Text2SqlConverter:
    def __init__(self, llm_client, db_manager, cache_ttl=3600):
        self.llm_client = llm_client
        self.db_manager = db_manager
        self.cache = {}  # {question_hash: (sql, timestamp)}
        self.schema_cache = None
        self.allowed_keywords = {'SELECT', 'WHERE', 'JOIN', 'GROUP', 'ORDER', 'LIMIT', 'HAVING', 'DISTINCT'}
        self.forbidden_keywords = {'DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'TRUNCATE'}
    
    async def convert(self, question: str, context: dict = None) -> TextToSqlResponse:
        # 1. Check cache (hash question)
        # 2. Generate SQL via LLM with retries (3 attempts)
        # 3. Validate SQL (keyword check, sqlparse check)
        # 4. Return TextToSqlResponse with sql + explanation
    
    async def execute_and_format(self, sql: str, max_rows=1000) -> str:
        # 1. Execute with timeout (5 sec)
        # 2. Limit rows to max_rows
        # 3. Format as markdown table
        # 4. Handle errors gracefully
```

### 1.2. Расширить ChatService с streaming optimization

**Файл:** `src/api/chat_service.py` (расширение)

**Изменения:**

- Добавить `temperature` параметр: 0.3 для admin (SQL), 0.7 для normal (casual)
- Реализовать retry logic (3 попытки с exponential backoff)
- Добавить timeout (30 сек для request, 5 сек для Text-to-SQL)
- Специальный system prompt для admin режима
- Optimized chunking для streaming (yield на каждые 50+ characters или punctuation)
- Error recovery (если LLM timeout, return cached similar response или generic error message)

**Специальные system prompts:**

```python
SYSTEM_PROMPTS = {
    "normal": "You are a helpful AI assistant...",
    "admin": "You are a SQL expert. Your task is to help analyze dialog statistics. Answer based on SQL query results. Be concise and factual."
}
```

### 1.3. Оптимизировать API endpoints

**Файл:** `src/api/chat.py` (расширение)

**Изменения:**

- Добавить `/api/chat/debug/explain` endpoint (explain query execution plan)
- Добавить rate limiting (использовать SimpleNamespace временные окна)
- Добавить request validation (max message length 5000 chars)
- Оптимизировать streaming: yield chunks с minimal latency
- Добавить request logging (user_id, session_id, message length, response time)

### 1.4. Database optimizations

**Файл:** `alembic/versions/*_optimize_chat_indexes.py` (новая миграция)

**Изменения:**

```sql
CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at DESC);
```

**Также в `src/api_server.py`:**

- Включить SQLite WAL mode: `sqlite3.enable_shared_cache(True)`
- Оптимизировать connection pool для SQLAlchemy

---

## Фаза 2: Frontend Streaming UI Improvements (2 дня)

### 2.1. Расширить chat-message компонент

**Файл:** `frontend/web/src/components/chat/chat-message.tsx` (расширение)

**Добавить:**

- Markdown rendering с syntax highlighting для code blocks
- Copy button для SQL queries (с visual feedback)
- Timestamp formatting (relative time: "2 minutes ago")
- Admin mode badge для SQL messages
- Error message styling с red background
- Loading skeleton для streaming messages (pulse animation)

### 2.2. Улучшить chat-input компонент

**Файл:** `frontend/web/src/components/chat/chat-input.tsx` (расширение)

**Добавить:**

- Character counter (max 5000)
- Disable button при max length
- Visual feedback при typing (dots animation)
- Keyboard shortcut info (tooltip: "Enter to send, Shift+Enter for newline")
- Auto-focus на открытие (useEffect + useRef)
- Smooth height animation при multi-line text

### 2.3. Создать loading-skeleton компонент

**Новый файл:** `frontend/web/src/components/chat/loading-skeleton.tsx`

**Функции:**

- Pulse animation для skeleton
- Show 3-5 skeleton messages при первой загрузке
- Fade-out при появлении реального content

### 2.4. Создать chat-error компонент

**Новый файл:** `frontend/web/src/components/chat/chat-error.tsx`

**Функции:**

- Отобразить error message с иконкой
- Retry button (resubmit last message)
- Dismiss button
- Auto-hide через 10 сек (опционально)
- Разные стили для network vs LLM errors

### 2.5. Расширить chat-container

**Файл:** `frontend/web/src/components/chat/chat-container.tsx` (расширение)

**Добавить:**

- Error state management (show ChatError компонент)
- Loading state management (show skeletons)
- Unread message counter (badge on floating button)
- Auto-scroll to latest message (useEffect + ref.current?.scrollIntoView)
- Session persistence (save last session_id to localStorage)

---

## Фаза 3: Pagination & History Management (1 день)

### 3.1. Расширить API для pagination

**Файл:** `src/api/chat.py` (изменение)

**Изменить endpoint:**

```python
@app.get("/api/chat/history")
async def get_chat_history(
    session_id: str = Query(...),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
) -> PaginatedResponse[ChatMessage]:
    # Return {items: ChatMessage[], total: int, hasMore: bool}
```

### 3.2. Создать infinite scroll в frontend

**Файл:** `frontend/web/src/components/chat/chat-window.tsx` (расширение)

**Добавить:**

- Intersection Observer для "load more" button
- Fetch older messages when scrolling up
- Loading indicator при fetching history
- Merge new messages with existing (avoid duplicates)

---

## Фаза 4: Comprehensive Testing (1-2 дня)

### 4.1. Unit tests для backend

**Новый файл:** `tests/test_text2sql_production.py`

**Tests:**

- Test SQL validation (allowed/forbidden keywords)
- Test caching (same question returns cached result)
- Test timeout handling (SQL execution > 5 sec)
- Test result limiting (> 1000 rows truncated)
- Test error recovery (LLM timeout → graceful degradation)

**Новый файл:** `tests/test_chat_service_production.py`

**Tests:**

- Test temperature config per mode
- Test retry logic (3 attempts on failure)
- Test streaming chunks (proper formatting)
- Test error messages (include context)
- Test mode-specific behavior (admin vs normal)

### 4.2. Integration tests

**Новый файл:** `tests/test_chat_integration.py`

**Tests:**

- Full flow: message → LLM → response (normal mode)
- Full flow: question → Text-to-SQL → execution → LLM answer (admin mode)
- History persistence (save to DB, load back)
- Mode switching (clear history with warning)
- Streaming response parsing (frontend receives all chunks)

### 4.3. E2E tests (optional, but recommended)

**Новый файл:** `tests/test_chat_e2e.py` (используя pytest + Playwright или Cypress)

**Tests:**

- Dashboard: click floating button → open chat
- Send message in normal mode → receive streaming response
- Switch to admin mode → send question → see SQL execution
- Check history persistence (refresh → history still there)
- Mobile responsive (fullscreen on small screen)

### 4.4. Performance tests

**Новый файл:** `tests/test_chat_performance.py`

**Tests:**

- Measure latency: LLM response time (target: < 3 sec)
- Measure latency: Text-to-SQL conversion (target: < 2 sec)
- Measure throughput: parallel requests (target: 10+ concurrent)
- Memory usage: after 100+ messages (target: < 100MB)
- Database query performance (with indexes)

---

## Фаза 5: Documentation & Polish (1 день)

### 5.1. API Documentation

**Файл:** Update `frontend/doc/api-contract.md`

**Добавить:**

- Chat endpoints specification (with examples)
- Error response formats
- Rate limiting info
- Caching behavior
- Timeout behavior

### 5.2. Architecture Documentation

**Новый файл:** `docs/ARCHITECTURE_S5.md`

**Содержание:**

- Real LLM integration diagram
- Text-to-SQL pipeline flow
- Caching strategy (question cache, schema cache)
- Error handling strategy
- Performance optimizations applied

### 5.3. Testing Documentation

**Новый файл:** `docs/TESTING_GUIDE_S5.md`

**Содержание:**

- How to run tests (unit, integration, E2E)
- How to test Text-to-SQL locally
- How to test streaming responses
- Performance benchmarking guide

### 5.4. Deployment Readiness Checklist

**Новый файл:** `DEPLOYMENT_CHECKLIST.md`

**Items:**

- [ ] All tests passing (unit + integration + E2E)
- [ ] No TypeScript errors
- [ ] No ESLint errors
- [ ] Performance benchmarks met
- [ ] Error handling tested
- [ ] Rate limiting configured
- [ ] Logging configured
- [ ] Database backups configured
- [ ] Monitoring/alerting configured

---

## Implementation Tasks (Todos)

### Backend Tasks (Tier 1 - Critical)

- [ ] S5-B1: Extend Text2SqlConverter with caching, validation, security (src/text2sql.py)
- [ ] S5-B2: Add production features to ChatService (temperature, retry, timeout) (src/api/chat_service.py)
- [ ] S5-B3: Create database optimization migration (add indexes, WAL mode)
- [ ] S5-B4: Create unit tests for Text2SqlConverter (tests/test_text2sql_production.py)
- [ ] S5-B5: Create unit tests for ChatService (tests/test_chat_service_production.py)

### Frontend Tasks (Tier 1 - Critical)

- [ ] S5-F1: Extend chat-message with markdown rendering, copy button, error styling
- [ ] S5-F2: Create loading-skeleton component with pulse animation
- [ ] S5-F3: Create chat-error component with retry button
- [ ] S5-F4: Extend chat-container with error/loading state management
- [ ] S5-F5: Extend chat-input with character counter, keyboard hints

### Integration Tasks (Tier 2 - Important)

- [ ] S5-I1: Create pagination in API endpoint (limit, offset, hasMore)
- [ ] S5-I2: Implement infinite scroll in chat-window
- [ ] S5-I3: Create integration tests (tests/test_chat_integration.py)
- [ ] S5-I4: Create E2E tests (tests/test_chat_e2e.py) - optional but recommended

### Documentation Tasks (Tier 3 - Nice to have)

- [ ] S5-D1: Update API contract documentation
- [ ] S5-D2: Create architecture documentation (ARCHITECTURE_S5.md)
- [ ] S5-D3: Create testing guide (TESTING_GUIDE_S5.md)
- [ ] S5-D4: Create deployment checklist (DEPLOYMENT_CHECKLIST.md)

### Polish Tasks (Tier 3 - Nice to have)

- [ ] S5-P1: Dark mode support for chat
- [ ] S5-P2: Message animations (fade-in, slide-in)
- [ ] S5-P3: Export conversation (PDF or JSON)
- [ ] S5-P4: Suggested questions based on context

---

## Technical Decisions

### Caching Strategy

- Question caching: Simple dict with timestamp (production-ready for single-instance)
- TTL: 1 hour for questions
- Schema caching: Load once at startup, refresh on demand
- Future: Redis for distributed caching (Sprint 6)

### Error Handling

- Network errors: Retry 3x with exponential backoff
- Timeout errors: Show user-friendly message + suggest simpler query
- LLM errors: Fallback to cached similar response or generic message
- Database errors: Log error, return error message

### Performance Targets

- LLM response: < 3 seconds
- Text-to-SQL: < 2 seconds
- Streaming latency: < 100ms between chunks
- API response: < 5 seconds total (including LLM)
- Database query: < 500ms (with indexes)

### Database Optimization

- Add indexes on session_id, user_id, created_at
- Enable SQLite WAL mode for concurrent access
- Connection pooling via SQLAlchemy
- Query result caching (10 min TTL)

---

## Deliverables

**Backend:**

- Real LLM integration with optimizations
- Text-to-SQL with caching and security
- Database optimizations
- Comprehensive error handling
- Unit tests coverage > 80%

**Frontend:**

- Streaming UI improvements
- Loading skeleton animations
- Error handling with retry
- Pagination and infinite scroll
- Mobile responsive enhancements

**Testing:**

- Unit tests (Backend: 15+, Frontend: 10+)
- Integration tests (5+ scenarios)
- E2E tests (3+ user flows)
- Performance benchmarks

**Documentation:**

- API contract update
- Architecture documentation
- Testing guide
- Deployment checklist

---

## Success Criteria

- ✅ All tests passing (unit + integration + E2E)
- ✅ Performance benchmarks met (LLM < 3s, Text-to-SQL < 2s)
- ✅ TypeScript strict mode: 0 errors
- ✅ ESLint: 0 errors
- ✅ Error handling tested for 5+ scenarios
- ✅ Rate limiting configured and tested
- ✅ Streaming responses working smoothly (no delays)
- ✅ Database optimizations applied and validated
- ✅ Documentation complete and clear
- ✅ Code ready for production deployment

---

## Timeline

- **Day 1-2:** Backend Real LLM + Text-to-SQL optimizations
- **Day 2:** Backend unit tests
- **Day 2-3:** Frontend UI improvements + loading/error components
- **Day 3:** Integration tests + pagination
- **Day 4:** E2E tests + performance benchmarks
- **Day 4-5:** Documentation + polish
- **Day 5-6:** Final testing + deployment checklist prep

---

**Status:** Ready for Implementation

**Estimated Hours:** 40-50 hours (single developer)

**Complexity:** Medium-High (Production-grade optimization)

### To-dos

- [ ] Расширить модели данных: ChatMessage, ChatResponse, TextToSqlRequest/Response. Добавить миграцию для таблицы chat_messages
- [ ] Создать Text2SqlConverter в src/text2sql.py с методами convert() и execute_and_format()
- [ ] Создать ChatService в src/api/chat_service.py с обработкой обоих режимов (normal/admin) и streaming
- [ ] Создать API endpoints: POST /api/chat/message (streaming), GET /api/chat/history, POST /api/chat/debug/sql
- [ ] Создать типы для чата в frontend/web/src/types/chat.ts (ChatMessage, ChatMode, etc.)
- [ ] Расширить frontend/web/src/lib/api.ts: chatMessage() с streaming, getChatHistory(), debugSql()
- [ ] Создать компоненты чата: chat-window, chat-message, chat-input, mode-toggle, floating-chat-button, chat-container
- [ ] Создать страницу /chat в frontend/web/src/app/chat/page.tsx с историей сессий
- [ ] Создать state management (chat-store.ts и use-chat.ts hooks) для управления состоянием чата
- [ ] Интегрировать FloatingChatButton в дашборд, добавить session management
- [ ] Написать интеграционные тесты для chat endpoints, Text2SQL converter, frontend компонентов
- [ ] UI polish: animations, dark mode, error handling, validation, rate limiting, documentation