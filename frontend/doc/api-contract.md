# Chat System API Contract

**Version:** 1.0.0
**Status:** Production Ready
**Base URL:** `http://localhost:8000` (development) | `/api` (production)

---

## Overview

Complete API specification for the AI Chat System with streaming support, Text-to-SQL queries, and session management.

---

## Authentication

Currently no authentication required for development. In production:
- JWT bearer token required in `Authorization` header
- Session tokens managed via cookies

---

## Error Handling

All endpoints return errors in this format:

```json
{
  "detail": "Error description",
  "error_code": "ERROR_CODE",
  "timestamp": "2025-10-17T12:30:45Z"
}
```

### Common HTTP Status Codes
- `200 OK` - Success
- `400 Bad Request` - Invalid parameters
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error
- `504 Gateway Timeout` - LLM/DB timeout

---

## Endpoints

### 1. Send Chat Message (Streaming)

**Endpoint:** `POST /api/chat/message`
**Authentication:** Required
**Stream:** Yes (Server-Sent Events)

#### Request

```json
{
  "session_id": "string (required)",
  "message": "string (required, max 5000 chars)",
  "mode": "normal | admin (default: normal)"
}
```

#### Response - Streaming

Server sends chunks as Server-Sent Events (SSE):

```
data: {"chunk": "Hello"}
data: {"chunk": " "}
data: {"chunk": "world"}
data: {"status": "complete"}
```

#### Examples

**Normal Mode (LLM Assistant):**
```bash
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "sess_abc123",
    "message": "What is Python?",
    "mode": "normal"
  }'
```

**Admin Mode (Text-to-SQL):**
```bash
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "sess_abc123",
    "message": "How many active users?",
    "mode": "admin"
  }'
```

#### Performance Targets
- Response time: < 3 seconds
- First chunk: < 1 second
- Chunk interval: < 100ms

---

### 2. Get Chat History

**Endpoint:** `GET /api/chat/history`
**Authentication:** Required
**Pagination:** Yes

#### Query Parameters

| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| session_id | string | required | - | Session ID |
| limit | integer | 50 | 200 | Number of messages |
| offset | integer | 0 | - | Pagination offset |

#### Response

```json
{
  "items": [
    {
      "id": "msg_123",
      "session_id": "sess_abc123",
      "role": "user",
      "content": "What is Python?",
      "created_at": "2025-10-17T12:30:45Z"
    },
    {
      "id": "msg_124",
      "session_id": "sess_abc123",
      "role": "assistant",
      "content": "Python is a programming language...",
      "created_at": "2025-10-17T12:30:50Z"
    }
  ],
  "total": 42,
  "limit": 50,
  "offset": 0,
  "has_more": false
}
```

#### Example

```bash
curl "http://localhost:8000/api/chat/history?session_id=sess_abc123&limit=50&offset=0"
```

---

### 3. Create Chat Session

**Endpoint:** `POST /api/chat/session`
**Authentication:** Required

#### Request

```json
{
  "user_id": "string (required)"
}
```

#### Response

```json
{
  "session_id": "sess_abc123",
  "user_id": "user_456",
  "created_at": "2025-10-17T12:30:45Z",
  "mode": "normal"
}
```

#### Example

```bash
curl -X POST http://localhost:8000/api/chat/session \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user_456"}'
```

---

### 4. Debug SQL Query

**Endpoint:** `POST /api/chat/debug/sql`
**Authentication:** Required (Admin only)

#### Request

```json
{
  "question": "string (required)",
  "session_id": "string (optional)"
}
```

#### Response

```json
{
  "question": "How many users?",
  "sql": "SELECT COUNT(*) FROM users",
  "explanation": "Counting total users in the database",
  "results": "| count |\n|-------|\n| 42    |",
  "execution_time_ms": 123
}
```

#### Example

```bash
curl -X POST http://localhost:8000/api/chat/debug/sql \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How many active users?"
  }'
```

---

## Rate Limiting

