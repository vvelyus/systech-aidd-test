# Frontend Technical Debt Roadmap

**Статус:** 📋 Backlog
**Дата создания:** 18 октября 2025
**Приоритет:** Medium
**Оценка времени:** 30-40 минут

---

## 🎯 Цель

Устранить ошибки TypeScript/ESLint в frontend приложении для успешной сборки production билда.

---

## 📊 Текущее состояние

### ✅ Что работает:
- Все необходимые `lib` файлы существуют и реализованы:
  - ✅ `lib/utils.ts` - функция `cn` для Tailwind CSS
  - ✅ `lib/api.ts` - API клиент с поддержкой streaming
  - ✅ `lib/chat-store.ts` - Zustand store для чата
- Все компоненты UI созданы
- Все типы определены в `types/`
- Зависимости установлены (`clsx`, `tailwind-merge`, `zustand`, `uuid`)

### ❌ Что не работает:
- `npm run build` падает с ошибками TypeScript и ESLint
- 7 файлов требуют исправления
- Отсутствуют типы для пакета `uuid`

---

## 🐛 Список проблем

### 1. Отсутствующие типы для зависимостей

**Файл:** `src/hooks/use-chat.ts:11`

**Проблема:**
```
Could not find a declaration file for module 'uuid'
```

**Решение:**
```bash
cd frontend/web
npm install --save-dev @types/uuid
```

**Приоритет:** 🔴 Critical
**Оценка:** 2 минуты

---

### 2. Неиспользуемые импорты

#### 2.1 chat-input.tsx

**Файл:** `src/components/chat/chat-input.tsx:5`

**Проблема:**
```typescript
import { Send, Loader2, HelpCircle } from "lucide-react";
// 'HelpCircle' is declared but its value is never read
```

**Решение:**
```typescript
import { Send, Loader2 } from "lucide-react";
```

**Приоритет:** 🟡 Medium
**Оценка:** 1 минута

---

#### 2.2 chat-window.tsx

**Файл:** `src/components/chat/chat-window.tsx:10`

**Проблема:**
```typescript
import { Loader2 } from "lucide-react";
// 'Loader2' is defined but never used
```

**Решение:**
```typescript
// Удалить импорт Loader2
import { SuggestedQuestions } from "./suggested-questions";
import { LoadingSkeleton } from "./loading-skeleton";
```

**Приоритет:** 🟡 Medium
**Оценка:** 1 минута

---

#### 2.3 floating-chat-button.tsx

**Файл:** `src/components/chat/floating-chat-button.tsx:5`

**Проблема:**
```typescript
import { useState } from "react";
// 'useState' is defined but never used
```

**Решение:**
```typescript
import { Button } from "@/components/ui/button";
import { MessageCircle, X } from "lucide-react";
// Удалить импорт useState
```

**Приоритет:** 🟡 Medium
**Оценка:** 1 минута

---

#### 2.4 chat-message.tsx

**Файл:** `src/components/chat/chat-message.tsx:6-7`

**Проблема:**
```typescript
import { MessageRole, ChatMessage as ChatMessageType } from "@/types/chat";
import { Card } from "@/components/ui/card";
// 'MessageRole' is defined but never used
// 'Card' is defined but never used
```

**Решение:**
```typescript
import { ChatMessage as ChatMessageType } from "@/types/chat";
// Удалить импорт Card
```

**Приоритет:** 🟡 Medium
**Оценка:** 1 минута

---

#### 2.5 api.ts

**Файл:** `src/lib/api.ts:6`

**Проблема:**
```typescript
import type {
  ChatMode,
  ChatMessage,
  TextToSqlResponse,
  ChatHistory,  // <-- не используется
} from "@/types/chat";
```

**Решение:**
```typescript
import type {
  ChatMode,
  ChatMessage,
  TextToSqlResponse,
} from "@/types/chat";
```

**Приоритет:** 🟡 Medium
**Оценка:** 1 минута

---

### 3. Неиспользуемые переменные

#### 3.1 api.ts - timeoutId

**Файл:** `src/lib/api.ts:25`

**Проблема:**
```typescript
function withTimeout(timeoutMs: number): AbortSignal {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
  // 'timeoutId' is assigned a value but never used
  return controller.signal;
}
```

**Решение:**
```typescript
function withTimeout(timeoutMs: number): AbortSignal {
  const controller = new AbortController();
  setTimeout(() => controller.abort(), timeoutMs);
  return controller.signal;
}
```

**Приоритет:** 🟡 Medium
**Оценка:** 1 минута

---

#### 3.2 api.ts - catch parameter

**Файл:** `src/lib/api.ts:134`

**Проблема:**
```typescript
try {
  const json = JSON.parse(data);
  if (json.content) {
    yield json.content;
  }
} catch (e) {  // <-- 'e' is defined but never used
  // Ignore parsing errors
}
```

