# Sprint S2 (F2) - Инициализация Frontend проекта

## Цель спринта

Инициализировать современный frontend проект на Next.js с TypeScript, настроить инструменты разработки, создать базовую структуру приложения со страницей дашборда и интеграцией с существующим Mock API.

## Технологический стек

- **Framework**: Next.js 14+ (App Router)
- **Язык**: TypeScript (strict mode)
- **UI Library**: shadcn/ui (дефолтная тема)
- **Styling**: Tailwind CSS
- **Пакетный менеджер**: pnpm
- **Linting**: ESLint + Prettier
- **API Client**: fetch API / axios

## Структура проекта

```
frontend/
├── doc/              # Существующая документация
├── web/              # Next.js приложение (новое)
│   ├── src/
│   │   ├── app/           # App Router
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   └── dashboard/
│   │   │       └── page.tsx
│   │   ├── components/    # React компоненты
│   │   │   └── ui/        # shadcn/ui компоненты
│   │   ├── lib/           # Утилиты
│   │   │   ├── api.ts     # API client
│   │   │   └── utils.ts
│   │   └── types/         # TypeScript types
│   │       └── stats.ts
│   ├── public/
│   ├── .env.local
│   ├── .eslintrc.json
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── package.json
└── README.md
```

## Этапы реализации

### 1. Инициализация Next.js проекта

**Команда:**

```bash
cd frontend
pnpm create next-app@latest web --typescript --tailwind --app --src-dir --import-alias "@/*"
```

**Параметры:**

