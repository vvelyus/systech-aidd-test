"use client";

import { useCallback, useEffect, useState } from "react";
import { getStats } from "@/lib/api";
import { Period, StatsResponse } from "@/types/stats";
import { StatsCard } from "@/components/dashboard/stats-card";
import { PeriodSelector } from "@/components/dashboard/period-selector";
import { LoadingSkeleton } from "@/components/dashboard/loading-skeleton";
import { ErrorMessage } from "@/components/dashboard/error-message";
import { Sidebar } from "@/components/dashboard/sidebar";
import { DashboardHeader } from "@/components/dashboard/header";
import { ActivityChart } from "@/components/dashboard/activity-chart";
import { RecentDialogsTable } from "@/components/dashboard/recent-dialogs";
import { QuickActionMenu } from "@/components/ui/quick-action-menu";

export default function DashboardPage() {
  const [period, setPeriod] = useState<Period>("week");
  const [data, setData] = useState<StatsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sidebarOpen, setSidebarOpen] = useState(false);

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

  const handleNewDialog = () => {
    console.log('📌 Создание нового диалога...');
    // TODO: Реализовать создание нового диалога
  };

  const handleNewGroup = () => {
    console.log('👥 Создание новой группы...');
    // TODO: Реализовать создание новой группы
  };

  const handleNewReport = () => {
    console.log('📊 Создание нового отчета...');
    // TODO: Реализовать создание нового отчета
  };

  if (error) {
    return (
      <div className="flex h-screen flex-col">
        <DashboardHeader onMenuClick={() => setSidebarOpen(true)} />
        <Sidebar open={sidebarOpen} onOpenChange={setSidebarOpen} />
        <main className="flex-1 container mx-auto p-6">
          <div className="mb-6 flex items-center justify-between">
            <h1 className="text-3xl font-bold">Статистика диалогов</h1>
          </div>
          <ErrorMessage message={error} onRetry={loadData} />
        </main>
        <QuickActionMenu
          onNewDialog={handleNewDialog}
          onNewGroup={handleNewGroup}
          onNewReport={handleNewReport}
        />
      </div>
    );
  }

  if (loading || !data) {
    return (
      <div className="flex h-screen flex-col">
        <DashboardHeader onMenuClick={() => setSidebarOpen(true)} />
        <Sidebar open={sidebarOpen} onOpenChange={setSidebarOpen} />
        <main className="flex-1 container mx-auto p-6">
          <div className="mb-6 flex items-center justify-between">
            <h1 className="text-3xl font-bold">Статистика диалогов</h1>
          </div>
          <LoadingSkeleton />
        </main>
        <QuickActionMenu
          onNewDialog={handleNewDialog}
          onNewGroup={handleNewGroup}
          onNewReport={handleNewReport}
        />
      </div>
    );
  }

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar open={sidebarOpen} onOpenChange={setSidebarOpen} />
      <div className="flex-1 flex flex-col">
        <DashboardHeader onMenuClick={() => setSidebarOpen(true)} />
        <main className="flex-1 container mx-auto p-6 space-y-6">
          {/* Page Header */}
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold">Статистика диалогов</h1>
            <PeriodSelector selectedPeriod={period} onPeriodChange={setPeriod} />
          </div>

          {/* Summary Cards */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatsCard
              title="Всего сообщений"
              value={data.summary.total_messages}
              change={data.summary.total_messages_change}
              description="Всего за период"
            />
            <StatsCard
              title="Активных пользователей"
              value={data.summary.active_users}
              change={data.summary.active_users_change}
              description="Посещали в этом периоде"
            />
            <StatsCard
              title="Средняя длина диалога"
              value={parseFloat(data.summary.avg_dialog_length.toFixed(1))}
              change={data.summary.avg_dialog_length_change}
              description="Сообщений в диалоге"
            />
            <StatsCard
              title="Сообщений в день"
              value={parseFloat(data.summary.messages_per_day.toFixed(1))}
              change={data.summary.messages_per_day_change}
              description="В среднем за день"
            />
          </div>

          {/* Charts and Top Users */}
          <div className="grid gap-4 md:grid-cols-2">
            {/* Activity Chart */}
            <ActivityChart data={data.activity_timeline} isLoading={loading} />

            {/* Top Users */}
            <div className="rounded-lg border bg-card p-6">
              <h3 className="text-lg font-semibold mb-4">Топ пользователей</h3>
              <div className="space-y-3">
                {data.top_users.map((user, index) => (
                  <div
                    key={user.user_id}
                    className="flex items-center justify-between pb-3 border-b last:border-0"
                  >
                    <div>
                      <span className="font-semibold mr-2 text-sm">
                        #{index + 1}
                      </span>
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
            </div>
          </div>

          {/* Recent Dialogs Table */}
          <RecentDialogsTable data={data.recent_dialogs} isLoading={loading} />
        </main>

        {/* Quick Action Menu (Кнопка N) */}
        <QuickActionMenu
          onNewDialog={handleNewDialog}
          onNewGroup={handleNewGroup}
          onNewReport={handleNewReport}
        />
      </div>
    </div>
  );
}
