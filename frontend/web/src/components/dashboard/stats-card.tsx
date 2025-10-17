import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface StatsCardProps {
  title: string;
  value: number;
  change: number;
  icon?: React.ReactNode;
}

export function StatsCard({ title, value, change, icon }: StatsCardProps) {
  const isPositive = change >= 0;
  const changeColor = isPositive ? "text-green-600" : "text-red-600";
  const changeSign = isPositive ? "+" : "";

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        {icon}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value.toLocaleString()}</div>
        <p className={`text-xs ${changeColor} mt-1`}>
          {changeSign}
          {change.toFixed(1)}% относительно прошлого периода
        </p>
      </CardContent>
    </Card>
  );
}
