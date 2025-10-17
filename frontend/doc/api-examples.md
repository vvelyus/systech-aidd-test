# Stats API - Практические примеры

Этот документ содержит практические примеры использования Stats API на различных языках и инструментах.

## cURL (Command Line)

### Базовые примеры

```bash
# Health check
curl http://localhost:8000/

# Получить статистику за неделю (по умолчанию)
curl http://localhost:8000/stats

# Получить статистику за день
curl http://localhost:8000/stats?period=day

# Получить статистику за месяц
curl http://localhost:8000/stats?period=month

# С форматированием JSON
curl http://localhost:8000/stats?period=week | python -m json.tool

# Только определенные поля (используя jq)
curl http://localhost:8000/stats | jq '.summary'
```

### Сохранение ответа в файл

```bash
# Сохранить полный ответ
curl http://localhost:8000/stats?period=month -o stats.json

# Сохранить только summary
curl http://localhost:8000/stats | jq '.summary' > summary.json
```

---

## JavaScript (Browser / Node.js)

### Fetch API (Browser)

```javascript
// Базовый запрос
async function getStats(period = 'week') {
  try {
    const response = await fetch(`http://localhost:8000/stats?period=${period}`);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Ошибка при получении статистики:', error);
    throw error;
  }
}

// Использование
getStats('week')
  .then(stats => {
    console.log('Total messages:', stats.summary.total_messages);
    console.log('Active users:', stats.summary.active_users);
    console.log('Timeline points:', stats.activity_timeline.length);
  });
```

### С обработкой разных периодов

```javascript
async function fetchStatsForAllPeriods() {
  const periods = ['day', 'week', 'month'];
  const results = {};

  for (const period of periods) {
    const response = await fetch(`http://localhost:8000/stats?period=${period}`);
    results[period] = await response.json();
  }

  return results;
}

// Использование
fetchStatsForAllPeriods().then(allStats => {
  console.log('Day stats:', allStats.day.summary);
  console.log('Week stats:', allStats.week.summary);
  console.log('Month stats:', allStats.month.summary);
});
```

### Axios (Node.js)

```javascript
const axios = require('axios');

const API_BASE_URL = 'http://localhost:8000';

// Базовый запрос
async function getStats(period = 'week') {
  try {
    const response = await axios.get(`${API_BASE_URL}/stats`, {
      params: { period }
    });
    return response.data;
  } catch (error) {
    console.error('Ошибка:', error.message);
    throw error;
  }
}

// С таймаутом
async function getStatsWithTimeout(period = 'week', timeout = 5000) {
  try {
    const response = await axios.get(`${API_BASE_URL}/stats`, {
      params: { period },
      timeout: timeout
    });
    return response.data;
  } catch (error) {
    if (error.code === 'ECONNABORTED') {
      console.error('Запрос превысил таймаут');
    }
    throw error;
  }
}

// Использование
getStats('month').then(stats => {
  console.log('Summary:', stats.summary);
  console.log('Top users:', stats.top_users);
});
```

---

## Python

### Requests

```python
import requests

API_BASE_URL = "http://localhost:8000"

def get_stats(period="week"):
    """Получить статистику за указанный период."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/stats",
            params={"period": period},
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе: {e}")
        raise

# Использование
stats = get_stats("week")
print(f"Total messages: {stats['summary']['total_messages']}")
print(f"Active users: {stats['summary']['active_users']}")
print(f"Timeline length: {len(stats['activity_timeline'])}")
```

### С типизацией (Pydantic)

```python
from typing import Optional
from pydantic import BaseModel
import requests

class SummaryStats(BaseModel):
    total_messages: int
    total_messages_change: float
    active_users: int
    active_users_change: float
    avg_dialog_length: float
    avg_dialog_length_change: float
    messages_per_day: float
    messages_per_day_change: float

class StatsResponse(BaseModel):
    summary: SummaryStats
    activity_timeline: list
    top_users: list
    recent_dialogs: list

def get_stats_typed(period: str = "week") -> StatsResponse:
    """Получить статистику с типизацией."""
    response = requests.get(
        "http://localhost:8000/stats",
        params={"period": period}
    )
    response.raise_for_status()
    return StatsResponse(**response.json())

# Использование
stats = get_stats_typed("month")
print(f"Type: {type(stats)}")
print(f"Total messages: {stats.summary.total_messages}")
```

### Async с httpx

```python
import httpx
import asyncio

async def get_stats_async(period: str = "week") -> dict:
    """Асинхронное получение статистики."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/stats",
            params={"period": period},
            timeout=5.0
        )
        response.raise_for_status()
        return response.json()

