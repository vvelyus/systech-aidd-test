"use client"

import React from "react"
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export interface TimelineData {
  date: string
  user_messages: number
  bot_messages: number
  total: number
}

interface ActivityChartProps {
  data: TimelineData[]
  isLoading?: boolean
}

// Custom dot component to display values on the chart (only for weekly data)
const CustomDot = (props: any) => {
  const { cx, cy, payload, dataKey } = props
  const value = payload[dataKey]

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

export function ActivityChart({ data, isLoading }: ActivityChartProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString("ru", { month: "short", day: "numeric" })
  }

  const chartData = data.map((item) => ({
    ...item,
    displayDate: formatDate(item.date),
  }))

  // Show dots with values only for weekly data (7 days)
  const isWeekly = data.length === 7
  const dotComponent = isWeekly ? <CustomDot dataKey="user_messages" /> : undefined
  const botDotComponent = isWeekly ? <CustomDot dataKey="bot_messages" /> : undefined

  return (
    <Card>
      <CardHeader>
        <CardTitle>График активности</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="h-64 flex items-center justify-center text-muted-foreground">
            <p>Загрузка графика...</p>
          </div>
        ) : (
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient
                  id="colorUserMessages"
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.1} />
                </linearGradient>
                <linearGradient id="colorBotMessages" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0.1} />
                </linearGradient>
              </defs>
              <CartesianGrid
                strokeDasharray="0"
                stroke="#d4d4d8"
                horizontal={true}
                vertical={true}
              />
              <XAxis
                dataKey="displayDate"
                stroke="var(--color-muted-foreground)"
                style={{ fontSize: "12px" }}
              />
              <YAxis
                stroke="var(--color-muted-foreground)"
                style={{ fontSize: "12px" }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "var(--color-background)",
                  border: "1px solid var(--color-border)",
                  borderRadius: "8px",
                }}
                formatter={(value) => [value, ""]}
              />
              <Area
                type="monotone"
                dataKey="user_messages"
                stroke="#3b82f6"
                fillOpacity={1}
                fill="url(#colorUserMessages)"
                name="Пользователи"
                dot={dotComponent}
              />
              <Area
                type="monotone"
                dataKey="bot_messages"
                stroke="#10b981"
                fillOpacity={1}
                fill="url(#colorBotMessages)"
                name="Бот"
                dot={botDotComponent}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  )
}
