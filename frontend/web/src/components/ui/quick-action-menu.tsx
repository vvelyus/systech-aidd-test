"use client"

import React, { useState, useEffect } from "react"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu"
import { Button } from "@/components/ui/button"
import { Plus, MessageSquare, Users, FileText, Settings } from "lucide-react"

interface QuickActionMenuProps {
  onNewDialog?: () => void
  onNewGroup?: () => void
  onNewNote?: () => void
  onNewReport?: () => void
}

/**
 * QuickActionMenu компонент
 *
 * Горячая клавиша: N
 * Открывает меню для быстрого создания новых элементов
 *
 * @example
 * ```tsx
 * <QuickActionMenu
 *   onNewDialog={() => console.log('New dialog')}
 *   onNewGroup={() => console.log('New group')}
 * />
 * ```
 */
export function QuickActionMenu({
  onNewDialog,
  onNewGroup,
  onNewNote,
  onNewReport,
}: QuickActionMenuProps) {
  const [open, setOpen] = useState(false)
  const [showHint, setShowHint] = useState(false)

  // Обработка горячей клавиши N
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement

      // Не открываем меню если пользователь печатает в input/textarea
      const isInputElement =
        target instanceof HTMLInputElement ||
        target instanceof HTMLTextAreaElement ||
        target.contentEditable === 'true'

      if (!isInputElement && (e.key === 'n' || e.key === 'N')) {
        e.preventDefault()
        setOpen(!open)
      }

      // Показываем подсказку при Shift+? (Help)
      if (e.key === '?' && e.shiftKey) {
        setShowHint(!showHint)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [open, showHint])

  const menuItems = [
    {
      icon: MessageSquare,
      label: '💬 Новый диалог',
      description: 'Начать новую беседу',
      onClick: onNewDialog,
      shortcut: 'N, D'
    },
    {
      icon: Users,
      label: '👥 Новая группа',
      description: 'Создать новую группу',
      onClick: onNewGroup,
      shortcut: 'N, G'
    },
    {
      icon: FileText,
      label: '📝 Новая заметка',
      description: 'Добавить новую заметку',
      onClick: onNewNote,
      shortcut: 'N, N'
    },
    {
      icon: Settings,
      label: '📊 Новый отчет',
      description: 'Создать новый отчет',
      onClick: onNewReport,
      shortcut: 'N, R'
    },
  ]

  return (
    <>
      {/* Кнопка N */}
      <DropdownMenu open={open} onOpenChange={setOpen}>
        <DropdownMenuTrigger asChild>
          <Button
            variant="default"
            size="icon"
            className="fixed bottom-6 left-6 rounded-full w-12 h-12 shadow-lg hover:shadow-xl transition-all hover:scale-110 z-50 group"
            title="N - Создать новое (горячая клавиша)"
            aria-label="Quick action menu"
          >
            <Plus className="h-6 w-6" />
            {/* Ярлычок с буквой N */}
            <span className="absolute -top-2 -right-2 bg-white text-black text-xs rounded-full w-6 h-6 flex items-center justify-center font-bold shadow-md group-hover:bg-gray-100 transition-colors">
              N
            </span>
          </Button>
        </DropdownMenuTrigger>

        {/* Выпадающее меню */}
        <DropdownMenuContent side="right" align="end" className="w-64">
          {/* Заголовок с подсказкой */}
          <div className="px-2 py-1.5 text-xs text-muted-foreground font-medium">
            Быстрое действие (Нажми N)
          </div>
          <DropdownMenuSeparator />

          {/* Пункты меню */}
          {menuItems.map((item, index) => {
            const IconComponent = item.icon
            return (
              <DropdownMenuItem
                key={index}
                onClick={() => {
                  item.onClick?.()
                  setOpen(false)
                }}
                className="cursor-pointer group/item"
              >
                <div className="flex items-start gap-3 py-1">
                  <IconComponent className="h-5 w-5 mt-0.5 flex-shrink-0 text-muted-foreground group-hover/item:text-foreground transition-colors" />
                  <div className="flex-1">
                    <div className="text-sm font-medium">{item.label}</div>
                    <div className="text-xs text-muted-foreground">
                      {item.description}
                    </div>
                  </div>
                  <div className="text-xs text-muted-foreground ml-2">
                    {item.shortcut}
                  </div>
                </div>
              </DropdownMenuItem>
            )
          })}

          <DropdownMenuSeparator />

          {/* Подсказка */}
          <div className="px-2 py-1.5 text-xs text-muted-foreground">
            ⌨️ Нажми <kbd className="bg-muted px-1.5 py-0.5 rounded text-xs font-mono">?</kbd> для справки
          </div>
        </DropdownMenuContent>
      </DropdownMenu>

      {/* Подсказка (если включена) */}
      {showHint && (
        <div className="fixed bottom-24 left-6 bg-card border border-border rounded-lg shadow-lg p-4 w-64 z-40 animate-in fade-in slide-in-from-bottom-2">
          <div className="space-y-2 text-sm">
            <h3 className="font-semibold">Горячие клавиши</h3>
            <div className="space-y-1 text-muted-foreground">
              <div><kbd className="bg-muted px-1 rounded">N</kbd> - Быстрое действие</div>
              <div><kbd className="bg-muted px-1 rounded">?</kbd> - Справка</div>
              <div><kbd className="bg-muted px-1 rounded">1</kbd> - Dashboard</div>
              <div><kbd className="bg-muted px-1 rounded">2</kbd> - Chat</div>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