# Использование
async def main():
    stats = await get_stats_async("week")
    print(f"Active users: {stats['summary']['active_users']}")

asyncio.run(main())
```

### Параллельный запрос нескольких периодов

```python
import asyncio
import httpx

async def fetch_all_periods():
    """Получить статистику для всех периодов параллельно."""
    periods = ["day", "week", "month"]

    async with httpx.AsyncClient() as client:
        tasks = [
            client.get(
                "http://localhost:8000/stats",
                params={"period": period}
            )
            for period in periods
        ]

        responses = await asyncio.gather(*tasks)

        return {
            period: response.json()
            for period, response in zip(periods, responses)
        }

# Использование
async def main():
    all_stats = await fetch_all_periods()

    for period, stats in all_stats.items():
        print(f"{period.upper()}: {stats['summary']['total_messages']} messages")

asyncio.run(main())
```

---

## React Example

```javascript
import React, { useState, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:8000';

function StatsViewer() {
  const [stats, setStats] = useState(null);
  const [period, setPeriod] = useState('week');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchStats();
  }, [period]);

  const fetchStats = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/stats?period=${period}`);

      if (!response.ok) {
        throw new Error('Failed to fetch stats');
      }

      const data = await response.json();
      setStats(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!stats) return null;

  return (
    <div>
      <h1>Dashboard Statistics</h1>

      <select value={period} onChange={(e) => setPeriod(e.target.value)}>
        <option value="day">Last Day</option>
        <option value="week">Last Week</option>
        <option value="month">Last Month</option>
      </select>

      <div className="summary">
        <h2>Summary</h2>
        <p>Total Messages: {stats.summary.total_messages}</p>
        <p>Active Users: {stats.summary.active_users}</p>
        <p>Avg Dialog Length: {stats.summary.avg_dialog_length}</p>
      </div>

      <div className="top-users">
        <h2>Top Users</h2>
        <ul>
          {stats.top_users.map(user => (
            <li key={user.user_id}>
              {user.first_name} - {user.message_count} messages
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default StatsViewer;
```

---

## Testing с Postman

### Коллекция запросов

```json
{
  "info": {
    "name": "SysTech AIDD Stats API",
    "description": "API для статистики диалогов"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "url": "http://localhost:8000/"
      }
    },
    {
      "name": "Get Stats - Week",
      "request": {
        "method": "GET",
        "url": {
          "raw": "http://localhost:8000/stats?period=week",
          "query": [
            {
              "key": "period",
              "value": "week"
            }
          ]
        }
      }
    },
    {
      "name": "Get Stats - Day",
      "request": {
        "method": "GET",
        "url": {
          "raw": "http://localhost:8000/stats?period=day",
          "query": [
            {
              "key": "period",
              "value": "day"
            }
          ]
        }
      }
    },
    {
      "name": "Get Stats - Month",
      "request": {
        "method": "GET",
        "url": {
          "raw": "http://localhost:8000/stats?period=month",
          "query": [
            {
              "key": "period",
              "value": "month"
            }
          ]
        }
      }
    }
  ]
}
```

---

## Обработка ошибок

### JavaScript

```javascript
async function getStatsWithErrorHandling(period) {
  try {
    const response = await fetch(`http://localhost:8000/stats?period=${period}`);

    if (!response.ok) {
      if (response.status === 422) {
        throw new Error('Invalid period parameter');
      }
      throw new Error(`HTTP error ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    if (error.name === 'TypeError') {
      console.error('Network error - API server may be down');
    }
    console.error('Error:', error.message);
    throw error;
  }
}
```

### Python

```python
import requests
from requests.exceptions import RequestException, Timeout, HTTPError

def get_stats_safe(period="week"):
    """Безопасное получение статистики с обработкой ошибок."""
    try:
        response = requests.get(
            "http://localhost:8000/stats",
            params={"period": period},
            timeout=5
        )
        response.raise_for_status()
        return response.json()

    except Timeout:
        print("Request timed out")
        return None
    except HTTPError as e:
        if e.response.status_code == 422:
            print(f"Invalid period: {period}")
        else:
            print(f"HTTP error: {e}")
        return None
    except RequestException as e:
        print(f"Request failed: {e}")
        return None
```

---

## Полезные команды

```bash
# Запуск API сервера
make api-run

# Тестирование API
make api-test

# Открыть документацию
# Затем перейти в браузере:
# http://localhost:8000/docs
make api-docs
```

## Связанные документы

- [API Contract](api-contract.md) - Полное описание контракта API
- [Frontend Roadmap](frontend-roadmap.md) - План развития frontend
