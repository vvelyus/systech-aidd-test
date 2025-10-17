"use client";

import { useState, useCallback } from "react";
import { ChatMode, ChatMessage as ChatMessageType } from "@/types/chat";
import { FloatingChatButton } from "./floating-chat-button";
import { ChatWindow } from "./chat-window";
import { ChatError } from "./chat-error";

interface ChatContainerProps {
  sessionId: string;
  userId?: number;
  initialMode?: ChatMode;
  onSendMessage?: (message: string, mode: ChatMode) => void;
}

export function ChatContainer({
  sessionId,
  userId,
  initialMode = "normal",
  onSendMessage,
}: ChatContainerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [currentMode, setCurrentMode] = useState<ChatMode>(initialMode);
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSendMessage = useCallback(
    (message: string) => {
      if (!message.trim()) return;

      // Clear error on new message
      setError(null);

      // Add user message to UI
      const userMessage: ChatMessageType = {
        id: `msg-${Date.now()}`,
        content: message,
        role: "user",
        mode: currentMode,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);

      // Call parent handler or API
      if (onSendMessage) {
        onSendMessage(message, currentMode);
      }

      // Simulate response (will be replaced with real API call)
      setTimeout(() => {
        const assistantMessage: ChatMessageType = {
          id: `msg-${Date.now() + 1}`,
          content: `Ответ на вопрос: "${message}"`,
          role: "assistant",
          mode: currentMode,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, assistantMessage]);
        setIsLoading(false);
      }, 1000);
    },
    [currentMode, onSendMessage]
  );

  const handleModeChange = (mode: ChatMode) => {
    setCurrentMode(mode);
    setError(null);
    // Clear messages when changing mode as per requirements
    setMessages([]);
  };

  return (
    <>
      {/* Floating Button */}
      <FloatingChatButton
        isOpen={isOpen}
        onToggle={setIsOpen}
        unreadCount={0}
      />

      {/* Chat Modal */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 w-96 h-[500px] z-40 rounded-lg overflow-hidden flex flex-col">
          <ChatError
            error={error}
            onClose={() => setError(null)}
            onRetry={() => {
              setError(null);
              if (messages.length > 0) {
                const lastUserMessage = [...messages]
                  .reverse()
                  .find((m) => m.role === "user");
                if (lastUserMessage) {
                  handleSendMessage(lastUserMessage.content);
                }
              }
            }}
          />
          <div className="flex-1 overflow-hidden">
            <ChatWindow
              messages={messages}
              isLoading={isLoading}
              currentMode={currentMode}
              onSendMessage={handleSendMessage}
              onModeChange={handleModeChange}
            />
          </div>
        </div>
      )}

      {/* Mobile Fullscreen Chat */}
      {isOpen && (
        <div className="md:hidden fixed inset-0 z-40 bg-white flex flex-col">
          <div className="flex items-center justify-between p-4 border-b bg-white">
            <h2 className="text-lg font-semibold">AI Chat</h2>
            <button
              onClick={() => setIsOpen(false)}
              className="text-gray-500 hover:text-gray-700"
            >
              ✕
            </button>
          </div>
          <ChatError
            error={error}
            onClose={() => setError(null)}
            onRetry={() => {
              setError(null);
              if (messages.length > 0) {
                const lastUserMessage = [...messages]
                  .reverse()
                  .find((m) => m.role === "user");
                if (lastUserMessage) {
                  handleSendMessage(lastUserMessage.content);
                }
              }
            }}
          />
          <div className="flex-1 overflow-hidden">
            <ChatWindow
              messages={messages}
              isLoading={isLoading}
              currentMode={currentMode}
              onSendMessage={handleSendMessage}
              onModeChange={handleModeChange}
            />
          </div>
        </div>
      )}
    </>
  );
}
