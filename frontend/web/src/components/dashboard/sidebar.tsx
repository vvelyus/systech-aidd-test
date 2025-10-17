"use client"

import React from "react"
import Link from "next/link"
import { BarChart3, MessageCircle } from "lucide-react"

import { cn } from "@/lib/utils"
import {
  Sheet,
  SheetContent,
} from "@/components/ui/sheet"

interface SidebarProps {
  open?: boolean
  onOpenChange?: (open: boolean) => void
}

export function Sidebar({ open, onOpenChange }: SidebarProps) {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="left" className="w-64">
        <nav className="flex flex-col space-y-4 mt-8">
          <Link
            href="/dashboard"
            className={cn(
              "flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-accent transition-colors",
              "text-sm font-medium"
            )}
            onClick={() => onOpenChange?.(false)}
          >
            <BarChart3 className="h-5 w-5" />
            <span>Dashboard</span>
          </Link>
          <Link
            href="/chat"
            className={cn(
              "flex items-center gap-3 px-4 py-2 rounded-lg hover:bg-accent transition-colors",
              "text-sm font-medium text-muted-foreground"
            )}
            onClick={() => onOpenChange?.(false)}
          >
            <MessageCircle className="h-5 w-5" />
            <span>Чат (скоро)</span>
          </Link>
        </nav>
      </SheetContent>
    </Sheet>
  )
}
