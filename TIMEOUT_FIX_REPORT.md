# Admin Mode Timeout Fix Report

## Problem Identified

The admin mode in the chat application was experiencing "Request timed out (too complex query)" errors when attempting to fetch statistics. The issue was caused by insufficient timeout values for:

1. **Text-to-SQL conversion** - Only 5 seconds
2. **SQL query execution** - Only 10 seconds (internal) wrapped in 20 seconds
3. **LLM response generation** - 60 seconds was sometimes not enough

## Root Cause

When users ask complex questions like "Сколько сообщений было отправлено на этой неделе?" (How many messages were sent this week?), the system needs to:

1. Convert the natural language question to SQL (LLM call)
2. Execute the SQL query against the database
3. Process and format the results
4. Generate an analysis response (another LLM call)

With tight timeouts, any of these steps could timeout, causing the entire request to fail.

## Changes Made

### 1. Updated `src/api/main.py` (ChatService Initialization)

**Before:**
```python
chat_service = ChatService(
    llm_client=_llm_client,
    db_manager=_db_manager,
    logger=_logger,
    request_timeout=60.0,  # Increased from 30s
    text2sql_timeout=15.0,  # Increased from 5s
)
```

**After:**
```python
chat_service = ChatService(
    llm_client=_llm_client,
    db_manager=_db_manager,
    logger=_logger,
    request_timeout=90.0,  # Increased from 60s to 90s for complex queries
    text2sql_timeout=30.0,  # Increased from 5s to 30s for SQL generation
)
```

**Changes:**
- `request_timeout`: 60s → 90s
- `text2sql_timeout`: 15s → 30s

### 2. Updated `src/api/chat_service.py` (_process_admin_mode Method)

**Before:**
```python
# Step 1: Text-to-SQL conversion
text2sql_response = await asyncio.wait_for(
    self.text2sql.convert(message, max_retries=3),
    timeout=self.text2sql_timeout  # Was using fixed 5s value
)

# Step 2: SQL execution
results = await asyncio.wait_for(
    self.text2sql.execute_and_format(
        text2sql_response.sql,
        max_rows=1000,
        timeout=10.0  # Too short
    ),
    timeout=20.0  # Not enough for complex queries
)

# Step 3: LLM interpretation
llm_response = await asyncio.wait_for(
    self.llm_client.get_response(llm_prompt),
    timeout=self.request_timeout  # But was wrapped in 20s before
)
```

**After:**
```python
# Step 1: Text-to-SQL conversion with configurable timeout
text2sql_response = await asyncio.wait_for(
    self.text2sql.convert(message, max_retries=3),
    timeout=self.text2sql_timeout  # Now uses 30s (configurable)
)

# Step 2: SQL execution with increased timeouts
results = await asyncio.wait_for(
    self.text2sql.execute_and_format(
        text2sql_response.sql,
        max_rows=1000,
        timeout=30.0  # Increased from 10s to 30s
    ),
    timeout=40.0  # Increased from 20s to 40s
)

# Step 3: LLM interpretation with full request timeout
llm_response = await asyncio.wait_for(
    self.llm_client.get_response(llm_prompt),
    timeout=self.request_timeout  # Now uses 90s (configurable)
)
```

**Changes:**
- Text-to-SQL conversion: Uses configurable timeout (30s now)
- SQL execution: 10s → 30s internal, 20s → 40s overall
- LLM interpretation: Uses full request timeout (90s)

### 3. Updated `src/text2sql.py` (convert Method)

**Before:**
```python
response = await asyncio.wait_for(
    self.llm_client.get_response(
        f"{system_prompt}\n\nQuestion: {question}"
    ),
    timeout=5.0  # 5 second timeout per LLM call
)
```

**After:**
```python
response = await asyncio.wait_for(
    self.llm_client.get_response(
        f"{system_prompt}\n\nQuestion: {question}"
    ),
    timeout=15.0  # Increased from 5s to 15s for SQL generation
)
```

**Changes:**
- LLM call for SQL generation: 5s → 15s

## Timeout Architecture

The new timeout structure ensures each step has adequate time:

```
Request Flow Timeline (worst case):
├─ Text-to-SQL Conversion: 30s max (with retries: up to 3 attempts, exponential backoff)
├─ SQL Query Execution: 30s max (database query)
├─ SQL Formatting: Minimal (< 1s)
├─ LLM Interpretation: 90s max (response generation)
└─ Total: ~180s max with all retries

Browser Timeout: Should be set to 180+ seconds for admin mode
```

## Testing Recommendations

1. **Test with different query complexities:**
   - Simple: "Сколько сообщений?" (How many messages?)
   - Medium: "Сколько сообщений было отправлено на этой неделе?" (Weekly messages)
   - Complex: "Покажи топ-5 пользователей по количеству сообщений с процентом от общего количества" (Top users with percentages)

2. **Monitor logs for timeout patterns:**
   ```bash
   tail -f logs/bot.log | grep -E "timeout|Timeout|TIMEOUT"
   ```

3. **Check actual response times:**
   - Note the time between request and response
   - Look for "LLM timeout" warnings in logs

## Environment Variables

To customize timeouts without code changes, consider adding:

```bash
# Optional future enhancement
REQUEST_TIMEOUT=90
TEXT2SQL_TIMEOUT=30
SQL_EXEC_TIMEOUT=30
```

## Notes

- The retries with exponential backoff in `_process_admin_mode_with_retry` will handle transient failures
- If timeouts persist, consider:
  1. Optimizing database queries (add indexes)
  2. Simplifying LLM prompts
  3. Caching frequently asked questions
  4. Using a faster LLM model

## Browser Client Configuration

Make sure the browser client has appropriate timeout settings:
- Should wait at least 3 minutes for admin mode requests
- Consider showing a "Processing..." indicator to users
