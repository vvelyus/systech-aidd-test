import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
}

export function ErrorMessage({ message, onRetry }: ErrorMessageProps) {
  return (
    <Card className="border-red-200 bg-red-50">
      <CardHeader>
        <CardTitle className="text-red-800">Ошибка загрузки данных</CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-red-700 mb-4">{message}</p>
        {onRetry && (
          <Button variant="outline" onClick={onRetry}>
            Повторить попытку
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
