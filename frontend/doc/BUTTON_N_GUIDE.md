# Кнопка "N" - Полное руководство 🎯

## Что это?

Кнопка **"N"** (обычно в чёрном круге внизу экрана) - это **горячая клавиша для создания нового элемента** (New). На скриншоте видно, что она открывает меню с опциями:

```
┌──────────────────────────────┐
│ Route          Static        │
│ Turbopack      Enabled       │
│ Route Info                 > │
│ Preferences              ⚙️  │
└──────────────────────────────┘
    ↑
    └─ Меню открывается по нажатию "N"
```

---

## 📚 Примеры использования

### Пример 1: Диалоговое приложение (в нашем контексте)

Кнопка **"N"** должна открывать меню для создания:
- ✅ Нового диалога
- ✅ Новой группы
- ✅ Новой заметки
- ✅ Нового контакта

```typescript
// Когда пользователь нажимает N:
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'n' || e.key === 'N') {
    e.preventDefault()
    setShowNewMenu(!showNewMenu)  // Открыть меню
  }
}
```

### Пример 2: В нашем Dashboard

Кнопка "N" могла бы:
- 🔹 Создать новый период для анализа
- 🔹 Создать новый отчет
- 🔹 Создать новый фильтр
- 🔹 Создать новое событие

---

## 💻 Как реализовать кнопку "N"

### Шаг 1: Создать компонент меню

```typescript
// src/components/ui/quick-action-menu.tsx
"use client"

import React, { useState, useEffect } from "react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"

interface QuickActionMenuProps {
  onNewDialog?: () => void
  onNewGroup?: () => void
  onNewNote?: () => void
}

export function QuickActionMenu({
  onNewDialog,
  onNewGroup,
  onNewNote,
}: QuickActionMenuProps) {
  const [open, setOpen] = useState(false)

  // Прослушиваем клавишу N
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Проверяем, что пользователь не печатает в input
      if (
        e.key === 'n' &&
        e.target instanceof HTMLInputElement === false &&
        e.target instanceof HTMLTextAreaElement === false
      ) {
        e.preventDefault()
        setOpen(!open)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [open])

  return (
    <DropdownMenu open={open} onOpenChange={setOpen}>
      <DropdownMenuTrigger asChild>
        <Button
          variant="default"
          size="icon"
          className="fixed bottom-6 left-6 rounded-full w-12 h-12 shadow-lg"
          title="N - Создать новое (горячая клавиша)"
        >
          <Plus className="h-6 w-6" />
          <span className="absolute -top-1 -right-1 bg-white text-black text-xs rounded-full w-5 h-5 flex items-center justify-center font-bold">
            N
          </span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent side="right" align="end">
        <DropdownMenuItem onClick={() => { onNewDialog?.(); setOpen(false) }}>
          💬 Новый диалог
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => { onNewGroup?.(); setOpen(false) }}>
          👥 Новая группа
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => { onNewNote?.(); setOpen(false) }}>
          📝 Новая заметка
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
```

### Шаг 2: Добавить в Dashboard Page

```typescript
// src/app/dashboard/page.tsx
"use client"

import { QuickActionMenu } from "@/components/ui/quick-action-menu"

export default function DashboardPage() {
  // ... существующий код ...

  const handleNewDialog = () => {
    console.log('Создание нового диалога')
    // Ваша логика здесь
  }

  const handleNewGroup = () => {
    console.log('Создание новой группы')
    // Ваша логика здесь
  }

  const handleNewNote = () => {
    console.log('Создание новой заметки')
    // Ваша логика здесь
  }

  return (
    <div className="flex min-h-screen bg-background">
      {/* ... существующее содержимое ... */}

      {/* Добавляем кнопку N */}
      <QuickActionMenu
        onNewDialog={handleNewDialog}
        onNewGroup={handleNewGroup}
        onNewNote={handleNewNote}
      />
    </div>
  )
}
```

---

## 🎨 Стили для кнопки N

```css
/* В globals.css */

/* Кнопка N с иконкой-ярлычком */
.quick-action-button {
  position: fixed;
  bottom: 1.5rem;
  left: 1.5rem;
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transition: all 0.3s ease;
}

.quick-action-button:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.quick-action-button .badge {
  position: absolute;
  top: -0.25rem;
  right: -0.25rem;
  background: white;
  color: black;
  width: 1.25rem;
  height: 1.25rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: bold;
  border: 2px solid currentColor;
}
```

---

## 📋 Клавиатурные сокращения (возможные расширения)

```typescript
// Можно добавить и другие горячие клавиши:
const keyboardShortcuts = {
  'n': () => openNewMenu(),        // N - Новое
  '?': () => showHelp(),            // ? - Справка
  'k': () => openCommandPalette(), // Cmd+K - Командная палитра
  '1': () => goToDashboard(),       // 1 - Dashboard
  '2': () => goToChat(),            // 2 - Chat
}

// Пример реализации:
useEffect(() => {
  const handleKeyboard = (e: KeyboardEvent) => {
    if (e.ctrlKey || e.metaKey) {
      // Cmd/Ctrl + K для командной палитры
      if (e.key === 'k') {
        e.preventDefault()
        openCommandPalette()
      }
    } else if (!isInputActive(e.target)) {
      // Одиночные клавиши только если не в input
      const action = keyboardShortcuts[e.key]
      if (action) {
        e.preventDefault()
        action()
      }
    }
  }

  window.addEventListener('keydown', handleKeyboard)
  return () => window.removeEventListener('keydown', handleKeyboard)
}, [])
```

---

## 🎯 Практические примеры в разных приложениях

### Slack: N = Новое сообщение
```
При нажатии N → Открывается поле для нового сообщения
```

### GitHub: N = Новый issue
```
При нажатии N → Открывается форма создания новой задачи
```

### Figma: N = Новый элемент
```
При нажатии N → Контекстное меню для добавления элементов
```

### Trello: N = Новая карточка
```
При нажатии N → Создается новая карточка в текущей колонке
```

---

## ✨ Лучшие практики

1. **Контекстность**: Кнопка N должна создавать элемент, соответствующий текущему контексту
2. **Видимость**: Показывайте подсказку "Нажми N" для новых пользователей
3. **Доступность**: Работайте корректно с input полями (не открывайте меню когда печатают)
4. **Feedback**: Покажите визуальный feedback (анимация, звук)
5. **Альтернатива**: Всегда предоставляйте кнопку-альтернативу для пользователей, которые не знают о горячей клавише

---

## 📚 Полезные ссылки

- [MDN: Keyboard Event](https://developer.mozilla.org/en-US/docs/Web/API/KeyboardEvent)
- [W3C: Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [shadcn/ui Dropdown Menu](https://ui.shadcn.com/docs/components/dropdown-menu)
