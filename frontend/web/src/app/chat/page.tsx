"use client";

import { useChat } from "@/hooks/use-chat";
import { ChatWindow } from "@/components/chat/chat-window";
import { DashboardHeader } from "@/components/dashboard/header";
import { Sidebar } from "@/components/dashboard/sidebar";
import { useState } from "react";

export default function ChatPage() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Using mock userId for now, in real app would come from auth
  const userId = 123456;

  const {
    sessionId,
    messages,
    currentMode,
    isLoading,
    error,
    sendMessage,
    switchMode,
    clearChat,
  } = useChat(userId);

  const handleSendMessage = async (message: string) => {
    await sendMessage(message);
  };

  const handleModeChange = async (mode: "normal" | "admin") => {
    await switchMode(mode);
  };

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <Sidebar open={sidebarOpen} onOpenChange={setSidebarOpen} />

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <DashboardHeader onMenuClick={() => setSidebarOpen(true)} title="Chat" />

        {/* Chat Area */}
        <div className="flex-1 container mx-auto p-6">
          <div className="h-full">
            {/* Error Display */}
            {error && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-800">
                  <strong>Ошибка:</strong> {error}
                </p>
              </div>
            )}

            {/* Chat Window */}
            {sessionId ? (
              <div className="h-[calc(100vh-200px)] rounded-lg overflow-hidden shadow-lg">
                <ChatWindow
                  messages={messages}
                  isLoading={isLoading}
                  currentMode={currentMode}
                  onSendMessage={handleSendMessage}
                  onModeChange={handleModeChange}
                />
              </div>
            ) : (
              <div className="flex items-center justify-center h-full">
                <div className="text-center">
                  <div className="text-4xl mb-4">⏳</div>
                  <p className="text-lg text-gray-600">
                    Инициализация чата...
                  </p>
                </div>
              </div>
            )}

            {/* Action Buttons */}
            {sessionId && (
              <div className="mt-4 flex justify-end gap-2">
                <button
                  onClick={clearChat}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition"
                >
                  Очистить чат
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