- TypeScript: Yes
- ESLint: Yes
- Tailwind CSS: Yes
- App Router: Yes
- src/ directory: Yes
- Import alias (@/*): Yes

**Результат**: Базовая структура Next.js проекта в `frontend/web/`

### 2. Настройка shadcn/ui

**Команды:**

```bash
cd frontend/web
pnpm dlx shadcn-ui@latest init
```

**Конфигурация:**

- Style: Default
- Base color: Slate
- CSS variables: Yes

**Установить начальные компоненты:**

```bash
pnpm dlx shadcn-ui@latest add card button
```

**Файлы**: `components.json`, `src/components/ui/card.tsx`, `src/components/ui/button.tsx`

### 3. Настройка TypeScript (strict mode)

**Файл**: `tsconfig.json`

Обновить для strict режима:

```json
{
  "compilerOptions": {
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

### 4. Настройка ESLint и Prettier

**Файл**: `.eslintrc.json`

Добавить правила:

```json
{
  "extends": ["next/core-web-vitals", "next/typescript"],
  "rules": {
    "@typescript-eslint/no-unused-vars": "error",
    "@typescript-eslint/no-explicit-any": "warn"
  }
}
```

**Файл**: `.prettierrc` (создать)

```json
{
  "semi": true,
  "singleQuote": false,
  "tabWidth": 2,
  "trailingComma": "es5"
}
```

### 5. Настройка Environment переменных

**Файл**: `.env.local` (создать)

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Файл**: `.env.example` (создать для документации)

```
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 6. Создание TypeScript типов для API

**Файл**: `src/types/stats.ts`

На основе API контракта (`frontend/doc/api-contract.md`):

```typescript
export type Period = "day" | "week" | "month";

export interface SummaryMetric {
  value: number;
  change_percent: number;
}

export interface Summary {
  total_dialogs: SummaryMetric;
  total_messages: SummaryMetric;
  active_users: SummaryMetric;
  avg_messages_per_dialog: SummaryMetric;
}

export interface TimePoint {
  timestamp: string;
  value: number;
}

export interface TopUser {
  user_id: number;
  username: string | null;
  dialog_count: number;
  message_count: number;
}

export interface RecentDialog {
  dialog_id: number;
  user_id: number;
  username: string | null;
  last_message_at: string;
  message_count: number;
}

export interface StatsResponse {
  summary: Summary;
  activity_timeline: TimePoint[];
  top_users: TopUser[];
  recent_dialogs: RecentDialog[];
}
```

### 7. Создание API Client

**Файл**: `src/lib/api.ts`

```typescript
import { StatsResponse, Period } from "@/types/stats";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function getStats(period: Period = "week"): Promise<StatsResponse> {
  try {
    const response = await fetch(`${API_URL}/stats?period=${period}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
    });

    if (!response.ok) {
      throw new ApiError(
        `API error: ${response.statusText}`,
        response.status
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError("Failed to fetch stats");
  }
}
```

### 8. Создание Root Layout

**Файл**: `src/app/layout.tsx`

```typescript
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin", "cyrillic"] });

export const metadata: Metadata = {
  title: "SysTech AIDD - Dashboard",
  description: "Статистика диалогов Telegram-бота",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ru">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
```

### 9. Создание главной страницы (редирект на дашборд)

**Файл**: `src/app/page.tsx`

```typescript
import { redirect } from "next/navigation";

export default function Home() {
  redirect("/dashboard");
}
```

### 10. Создание страницы Dashboard

**Файл**: `src/app/dashboard/page.tsx`

Создать базовую страницу с:

- Загрузкой данных через API client
- 4 карточки summary метрик
- Заглушки для графика, таблиц топ-пользователей и последних диалогов
- Обработкой состояний loading и error
- Переключателем периода (day/week/month)

Использовать компоненты shadcn/ui (Card, Button).

### 11. Создание базовых UI компонентов

**Компоненты для Dashboard:**

1. `src/components/dashboard/stats-card.tsx` - Карточка метрики
2. `src/components/dashboard/period-selector.tsx` - Переключатель периода
3. `src/components/dashboard/loading-skeleton.tsx` - Скелетон для загрузки
4. `src/components/dashboard/error-message.tsx` - Отображение ошибок

### 12. Обновление команд в Makefile

**Файл**: `Makefile` (добавить секцию)

```makefile
# ============================================================================
# Frontend команды
# ============================================================================

.PHONY: frontend-install frontend-dev frontend-build frontend-lint frontend-type-check frontend-test

frontend-install:
	@echo "📦 Installing frontend dependencies..."
	cd frontend/web && pnpm install

frontend-dev:
	@echo "🚀 Starting frontend dev server..."
	cd frontend/web && pnpm dev

frontend-build:
	@echo "🏗️  Building frontend for production..."
	cd frontend/web && pnpm build

frontend-lint:
	@echo "🔍 Running ESLint..."
	cd frontend/web && pnpm lint

frontend-type-check:
	@echo "🔍 Running TypeScript type check..."
	cd frontend/web && pnpm tsc --noEmit

frontend-test:
	@echo "🧪 Running frontend tests..."
	cd frontend/web && pnpm test
```

### 13. Создание документации

**Файл**: `frontend/web/README.md`

Создать с разделами:

- Требования (Node.js 18+, pnpm)
- Быстрый старт
- Доступные команды
- Структура проекта
- Переменные окружения
- Интеграция с API
- Разработка (как добавлять компоненты)

**Обновить**: `frontend/README.md` - добавить информацию о `web/` директории

### 14. Создание frontend-vision.md

**Файл**: `frontend/doc/frontend-vision.md`

Описать:

- Концепцию пользовательского интерфейса
- Принципы дизайна
- Структуру навигации
- Ключевые экраны (Dashboard, Chat)
- UX требования (отзывчивость, доступность)

### 15. Обновление roadmap и финализация

**Обновить файл**: `frontend/doc/frontend-roadmap.md`

- Обновить статус F2 с ⏳ на ✅
- Добавить ссылку на план спринта в таблицу
- Обновить метрики прогресса (2 из 5 спринтов)
- Указать дату завершения спринта

**Обновить файл**: `frontend/README.md`

- Добавить секцию о `web/` директории
- Обновить команды для запуска frontend

### 16. Проверка всех команд package.json

**Файл**: `frontend/web/package.json`

Проверить что работают все scripts:

```bash
cd frontend/web

# Основные команды
pnpm dev          # Dev server запускается
pnpm build        # Production build успешен
pnpm start        # Production server работает
pnpm lint         # ESLint проходит без ошибок

# Type checking
pnpm tsc --noEmit # TypeScript компиляция без ошибок
```

### 17. Тестирование интеграции с Mock API

**Проверить подключение:**

1. Запустить backend: `make api-run` (Terminal 1)
2. Запустить frontend: `make frontend-dev` (Terminal 2)
3. Открыть http://localhost:3000/dashboard
4. Проверить что данные загружаются
5. Проверить переключение периодов (day/week/month)
6. Проверить обработку ошибок (остановить backend)
7. Проверить состояние loading при загрузке

## Проверка качества

### TypeScript

```bash
cd frontend/web
pnpm tsc --noEmit
```

✅ Должно быть: 0 ошибок

### ESLint

```bash
cd frontend/web
pnpm lint
```

✅ Должно быть: 0 ошибок

### Build

```bash
cd frontend/web
pnpm build
```

✅ Должна пройти успешно

### Dev Server

```bash
# Terminal 1: Backend
make api-run

# Terminal 2: Frontend
make frontend-dev
```

✅ Должно открыться: http://localhost:3000/dashboard

✅ Данные должны загружаться с http://localhost:8000/stats

## Итоговые артефакты

### Новые файлы

- `frontend/web/` - полная структура Next.js проекта
- `frontend/doc/frontend-vision.md` - видение UI
- `frontend/doc/plans/s2-init-plan.md` - план спринта

### Обновленные файлы

- `Makefile` - команды для frontend
- `frontend/README.md` - обновленная документация
- `frontend/doc/frontend-roadmap.md` - статус F2

### Функциональность

- ✅ Работающий Next.js проект
- ✅ Страница Dashboard с реальными данными из API
- ✅ TypeScript strict mode
- ✅ Настроенные линтеры
- ✅ Интеграция с shadcn/ui
- ✅ Полная документация

## Принципы реализации

1. **Modern Stack**: Используем последние версии и best practices
2. **Type Safety**: Strict TypeScript для всех файлов
3. **Code Quality**: ESLint + Prettier с строгими правилами
4. **Component-First**: Модульные переиспользуемые компоненты
5. **API Integration**: Готовая интеграция с Mock API
6. **Documentation**: Полная документация для разработчиков
