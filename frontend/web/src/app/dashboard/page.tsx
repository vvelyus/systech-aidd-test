"use client";

import { useCallback, useEffect, useState } from "react";
import { getStats } from "@/lib/api";
import { Period, StatsResponse } from "@/types/stats";
import { StatsCard } from "@/components/dashboard/stats-card";
import { PeriodSelector } from "@/components/dashboard/period-selector";
import { LoadingSkeleton } from "@/components/dashboard/loading-skeleton";
import { ErrorMessage } from "@/components/dashboard/error-message";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function DashboardPage() {
  const [period, setPeriod] = useState<Period>("week");
  const [data, setData] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const stats = await getStats(period);
      setData(stats);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Не удалось загрузить данные"
      );
    } finally {
      setLoading(false);
    }
  }, [period]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-3xl font-bold">Статистика диалогов</h1>
        </div>
        <LoadingSkeleton />
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-3xl font-bold">Статистика диалогов</h1>
        </div>
        <ErrorMessage message={error} onRetry={loadData} />
      </div>
    );
  }

  if (!data) {
    return null;
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold">Статистика диалогов</h1>
        <PeriodSelector selectedPeriod={period} onPeriodChange={setPeriod} />
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mb-6">
        <StatsCard
          title="Всего сообщений"
          value={data.summary.total_messages}
          change={data.summary.total_messages_change}
        />
        <StatsCard
          title="Активных пользователей"
          value={data.summary.active_users}
          change={data.summary.active_users_change}
        />
        <StatsCard
          title="Средняя длина диалога"
          value={data.summary.avg_dialog_length}
          change={data.summary.avg_dialog_length_change}
        />
        <StatsCard
          title="Сообщений в день"
          value={data.summary.messages_per_day}
          change={data.summary.messages_per_day_change}
        />
      </div>

      {/* Charts and Tables */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* Timeline Placeholder */}
        <Card>
          <CardHeader>
            <CardTitle>График активности</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-center justify-center text-muted-foreground">
              <p>
                График будет реализован в следующем спринте
                <br />({data.activity_timeline.length} точек данных)
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Top Users */}
        <Card>
          <CardHeader>
            <CardTitle>Топ пользователей</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {data.top_users.map((user, index) => (
                <div
                  key={user.user_id}
                  className="flex items-center justify-between border-b pb-2 last:border-0"
                >
                  <div>
                    <span className="font-semibold mr-2">#{index + 1}</span>
                    <span className="text-sm">
                      {user.first_name ||
                        user.username ||
                        `User ${user.user_id}`}
                    </span>
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {user.message_count} сообщений
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Dialogs */}
      <Card className="mt-4">
        <CardHeader>
          <CardTitle>Последние диалоги</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {data.recent_dialogs.map((dialog) => (
              <div
                key={dialog.user_id}
                className="flex items-center justify-between border-b pb-2 last:border-0"
              >
                <div className="flex-1">
                  <div className="text-sm font-medium">
                    {dialog.first_name ||
                      dialog.username ||
                      `User ${dialog.user_id}`}
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {dialog.last_message}
                  </div>
                </div>
                <div className="text-xs text-muted-foreground ml-4 text-right">
                  {dialog.message_count} сообщений
                  <br />
                  {new Date(dialog.last_activity).toLocaleString("ru")}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