**Решение:**
```typescript
try {
  const json = JSON.parse(data);
  if (json.content) {
    yield json.content;
  }
} catch {
  // Ignore parsing errors
}
```

**Приоритет:** 🟡 Medium
**Оценка:** 1 минута

---

### 4. React Hooks - exhaustive-deps

**Файл:** `src/components/chat/chat-container.tsx:36`

**Проблема:**
```typescript
useEffect(() => {
  if (initialMode && initialMode !== currentMode) {
    switchMode(initialMode);
  }
}, [initialMode]); // Missing dependencies: 'currentMode' and 'switchMode'
```

**Решение:**
```typescript
useEffect(() => {
  if (initialMode && initialMode !== currentMode) {
    switchMode(initialMode);
  }
  // eslint-disable-next-line react-hooks/exhaustive-deps
}, [initialMode]); // Only run once on mount
```

**Обоснование:** Хук должен запускаться только один раз при монтировании для установки начального режима. Добавление `currentMode` и `switchMode` в зависимости приведет к бесконечным перерендерам.

**Приоритет:** 🟡 Medium
**Оценка:** 2 минуты

---

### 5. TypeScript - RegExp флаги (ES2018)

**Файл:** `src/components/chat/chat-message.tsx:22`

**Проблема:**
```typescript
const sqlMatch = useMemo(() => {
  return message.content.match(/SQL Query:\s*(.+?)(?:\n\n|$)/s);
  // This regular expression flag 's' is only available when targeting 'es2018' or later
}, [message.content]);
```

**Решение:**
```typescript
const sqlMatch = useMemo(() => {
  return message.content.match(/SQL Query:\s*([\s\S]+?)(?:\n\n|$)/);
  // Используем [\s\S] вместо флага /s для совместимости
}, [message.content]);
```

**Также исправить на строке 72:**
```typescript
const cleanContent = content.replace(/SQL Query:\s*[\s\S]+?(?:\n\n|$)/, "").trim();
```

**Приоритет:** 🔴 Critical
**Оценка:** 3 минуты

---

### 6. ReactMarkdown - TypeScript типы

**Файл:** `src/components/chat/chat-message.tsx:97, 118`

**Проблема:**
```typescript
<ReactMarkdown
  className="prose prose-sm max-w-none dark:prose-invert"
  components={{
    code: ({inline, children, ...props}) => (  // Property 'inline' does not exist
      <code className={inline ? "..." : "..."} {...props}>
        {children}
      </code>
    ),
  }}
>
```

**Решение (упрощенный вариант):**
```typescript
<ReactMarkdown
  className="prose prose-sm max-w-none dark:prose-invert"
>
  {content}
</ReactMarkdown>
```

**Альтернативное решение (с кастомизацией):**
Установить `@types/react-markdown` или использовать правильные типы из `react-markdown`.

**Приоритет:** 🟡 Medium
**Оценка:** 5 минут

---

### 7. TypeScript - undefined checks

**Файл:** `src/components/dashboard/activity-chart.tsx:45`

**Проблема:**
```typescript
const CustomDot = (props: any) => {
  const { cx, cy, payload, dataKey } = props
  const value = payload[dataKey]

  return (
    <g>
      <circle cx={cx} cy={cy} r={4} />
      <text x={cx} y={cy - 12}>  {/* 'cy' is possibly 'undefined' */}
        {value}
      </text>
    </g>
  )
}
```

**Решение:**
```typescript
interface CustomDotProps {
  cx?: number;
  cy?: number;
  payload?: TimelineData;
  dataKey?: keyof TimelineData;
}

const CustomDot = (props: CustomDotProps) => {
  const { cx, cy, payload, dataKey } = props
  const value = dataKey && payload ? payload[dataKey] : 0

  if (!cx || !cy) return null;  // Guard clause

  return (
    <g>
      <circle cx={cx} cy={cy} r={4} fill={dataKey === "user_messages" ? "#3b82f6" : "#10b981"} />
      <text
        x={cx}
        y={cy - 12}
        textAnchor="middle"
        fill={dataKey === "user_messages" ? "#3b82f6" : "#10b981"}
        fontSize="12"
        fontWeight="bold"
      >
        {value}
      </text>
    </g>
  )
}
```

**Приоритет:** 🔴 Critical
**Оценка:** 5 минут

---

### 8. TypeScript - any types

**Файл:** `src/components/dashboard/activity-chart.tsx:29`

**Проблема:**
```typescript
const CustomDot = (props: any) => {  // Unexpected any
```

**Решение:** См. пункт 7 выше

**Приоритет:** 🟡 Medium
**Оценка:** включено в пункт 7

---

## 📋 План исправления (Checklist)

### Подготовка (5 минут)
- [ ] Создать ветку: `git checkout -b fix/frontend-typescript-errors`
- [ ] Перейти в директорию: `cd frontend/web`
- [ ] Установить типы: `npm install --save-dev @types/uuid`

