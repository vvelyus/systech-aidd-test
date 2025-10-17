"use client"

import React, { useState } from "react"
import { ChevronDown } from "lucide-react"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"

export interface DialogData {
  user_id: number
  username?: string | null
  first_name?: string | null
  last_message: string
  message_count: number
  last_activity: string
}

interface RecentDialogsTableProps {
  data: DialogData[]
  isLoading?: boolean
}

export function RecentDialogsTable({ data, isLoading }: RecentDialogsTableProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  const getUserDisplay = (dialog: DialogData) => {
    return dialog.first_name || dialog.username || `User ${dialog.user_id}`
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleString("ru", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    })
  }

  return (
    <Card className="mt-6">
      <CardHeader className="flex flex-row items-center justify-between space-y-0">
        <CardTitle>Последние диалоги</CardTitle>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setIsExpanded(!isExpanded)}
          className="gap-2"
        >
          <ChevronDown
            className={`h-4 w-4 transition-transform ${
              isExpanded ? "rotate-180" : ""
            }`}
          />
          {isExpanded ? "Скрыть" : "Показать"}
        </Button>
      </CardHeader>

      {isExpanded && (
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8 text-muted-foreground">
              <p>Загрузка диалогов...</p>
            </div>
          ) : data.length === 0 ? (
            <div className="flex items-center justify-center py-8 text-muted-foreground">
              <p>Нет диалогов для отображения</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Пользователь</TableHead>
                  <TableHead>Последнее сообщение</TableHead>
                  <TableHead className="text-right">Сообщений</TableHead>
                  <TableHead className="text-right">Последняя активность</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data.map((dialog) => (
                  <TableRow key={dialog.user_id}>
                    <TableCell className="font-medium">
                      {getUserDisplay(dialog)}
                    </TableCell>
                    <TableCell className="max-w-xs truncate">
                      {dialog.last_message}
                    </TableCell>
                    <TableCell className="text-right">
                      {dialog.message_count}
                    </TableCell>
                    <TableCell className="text-right text-sm text-muted-foreground">
                      {formatDate(dialog.last_activity)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      )}
    </Card>
  )
}
