# Sprint F3 - Реализация Dashboard статистики диалогов

## Обзор

Реализовать полнофункциональный Dashboard с современным UI согласно референсу shadcn/ui dashboard-01. Добавить sidebar (скрытый по умолчанию), переключатель темы, кнопку GitHub, интерактивные графики и сворачиваемую таблицу данных.

## Задачи (сокращенно)

### 1. Инфраструктура

- Установить: recharts, next-themes, lucide-react
- Добавить shadcn/ui: dropdown-menu, sheet, table, badge, separator
- Обновить package.json с новыми зависимостями

### 2. Настройка тем

- Создать ThemeProvider компонент (`src/components/theme-provider.tsx`)
- Обновить layout.tsx с ThemeProvider и suppressHydrationWarning
- Обновить globals.css с CSS переменными для светлой и темной темы

### 3. Компоненты темы

- Создать ThemeToggle (`src/components/theme-toggle.tsx`) с dropdown меню (Sun, Moon, Monitor)

### 4. Навигация и заголовок

- Создать Sidebar (`src/components/dashboard/sidebar.tsx`) с Sheet компонентом (скрыт по умолчанию)
- Создать Header (`src/components/dashboard/header.tsx`) с GitHub кнопкой и theme toggle

### 5. Графики и таблицы

- Создать ActivityChart (`src/components/dashboard/activity-chart.tsx`) с Recharts Area chart
- Улучшить StatsCard: badge, иконки, описание, крупные значения
- Создать RecentDialogsTable (`src/components/dashboard/recent-dialogs.tsx`) со сворачиванием

### 6. Интеграция

- Обновить dashboard/page.tsx с flex layout, Sidebar, Header, все компоненты
- Проверить работу в темной теме
- Финальная проверка: типизация, responsive, accessibility

### 7. Постспринт

- Актуализировать frontend-roadmap.md (результаты F3)
- Добавить ссылку на sprint-f3-dashboard.plan.md в таблицу
- Обновить метрики (3 из 5 спринтов, 60%)

## Проверка консистентности

**Соответствие требованиям:**

- ✓ Sidebar скрыт по умолчанию (Sheet компонент)
- ✓ GitHub кнопка с иконкой (lucide-react)
- ✓ Таблица скрыта по умолчанию (isExpanded state)
- ✓ Переключение темы (next-themes + useTheme)

**Соответствие frontend-vision.md:**

- ✓ Светлая/темная тема согласно цветовой схеме
- ✓ Компоненты из функциональных требований F1
- ✓ Responsive layout (md: grid-cols-2, lg: grid-cols-4)
- ✓ Loading states и error handling

**Последовательность зависимостей:**

- ✓ Пакеты устанавливаются первыми
- ✓ ThemeProvider перед использованием useTheme
- ✓ Компоненты собираются от простых к сложным
- ✓ Интеграция на финальном этапе

## Файлы к изменению

**Создать:**

- `frontend/web/src/components/theme-provider.tsx`
- `frontend/web/src/components/theme-toggle.tsx`
- `frontend/web/src/components/dashboard/header.tsx`
- `frontend/web/src/components/dashboard/sidebar.tsx`
- `frontend/web/src/components/dashboard/activity-chart.tsx`
- `frontend/web/src/components/dashboard/recent-dialogs.tsx`

**Обновить:**

- `frontend/web/src/app/layout.tsx`
- `frontend/web/src/app/globals.css`
- `frontend/web/src/app/dashboard/page.tsx`
- `frontend/web/src/components/dashboard/stats-card.tsx`
- `frontend/web/package.json`
- `frontend/doc/frontend-roadmap.md`

**Добавить (shadcn CLI):**

- `frontend/web/src/components/ui/dropdown-menu.tsx`
- `frontend/web/src/components/ui/sheet.tsx`
- `frontend/web/src/components/ui/table.tsx`
- `frontend/web/src/components/ui/badge.tsx`
- `frontend/web/src/components/ui/separator.tsx`

## Результат

- Современный Dashboard с темной/светлой темой
- Sidebar навигация (скрытый по умолчанию)
- Интерактивный график активности с Recharts
- Кнопка GitHub с иконкой
- Сворачиваемая таблица последних диалогов
- Полностью responsive дизайн
- Соответствие референсу shadcn/ui dashboard-01

---

*План создан: 2025-10-17*
*Спринт: F3 - Реализация Dashboard статистики диалогов*