| Endpoint | Rate Limit | Window |
|----------|-----------|--------|
| /api/chat/message | 100 req/min | Per user |
| /api/chat/history | 1000 req/min | Per user |
| /api/chat/session | 10 req/min | Per user |
| /api/chat/debug/sql | 50 req/min | Per user |

**Response Header:** `X-RateLimit-Remaining`

---

## Caching Behavior

### Text-to-SQL Query Cache
- **TTL:** 1 hour
- **Key:** SHA256(question)
- **Scope:** Per system
- **Headers:** `Cache-Control: private, max-age=3600`

### History Cache
- **TTL:** 5 minutes
- **Key:** `{session_id}:{offset}:{limit}`
- **Scope:** Per session

### Disable Cache
```bash
# Add header to bypass cache
-H "Cache-Control: no-cache"
```

---

## Timeout Behavior

### Request Timeouts
- **LLM request:** 30 seconds
- **Text-to-SQL conversion:** 5 seconds
- **SQL execution:** 5 seconds

### Timeout Response
```json
{
  "detail": "Request timeout after 30s. Try a simpler question.",
  "error_code": "REQUEST_TIMEOUT",
  "retry_after": 5
}
```

---

## Streaming Response Format

### Server-Sent Events (SSE)

```
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

data: {"chunk": "Hello"}
data: {"chunk": " "}
data: {"chunk": "world"}
data: {"status": "complete"}
data: {"session_id": "sess_abc123"}
```

### Client-Side Parsing (JavaScript)

```javascript
const eventSource = new EventSource(
  '/api/chat/message?session_id=sess_abc123&message=Hello&mode=normal'
);

let response = '';

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.chunk) {
    response += data.chunk;
    console.log(response);
  }

  if (data.status === 'complete') {
    eventSource.close();
    console.log('Response complete:', response);
  }
};

eventSource.onerror = (error) => {
  console.error('Stream error:', error);
  eventSource.close();
};
```

---

## Data Models

### ChatMessage

```typescript
interface ChatMessage {
  id: string;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: ISO8601DateTime;
  updated_at?: ISO8601DateTime;
}
```

### ChatSession

```typescript
interface ChatSession {
  session_id: string;
  user_id: string;
  mode: 'normal' | 'admin';
  created_at: ISO8601DateTime;
  last_activity: ISO8601DateTime;
}
```

### TextToSqlResponse

```typescript
interface TextToSqlResponse {
  question: string;
  sql: string;
  explanation: string;
  results?: string;
  execution_time_ms: number;
}
```

---

## Mode Specification

### Normal Mode (LLM Assistant)
- **Purpose:** General conversation with AI
- **Temperature:** 0.7 (more creative)
- **System Prompt:** Helpful assistant
- **Supports:** Any question/topic

### Admin Mode (Analytics)
- **Purpose:** SQL queries + data analysis
- **Temperature:** 0.3 (more precise)
- **System Prompt:** SQL expert
- **Supports:** Data-related questions
- **Requires:** Admin permissions

---

## Examples by Language

### Python (requests)

```python
import requests
import json

def send_chat_message(session_id, message, mode='normal'):
    url = 'http://localhost:8000/api/chat/message'
    payload = {
        'session_id': session_id,
        'message': message,
        'mode': mode
    }

    with requests.post(url, json=payload, stream=True) as response:
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode('utf-8').replace('data: ', ''))
                if 'chunk' in data:
                    print(data['chunk'], end='', flush=True)
```

### JavaScript (fetch)

```javascript
async function sendChatMessage(sessionId, message, mode = 'normal') {
  const response = await fetch('/api/chat/message', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId, message, mode })
  });

  const reader = response.body.getReader();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const text = new TextDecoder().decode(value);
    const data = JSON.parse(text.replace('data: ', ''));
    if (data.chunk) console.log(data.chunk);
  }
}
```

---

## Versioning

Current version: **1.0.0**

### Backwards Compatibility
- All changes will be backwards compatible
- Deprecated endpoints will have `X-Deprecated` header
- Migration period: 6 months

---

## Support & Documentation

- **Interactive Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **GitHub Issues:** Report bugs and feature requests

---

**Last Updated:** 2025-10-17
**Status:** ✅ Production Ready
