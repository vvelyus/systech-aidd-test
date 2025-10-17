# Rate Limit (429) - Решение проблемы

## Проблема

При использовании бота и API получается ошибка:

```
Error code: 429 - {'error': {'message': 'Rate limit exceeded: free-models-per-day. Add 10 credits to. Please try again with a simpler question.'}}
```

### Что это значит?

- **Код 429** - HTTP ошибка "Too Many Requests" (слишком много запросов)
- **`free-models-per-day`** - превышен лимит на количество **бесплатных запросов в день** на OpenRouter.ai
- **Необходимо** - добавить кредиты на счёт OpenRouter либо дождаться следующего дня (лимит сбрасывается в 00:00 UTC)

---

## Решение

### Вариант 1: Добавить кредиты на OpenRouter 💳

1. Перейти на https://openrouter.ai
2. Залогиниться на свой аккаунт
3. Нажать на профиль (верх справа)
4. Выбрать **"Credits"** или **"Billing"**
5. Добавить кредиты (минимум $5-10)
6. После пополнения лимит сразу восстановится

### Вариант 2: Дождаться сброса лимита ⏰

- Суточный лимит сбрасывается каждые 24 часа (в 00:00 UTC)
- Если ошибка произошла сегодня - попробовать завтра

### Вариант 3: Использовать более эффективные запросы 📝

Чтобы не превышать лимит:

**❌ Неэффективно (долгие запросы):**
```
"Проанализируй всю историю чатов за последний год,
сделай детальный отчет по каждому пользователю с
примерами диалогов и статистикой по времени суток"
```

**✅ Эффективно (короткие запросы):**
```
"Сколько всего пользователей?"
"Какие самые активные пользователи за неделю?"
"Средняя длина сообщений?"
```

---

## Улучшения в коде

### 1. Лучшая обработка ошибок (LLMClient)

**Что изменилось:**
- ✅ Добавлен специальный класс `RateLimitExceededError`
- ✅ Диагностика типа лимита (free-daily vs standard)
- ✅ Информативные логи с деталями ошибки
- ✅ **NO RETRY при free-models-per-day** - выбрасывается сразу ✋
- ✅ Retry работает только для других типов лимитов (если они будут)
- ✅ Exponential backoff для других типов ошибок (1s, 2s, 4s, 8s...)

```python
# Новая логика
if is_free_limit:
    # Выбросить СРАЗУ - retry не поможет
    raise RateLimitExceededError(error_msg)
else:
    # Для других лимитов использовать retry
    for attempt in range(max_retries + 1):
        # ... retry логика с backoff
```

### 2. Информативные сообщения для пользователя (ChatService)

**Что изменилось:**
- ✅ Специальная обработка `RateLimitExceededError`
- ✅ Дружественное сообщение об ошибке на русском
- ✅ Рекомендации по решению проблемы
- ✅ **Нет откладывания на retry** - ошибка показывается немедленно

```python
except RateLimitExceededError as e:
    error_message = (
        "🚫 API Rate Limit Exceeded\n\n"
        "The free tier usage limit has been exceeded. "
        "To continue using the service, please:\n"
        "1. Add credits to your OpenRouter account\n"
        "2. Wait until tomorrow (daily limits reset)\n"
        "3. Use a simpler query to reduce processing time\n\n"
        f"Details: {str(e)[:150]}"
    )
    yield error_message
```

---

## Файлы, которые изменились

| Файл | Изменения |
|------|-----------|
| `src/llm_client.py` | ✅ Удален retry при free-models-per-day, выбрасывается сразу |
| `src/api/chat_service.py` | ✅ Специальная обработка rate limit, информативные сообщения |

---

## Как использовать исправления

### Для разработчика

1. Проверить логи в `logs/bot.log` - там будут подробности ошибки:
```
ERROR: Rate limit exceeded: free-models-per-day.
       Add credits or wait until tomorrow (00:00 UTC).
       Error: ...
```

2. При ошибке 429 с free-models-per-day:
```python
# Retry НЕ БУДЕТ происходить
# Будет сразу выброшена RateLimitExceededError
# Пользователь получит информативное сообщение
```

### Для конечного пользователя

Если получена ошибка:

```
🚫 API Rate Limit Exceeded

The free tier usage limit has been exceeded.
To continue using the service, please:
1. Add credits to your OpenRouter account
2. Wait until tomorrow (daily limits reset)
3. Use a simpler query to reduce processing time
```

**Следуйте инструкциям выше (Вариант 1-3)**

---

## OpenRouter Free Tier Лимиты

| Параметр | Значение |
|----------|----------|
| **Бесплатный лимит в день** | ~30-50 запросов (зависит от модели) |
| **Стоимость сверх лимита** | Требуется оплата |
| **Сброс лимита** | Каждый день в 00:00 UTC |
| **Платные модели** | Работают без суточного лимита (платятся за каждый запрос) |

---

## Рекомендуемые действия

### Краткосрочное ✅
1. **Дождаться завтра** - лимит сбросится
2. **Добавить кредиты** - $5 должно хватить на недельное тестирование

### Среднесрочное 🔧
1. Оптимизировать запросы (более короткие)
2. Добавить кэширование часто задаваемых вопросов
3. Использовать mock API для тестирования

### Долгосрочное 📊
1. Рассмотреть другие LLM провайдеры (Anthropic, OpenAI, Google)
2. Реализовать rate limiting на уровне приложения
3. Добавить queue для отложенной обработки

---

## Дополнительная информация

- **OpenRouter Docs**: https://openrouter.ai/docs
- **Rate Limit Details**: https://openrouter.ai/docs#rate-limits
- **Billing Info**: https://openrouter.ai/account/billing/overview
