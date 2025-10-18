"use client";

import { useState, useEffect } from "react";
import { useChat } from "@/hooks/use-chat";
import { FloatingChatButton } from "./floating-chat-button";
import { ChatWindow } from "./chat-window";
import { ChatError } from "./chat-error";

interface ChatContainerProps {
  userId?: number;
  initialMode?: "normal" | "admin";
}

export function ChatContainer({
  userId = 123456,
  initialMode = "normal",
}: ChatContainerProps) {
  const [isOpen, setIsOpen] = useState(false);

  // Use real chat hook
  const {
    sessionId,
    messages,
    currentMode,
    isLoading,
    error,
    sendMessage,
    switchMode,
  } = useChat(userId);

  // Set initial mode if different from current
  useEffect(() => {
    if (initialMode && initialMode !== currentMode) {
      switchMode(initialMode);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialMode]); // Only run once on mount

  const handleSendMessage = async (message: string) => {
    await sendMessage(message);
  };

  const handleModeChange = async (mode: "normal" | "admin") => {
    await switchMode(mode);
  };

  // Only show if session is ready
  if (!sessionId) {
    return null;
  }

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
            onClose={() => {}}
            onRetry={() => {
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
            onClose={() => {}}
            onRetry={() => {
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
