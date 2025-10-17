import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown } from "lucide-react";

interface StatsCardProps {
  title: string;
  value: number;
  change: number;
  description?: string;
}

export function StatsCard({ title, value, change, description }: StatsCardProps) {
  const isPositive = change >= 0;
  const badgeVariant = isPositive ? "default" : "destructive";
  const TrendIcon = isPositive ? TrendingUp : TrendingDown;

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        <Badge variant={badgeVariant} className="gap-1">
          <TrendIcon className="h-3 w-3" />
          {isPositive ? "+" : ""}{change.toFixed(1)}%
        </Badge>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="text-3xl font-bold">{value.toLocaleString()}</div>
        {description && (
          <p className="text-xs text-muted-foreground">
            {description}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