### Исправление импортов (5 минут)
- [ ] `chat-input.tsx` - удалить `HelpCircle`
- [ ] `chat-window.tsx` - удалить `Loader2`
- [ ] `floating-chat-button.tsx` - удалить `useState`
- [ ] `chat-message.tsx` - удалить `MessageRole` и `Card`
- [ ] `api.ts` - удалить `ChatHistory`

### Исправление переменных (3 минуты)
- [ ] `api.ts` - убрать `timeoutId` (строка 25)
- [ ] `api.ts` - убрать параметр `e` в catch (строка 134)

### Исправление React hooks (2 минуты)
- [ ] `chat-container.tsx` - добавить eslint-disable для useEffect

### Исправление регулярных выражений (3 минуты)
- [ ] `chat-message.tsx` - заменить флаг `/s` на `[\s\S]` (строки 22, 72)

### Исправление ReactMarkdown (5 минут)
- [ ] `chat-message.tsx` - упростить компоненты (строки 94-108, 115-130)

### Исправление типов (5 минут)
- [ ] `activity-chart.tsx` - добавить интерфейс `CustomDotProps`
- [ ] `activity-chart.tsx` - добавить guard clause для `cx` и `cy`

### Проверка (5 минут)
- [ ] Запустить сборку: `npm run build`
- [ ] Проверить отсутствие ошибок
- [ ] Запустить type-check: `npm run type-check`
- [ ] Запустить линтер: `npm run lint`

### Финализация (5 минут)
- [ ] Создать коммит: `git add .`
- [ ] Коммит: `git commit -m "fix(frontend): Resolve TypeScript and ESLint errors"`
- [ ] Push: `git push origin fix/frontend-typescript-errors`
- [ ] Создать PR в GitHub
- [ ] Merge после проверки

---

## 🎯 Критерии успеха (Definition of Done)

- ✅ `npm run build` завершается успешно без ошибок
- ✅ `npm run type-check` не выдает ошибок TypeScript
- ✅ `npm run lint` не выдает критических ошибок ESLint
- ✅ Все UI компоненты работают корректно
- ✅ Frontend доступен на `http://localhost:3000`
- ✅ Docker образ frontend собирается без ошибок
- ✅ Изменения закоммичены и merge в main

---

## 🔄 Зависимости

### Блокирует:
- Публикацию frontend образа в GHCR (Sprint D1)
- Deploy frontend на production сервер (Sprint D2)

### Не блокирует:
- ✅ Bot работает независимо
- ✅ API работает независимо
- ✅ Основной функционал через Telegram

---

## 📊 Оценка времени

| Этап | Время |
|------|-------|
| Подготовка | 5 мин |
| Исправление импортов | 5 мин |
| Исправление переменных | 3 мин |
| React hooks | 2 мин |
| RegExp | 3 мин |
| ReactMarkdown | 5 мин |
| TypeScript типы | 5 мин |
| Проверка и тестирование | 5 мин |
| Финализация | 5 мин |
| **ИТОГО** | **38 минут** |

---

## 💡 Примечания

### Почему не успели за 15 минут:

1. **Неожиданные проблемы:**
   - Файлы `lib/*.ts` уже существовали (проблема была не в них)
   - Реальная проблема - ошибки TypeScript/ESLint
   - Потребовалась установка дополнительных типов

2. **Сложность исправлений:**
   - 7 файлов требуют изменений
   - Множество мелких ошибок вместо одной большой
   - Каждое исправление требует пересборки для проверки

3. **Ограничения времени:**
   - PowerShell не поддерживает `&&` (дополнительное время на отладку)
   - Сборка Next.js занимает ~15-20 секунд каждый раз
   - Итеративный процесс: исправить → собрать → проверить → повторить

### Рекомендации для будущего:

1. **Настроить ESLint в IDE** - видеть ошибки сразу
2. **Использовать incremental сборку** - быстрее проверять изменения
3. **Настроить pre-commit hooks** - предотвращать коммиты с ошибками
4. **Добавить CI check** - автоматическая проверка при PR

---

## 🔗 Связанные документы

- [FRONTEND_FIX_BACKLOG.md](../../FRONTEND_FIX_BACKLOG.md) - Исходный backlog
- [Sprint D1 Plan](../../.cursor/plans/sprint-d1-build-publish-f14791f5.plan.md) - План спринта
- [DevOps Roadmap](../../devops/doc/devops-roadmap.md) - Общий план DevOps

---

## 📅 История изменений

| Дата | Событие |
|------|---------|
| 2025-10-18 | Roadmap создан на основе попытки исправления |
| 2025-10-18 | Все изменения откачены через `git restore` |
| - | Ожидание: исправление в отдельной ветке |

---

**Статус:** 📋 Ready to implement
**Следующий шаг:** Создать ветку и выполнить checklist
