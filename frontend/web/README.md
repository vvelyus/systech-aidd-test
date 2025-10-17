# SysTech AIDD - Frontend

Веб-интерфейс для системы аналитики диалогов Telegram-бота.

## Технологический стек

- **Framework**: Next.js 15+ (App Router)
- **Язык**: TypeScript (strict mode)
- **UI Library**: shadcn/ui
- **Styling**: Tailwind CSS 4.0
- **Пакетный менеджер**: pnpm

## Требования

- Node.js 18.0 или выше
- pnpm 9.0 или выше

## Быстрый старт

### 1. Установка зависимостей

```bash
# Из корня проекта
make frontend-install

# Или напрямую
cd frontend/web
pnpm install
```

### 2. Настройка переменных окружения

Скопируйте `.env.example` в `.env.local` и настройте:

```bash
cp .env.example .env.local
```

По умолчанию API доступен по адресу `http://localhost:8000`.

### 3. Запуск dev server

**Терминал 1 - Backend API:**
```bash
make api-run
```

**Терминал 2 - Frontend:**
```bash
make frontend-dev
# Или: cd frontend/web && pnpm dev
```

Frontend будет доступен по адресу: http://localhost:3000

## Доступные команды

### Через Makefile (из корня проекта)

```bash
make frontend-install     # Установить зависимости
make frontend-dev         # Запустить dev server
make frontend-build       # Production build
make frontend-lint        # Запустить ESLint
make frontend-type-check  # Проверка типов TypeScript
```

### Напрямую через pnpm

```bash
cd frontend/web

pnpm dev          # Dev server (http://localhost:3000)
pnpm build        # Production build
pnpm start        # Запустить production build
pnpm lint         # ESLint проверка
pnpm tsc --noEmit # TypeScript type check
```

## Структура проекта

```
frontend/web/
├── src/
│   ├── app/              # Next.js App Router
│   │   ├── layout.tsx    # Root layout
│   │   ├── page.tsx      # Главная страница (редирект)
│   │   └── dashboard/    # Страница дашборда
│   │       └── page.tsx
│   ├── components/       # React компоненты
│   │   ├── ui/           # shadcn/ui компоненты
│   │   └── dashboard/    # Компоненты дашборда
│   ├── lib/              # Утилиты
│   │   ├── api.ts        # API client
│   │   └── utils.ts      # Вспомогательные функции
│   └── types/            # TypeScript типы
│       └── stats.ts      # Типы для API статистики
├── public/               # Статические файлы
├── .env.local            # Локальные переменные окружения (не в git)
├── .env.example          # Пример конфигурации
├── components.json       # Конфигурация shadcn/ui
├── eslint.config.mjs     # ESLint конфигурация
├── next.config.js        # Next.js конфигурация
├── tailwind.config.ts    # Tailwind конфигурация
├── tsconfig.json         # TypeScript конфигурация
└── package.json          # Зависимости и скрипты
```

## Переменные окружения

### `.env.local`

```bash
# URL Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Интеграция с API

API Client находится в `src/lib/api.ts` и предоставляет функции для работы с backend:

```typescript
import { getStats } from "@/lib/api";
import { Period } from "@/types/stats";

// Получить статистику за указанный период
const stats = await getStats("week"); // "day" | "week" | "month"
```

### Структура ответа API

См. подробную документацию в `frontend/doc/api-contract.md`.

## Разработка

### Добавление новых компонентов shadcn/ui

```bash
cd frontend/web
pnpm dlx shadcn@latest add [component-name]
```

Доступные компоненты: https://ui.shadcn.com/docs/components

### TypeScript strict mode

Проект использует strict TypeScript конфигурацию:
- `strict: true`
- `noUncheckedIndexedAccess: true`
- `noUnusedLocals: true`
- `noUnusedParameters: true`

### Code Style

- **ESLint**: Автоматическая проверка при сохранении
- **Prettier**: Форматирование кода
- Используйте `@/` для импортов из `src/`

### Пример компонента

```typescript
// src/components/example.tsx
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export function Example() {
  return (
    <Card>
      <Button>Click me</Button>
    </Card>
  );
}
```

## Проверка качества кода

### TypeScript

```bash
make frontend-type-check
# Или: cd frontend/web && pnpm tsc --noEmit
```

### ESLint

```bash
make frontend-lint
# Или: cd frontend/web && pnpm lint
```

### Production Build

```bash
make frontend-build
# Или: cd frontend/web && pnpm build
```

## Troubleshooting

### Port 3000 занят

```bash
# Укажите другой порт
PORT=3001 pnpm dev
```

### API недоступен

1. Убедитесь что backend запущен: `make api-run`
2. Проверьте `NEXT_PUBLIC_API_URL` в `.env.local`
3. Откройте http://localhost:8000/docs для проверки API

### Ошибки TypeScript

```bash
# Очистите .next и пересоберите
rm -rf .next
pnpm dev
```

## Дополнительная информация

- [Next.js Documentation](https://nextjs.org/docs)
- [shadcn/ui Documentation](https://ui.shadcn.com)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [API Contract](../doc/api-contract.md)
- [Frontend Roadmap](../doc/frontend-roadmap.md)
