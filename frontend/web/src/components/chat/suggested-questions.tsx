"use client";

import { ChatMode } from "@/types/chat";
import { Button } from "@/components/ui/button";
import { Lightbulb } from "lucide-react";

interface SuggestedQuestionsProps {
  mode: ChatMode;
  onSelect: (question: string) => void;
  isLoading?: boolean;
}

const SUGGESTED_QUESTIONS: Record<ChatMode, string[]> = {
  normal: [
    "Привет! Как дела?",
    "Какие у тебя возможности?",
    "Помоги мне с проблемой",
    "Расскажи интересный факт",
  ],
  admin: [
    "Сколько сообщений было отправлено на этой неделе?",
    "Кто самый активный пользователь?",
    "Какова средняя длина диалога?",
    "Покажи динамику сообщений за месяц",
  ],
};

export function SuggestedQuestions({
  mode,
  onSelect,
  isLoading = false,
}: SuggestedQuestionsProps) {
  const questions = SUGGESTED_QUESTIONS[mode];

  return (
    <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
      <div className="flex items-center gap-2 mb-3">
        <Lightbulb className="w-4 h-4 text-yellow-500" />
        <span className="text-sm font-medium text-gray-700">
          {mode === "admin" ? "Примеры запросов" : "Попробуй спросить"}
        </span>
      </div>

      <div className="grid gap-2 grid-cols-1 md:grid-cols-2">
        {questions.map((question, index) => (
          <Button
            key={index}
            variant="outline"
            size="sm"
            onClick={() => onSelect(question)}
            disabled={isLoading}
            className="justify-start h-auto text-left whitespace-normal text-xs"
          >
            {question}
          </Button>
        ))}
      </div>
    </div>
  );
}
