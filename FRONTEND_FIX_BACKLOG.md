# 🔧 Frontend Fix - Backlog Task

**Статус:** 📋 Backlog (отложено после Sprint D1)  
**Приоритет:** Medium  
**Оценка:** ~30-60 минут

---

## 🐛 Проблема

Frontend контейнер запускается корректно, но приложение не работает из-за отсутствующих файлов библиотеки.

### Ошибки:

```
Module not found: Can't resolve '@/lib/api'
Module not found: Can't resolve '@/lib/utils'
Module not found: Can't resolve '@/lib/chat-store'
```

### Детали:

**Отсутствующие файлы:**
- `frontend/web/src/lib/api.ts` - API клиент для взаимодействия с backend
- `frontend/web/src/lib/utils.ts` - Утилиты (функция `cn` для Tailwind CSS)
- `frontend/web/src/lib/chat-store.ts` - Zustand store для управления состоянием чата

**Где используется:**
- `src/app/dashboard/page.tsx` - импортирует `getStats` из `@/lib/api`
- `src/hooks/use-chat.ts` - импортирует API функции и chat store
- `src/components/ui/*` - все UI компоненты импортируют `cn` из `@/lib/utils`

---

## 📋 Задачи для исправления

### 1. Создать `lib/utils.ts`

```typescript
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

**Зависимости:** `clsx`, `tailwind-merge` (возможно нужно установить)

---

### 2. Создать `lib/api.ts`

Должен содержать:
- `getStats(period: Period): Promise<StatsResponse>` - получение статистики
- `chatMessage(...)` - отправка сообщения в чат
- `getChatHistory(...)` - получение истории чата
- `createChatSession(...)` - создание новой сессии чата

**Базовый URL:** `process.env.NEXT_PUBLIC_API_URL` или `http://localhost:8000`

**Пример структуры:**
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function getStats(period: Period): Promise<StatsResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/stats?period=${period}`);
  if (!response.ok) throw new Error("Failed to fetch stats");
  return response.json();
}

// ... другие функции
```

---

### 3. Создать `lib/chat-store.ts`

Zustand store для управления состоянием чата.

**Требования:**
- Хранить список сообщений
- Текущий режим чата (normal/sql)
- Методы для добавления/очистки сообщений
- ID текущей сессии

**Пример структуры:**
```typescript
import { create } from 'zustand';
import { ChatMessage, ChatMode } from '@/types/chat';

interface ChatStore {
  messages: ChatMessage[];
  mode: ChatMode;
  sessionId: string | null;
  addMessage: (message: ChatMessage) => void;
  clearMessages: () => void;
  setMode: (mode: ChatMode) => void;
  // ... другие методы
}

export const useChatStore = create<ChatStore>((set) => ({
  messages: [],
  mode: 'normal',
  sessionId: null,
  // ... реализация методов
}));
```

---

## 🧪 Проверка после исправления

### 1. Локальная сборка:
```bash
cd frontend/web
npm install  # или pnpm install
npm run dev
```

### 2. Проверить:
- ✅ `http://localhost:3000` открывается без ошибок
- ✅ Dashboard отображается
- ✅ Нет ошибок в консоли браузера (F12)
- ✅ API запросы работают (если API запущен)

### 3. Docker сборка:
```bash
docker-compose build frontend
docker-compose up frontend
```

### 4. Финальная проверка:
```bash
docker-compose -f docker-compose.registry.yml down
# Пересобрать и опубликовать образ через CI/CD
git add .
git commit -m "fix(frontend): Add missing lib files (api, utils, chat-store)"
git push origin main
# Дождаться сборки в GitHub Actions
# Запустить из registry
docker-compose -f docker-compose.registry.yml up -d
```

---

## 📝 Дополнительные задачи (опционально)

### Проверить зависимости:

```bash
cd frontend/web
# Убедиться что установлены:
npm list clsx tailwind-merge zustand
# Если нет - установить:
npm install clsx tailwind-merge zustand
```

### Проверить types:

Убедиться что типы определены в:
- `src/types/chat.ts` (ChatMessage, ChatMode)
- `src/types/stats.ts` (Period, StatsResponse)

Если отсутствуют - создать.

---

## 🎯 Критерии завершения

- [ ] Создан `lib/utils.ts` с функцией `cn`
- [ ] Создан `lib/api.ts` с API функциями
- [ ] Создан `lib/chat-store.ts` с Zustand store
- [ ] Frontend запускается локально без ошибок
- [ ] Docker образ собирается без ошибок
- [ ] `http://localhost:3000` открывается и отображает UI
- [ ] Нет ошибок в консоли браузера
- [ ] Изменения закоммичены и опубликованы в GHCR

---

## 📎 Связанные задачи

- Sprint D1: Build & Publish ✅ (завершен)
- Sprint D2: Deploy to Server 📋 (следующий)
- Frontend Fix 📋 (эта задача)

---

## 💡 Примечание

Эта задача **не блокирует Sprint D2**, так как:
- Bot и API полностью функциональны
- Frontend - это опциональный веб-интерфейс для статистики
- Основной функционал работает через Telegram бота

Frontend можно исправить **после** deployment на сервер.

---

**Создано:** 18 октября 2025  
**Статус:** 📋 Backlog  
**Блокирует:** Нет  
**Приоритет:** Medium

