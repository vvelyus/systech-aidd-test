"use client";

import { AlertCircle, X } from "lucide-react";
import { Button } from "@/components/ui/button";

interface ChatErrorProps {
  error: string | null;
  onClose?: () => void;
  onRetry?: () => void;
}

export function ChatError({ error, onClose, onRetry }: ChatErrorProps) {
  if (!error) return null;

  const isNetworkError = error.includes("network") || error.includes("fetch");
  const isTimeoutError = error.includes("timeout") || error.includes("timed out");

  let suggestion = "Попробуйте еще раз.";
  if (isNetworkError) {
    suggestion = "Проверьте подключение к интернету.";
  } else if (isTimeoutError) {
    suggestion = "Запрос занял слишком много времени. Попробуйте более простой вопрос.";
  }

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
      <div className="flex items-start gap-3">
        <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
        <div className="flex-1 min-w-0">
          <h3 className="font-medium text-red-800">Ошибка</h3>
          <p className="text-sm text-red-700 mt-1 break-words">{error}</p>
          <p className="text-sm text-red-600 mt-2">{suggestion}</p>
          <div className="flex gap-2 mt-3">
            {onRetry && (
              <Button
                size="sm"
                variant="outline"
                onClick={onRetry}
                className="border-red-200 hover:bg-red-100"
              >
                Повторить
              </Button>
            )}
            {onClose && (
              <Button
                size="sm"
                variant="ghost"
                onClick={onClose}
                className="text-red-600 hover:bg-red-100"
              >
                <X className="w-4 h-4" />
              </Button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
