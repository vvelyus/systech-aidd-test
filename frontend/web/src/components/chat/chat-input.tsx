"use client";

import { useRef, useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Send, Loader2, HelpCircle } from "lucide-react";

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading?: boolean;
  placeholder?: string;
  maxLength?: number;
}

const MAX_MESSAGE_LENGTH = 5000;

export function ChatInput({
  onSend,
  isLoading = false,
  placeholder = "Введите сообщение...",
  maxLength = MAX_MESSAGE_LENGTH,
}: ChatInputProps) {
  const [message, setMessage] = useState("");
  const [showHint, setShowHint] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-expand textarea as user types
  useEffect(() => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
  }, [message]);

  // Auto-focus when component mounts
  useEffect(() => {
    textareaRef.current?.focus();
  }, []);

  const charCount = message.length;
  const isNearLimit = charCount > maxLength * 0.8;
  const isAtLimit = charCount >= maxLength;
  const remainingChars = maxLength - charCount;

  const handleSend = () => {
    if (message.trim() && !isLoading && !isAtLimit) {
      onSend(message);
      setMessage("");
      setShowHint(false);
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Enter to send, Shift+Enter for new line
    if (e.key === "Enter" && !e.shiftKey && !isAtLimit) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newMessage = e.target.value;
    if (newMessage.length <= maxLength) {
      setMessage(newMessage);
    }
  };

  return (
    <div className="flex flex-col gap-2 p-4 bg-white border-t border-gray-200 rounded-b-lg">
      {/* Help tooltip */}
      {showHint && (
        <div className="text-xs text-gray-600 bg-blue-50 border border-blue-200 rounded p-2 animate-fade-in">
          💡 <strong>Подсказка:</strong> Нажмите Enter для отправки, Shift+Enter для новой строки
        </div>
      )}

      {/* Input area */}
      <div className="flex gap-2">
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            onFocus={() => setShowHint(true)}
            onBlur={() => setShowHint(false)}
            placeholder={placeholder}
            disabled={isLoading}
            className={`w-full resize-none px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 disabled:bg-gray-100 disabled:cursor-not-allowed max-h-[120px] overflow-y-auto transition-all ${
              isAtLimit
                ? "border-red-300 focus:ring-red-500"
                : isNearLimit
                ? "border-yellow-300 focus:ring-yellow-500"
                : "border-gray-300 focus:ring-blue-500"
            }`}
            rows={1}
          />

          {/* Character counter */}
          <div
            className={`absolute bottom-2 right-3 text-xs font-medium transition-colors ${
              isAtLimit
                ? "text-red-500"
                : isNearLimit
                ? "text-yellow-600"
                : "text-gray-400"
            }`}
          >
            {charCount}/{maxLength}
          </div>
        </div>

        {/* Send button */}
        <Button
          onClick={handleSend}
          disabled={!message.trim() || isLoading || isAtLimit}
          size="lg"
          className="flex-shrink-0"
          title={
            isAtLimit
              ? "Превышен лимит символов"
              : !message.trim()
              ? "Введите сообщение"
              : "Отправить (Enter)"
          }
        >
          {isLoading ? (
            <Loader2 className="w-5 h-5 animate-spin" />
          ) : (
            <Send className="w-5 h-5" />
          )}
        </Button>
      </div>

      {/* Character limit warning */}
      {isNearLimit && (
        <div
          className={`text-xs transition-colors ${
            isAtLimit
              ? "text-red-600 font-semibold"
              : "text-yellow-600"
          }`}
        >
          {isAtLimit
            ? `❌ Достигнут лимит в ${maxLength} символов`
            : `⚠️ Осталось ${remainingChars} символов`}
        </div>
      )}
    </div>
  );
}
