"use client";

import { useEffect, useRef } from "react";
import { ChatMessage as ChatMessageType, ChatMode } from "@/types/chat";
import { ChatMessage } from "./chat-message";
import { ChatInput } from "./chat-input";
import { ModeToggle } from "./mode-toggle";
import { SuggestedQuestions } from "./suggested-questions";
import { LoadingSkeleton } from "./loading-skeleton";
import { Loader2 } from "lucide-react";

interface ChatWindowProps {
  messages: ChatMessageType[];
  isLoading?: boolean;
  currentMode?: ChatMode;
  onSendMessage?: (message: string) => void;
  onModeChange?: (mode: ChatMode) => void;
}

export function ChatWindow({
  messages,
  isLoading = false,
  currentMode = "normal",
  onSendMessage,
  onModeChange,
}: ChatWindowProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  const isEmpty = messages.length === 0;

  return (
    <div className="flex flex-col h-full bg-white rounded-lg shadow-lg">
      {/* Header with Mode Toggle */}
      <ModeToggle
        currentMode={currentMode}
        onModeChange={onModeChange || (() => {})}
      />

      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        {isEmpty ? (
          <div className="flex items-center justify-center h-full">
            <div className="w-full max-w-md">
              <div className="text-center mb-6">
                <p className="text-lg font-medium mb-2">Добро пожаловать! 👋</p>
                <p className="text-sm text-gray-500">
                  {currentMode === "admin"
                    ? "Задавайте вопросы о статистике диалогов"
                    : "Начните диалог с AI-ассистентом"}
                </p>
              </div>
              <SuggestedQuestions
                mode={currentMode}
                onSelect={onSendMessage || (() => {})}
                isLoading={isLoading}
              />
            </div>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <ChatMessage key={message.id} message={message} />
            ))}
            {isLoading && <LoadingSkeleton count={2} show={true} />}
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Input */}
      <ChatInput
        onSend={onSendMessage || (() => {})}
        isLoading={isLoading}
        placeholder={
          currentMode === "admin"
            ? "Задайте вопрос о статистике..."
            : "Введите сообщение..."
        }
      />
    </div>
  );
}
