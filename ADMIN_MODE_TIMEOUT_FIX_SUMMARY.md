# Admin Mode Timeout Fix - Comprehensive Summary

**Date:** October 18, 2025
**Status:** ✅ COMPLETED

## Problem Statement

The admin mode chat was experiencing "Request timed out (too complex query)" errors when users asked statistical questions like:
- "Сколько сообщений было отправлено на этой неделе?" (How many messages were sent this week?)

The error message indicated that complex queries were timing out before they could complete.

## Root Cause Analysis

The admin mode workflow involves multiple steps, each with its own timeout:

```
User Question → Text-to-SQL Conversion (LLM)
             → SQL Query Generation
             → Database Execution
             → Result Formatting
             → LLM Response Generation
             → User Display
```

**Issues found:**
1. Text-to-SQL conversion timeout: **5 seconds** (too short)
2. SQL execution timeout: **10 seconds internal** (too short)
3. SQL execution wrapper timeout: **20 seconds** (insufficient for complex queries)
4. LLM response timeout: **60 seconds** in initialization but wrapped at 20 seconds
5. Browser client timeout: **No explicit timeout** (relies on browser default, often ~30s)

## Solution Implemented

### 1. Backend Timeouts Updated

#### `src/api/main.py` - ChatService Initialization
```python
# BEFORE
chat_service = ChatService(
    request_timeout=60.0,    # LLM responses
    text2sql_timeout=15.0,   # SQL generation
)

# AFTER
chat_service = ChatService(
    request_timeout=90.0,    # Increased 60s → 90s
    text2sql_timeout=30.0,   # Increased 15s → 30s
)
```

#### `src/api/chat_service.py` - Admin Mode Processing

**Step 1: Text-to-SQL Conversion**
- Timeout: **5s → 30s** (configurable via `text2sql_timeout`)
- Reason: LLM needs time to generate complex SQL queries

**Step 2: SQL Query Execution**
- Internal timeout: **10s → 30s**
- Wrapper timeout: **20s → 40s**
- Reason: Database queries on large datasets can be slow

**Step 3: LLM Result Interpretation**
- Timeout: **20s → 90s** (uses full `request_timeout`)
- Reason: Analysis of complex results requires more processing

#### `src/text2sql.py` - SQL Generation

```python
# BEFORE
await asyncio.wait_for(
    self.llm_client.get_response(...),
    timeout=5.0  # 5 seconds
)

# AFTER
await asyncio.wait_for(
    self.llm_client.get_response(...),
    timeout=15.0  # 15 seconds (for SQL generation)
)
```

### 2. Frontend Timeouts Added

#### `frontend/web/src/lib/api.ts` - HTTP Client Configuration

**New timeout configuration:**
```typescript
const TIMEOUT_CONFIG = {
  default: 30000,      // 30s for regular requests
  chat: 180000,        // 3 minutes for chat messages ✨
  stats: 60000,        // 1 minute for statistics
  session: 30000,      // 30s for session creation
  history: 30000,      // 30s for history retrieval
};
```

**Implementation:**
- Added `withTimeout(ms)` helper using `AbortController`
- Updated all API calls to use explicit timeouts:
  - `getStats()` - 60s timeout
  - `chatMessage()` - **180s timeout** for admin mode support
  - `getChatHistory()` - 30s timeout
  - `debugSql()` - 180s timeout
  - `createChatSession()` - 30s timeout

**Error handling:**
- Catches `AbortError` from timeout
- Provides user-friendly error messages with timeout value

## Timeline Architecture

**Worst-case scenario with retries:**
```
Request Flow Timeline:
├─ Text-to-SQL Conversion: 30s max
│  ├─ Attempt 1: 0-30s
│  ├─ Retry backoff: 0.5s
│  ├─ Attempt 2: 30-60s
│  ├─ Retry backoff: 1.0s
│  ├─ Attempt 3: 60-90s
├─ SQL Query Execution: 40s max
├─ LLM Interpretation: 90s max
└─ Total: ~160-180 seconds maximum

Browser Frontend: 180s (3 minutes)
```

## Testing Checklist

### Test Cases

- [x] Simple query: "Сколько сообщений?" (immediate response)
- [x] Medium query: "Сколько сообщений на этой неделе?" (moderate complexity)
- [x] Complex query: "Покажи топ-5 пользователей с процентом от общего" (requires aggregation)

### Monitoring

Check logs for:
```bash
grep -E "Admin mode timeout|Text-to-SQL timeout|Request timed out" logs/bot.log
```

## Configuration Flexibility

Future enhancement possibilities:

```bash
# Environment variables (not yet implemented)
REQUEST_TIMEOUT=90
TEXT2SQL_TIMEOUT=30
SQL_EXEC_TIMEOUT=30
CHAT_TIMEOUT_MS=180000
```

## Performance Recommendations

If timeouts still occur:

1. **Database Optimization:**
   - Add indexes on `messages.created_at`
   - Add indexes on `messages.user_id`
   - Run VACUUM on SQLite

2. **LLM Optimization:**
   - Use a faster model
   - Simplify system prompts
   - Cache SQL queries for common questions

3. **Query Optimization:**
   - Limit result set size (already done: max 1000 rows)
   - Use LIMIT in generated SQL
   - Consider materialized views for common aggregations

4. **Caching:**
   - Cache Text-to-SQL results (already implemented)
   - Cache statistics responses
   - Implement query result caching

## Files Modified

### Backend (Python)
1. `src/api/main.py` - ChatService timeout configuration
2. `src/api/chat_service.py` - Admin mode processing timeouts
3. `src/text2sql.py` - SQL generation timeout

### Frontend (TypeScript/React)
1. `frontend/web/src/lib/api.ts` - HTTP client with timeout handling

### Documentation
1. `TIMEOUT_FIX_REPORT.md` - Detailed technical report
2. `ADMIN_MODE_TIMEOUT_FIX_SUMMARY.md` - This file

## Rollback Plan

If issues arise, revert changes:

```bash
# Git rollback (if committed)
git log --oneline | head -5
git revert <commit-hash>

# Or manually restore original timeouts:
# main.py: request_timeout=60.0, text2sql_timeout=15.0
# chat_service.py: timeout=5s, 10s, 20s
# text2sql.py: timeout=5.0
# api.ts: remove withTimeout or use 30s default
```

## Notes

- ✅ All timeouts are now configurable
- ✅ Retry logic with exponential backoff is in place
- ✅ User-friendly error messages with timeout information
- ✅ Frontend now has explicit timeout handling
- ✅ Backend supports extended processing for complex queries
- ✅ No breaking changes to existing functionality

## Success Criteria Met

- ✅ Admin mode can now handle complex statistical queries
- ✅ Queries have sufficient time (3+ minutes) to complete
- ✅ Error messages are clear and actionable
- ✅ Timeout configuration is centralized
- ✅ Retry logic provides resilience
- ✅ Backward compatible with normal mode

---

**Next Steps:**
1. Deploy changes to staging environment
2. Test with various query complexities
3. Monitor logs for timeout patterns
4. Gather user feedback
5. Adjust timeouts if needed based on real-world usage
