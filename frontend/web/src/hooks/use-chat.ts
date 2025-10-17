"use client";

import { useCallback, useEffect } from "react";
import { ChatMode, ChatMessage } from "@/types/chat";
import {
  chatMessage as apiChatMessage,
  getChatHistory,
  createChatSession,
} from "@/lib/api";
import { useChatStore } from "@/lib/chat-store";
import { v4 as uuidv4 } from "uuid";

/**
 * Custom hook для работы с чатом
 * Управляет отправкой сообщений, загрузкой истории и переключением режимов
 */
export function useChat(userId?: number) {
  const {
    sessionId,
    messages,
    currentMode,
    isLoading,
    error,
    setSessionId,
    addMessage,
    setMessages,
    setMode,
    setLoading,
    setError,
    clearMessages,
    clearError,
  } = useChatStore();

  // Инициализация сессии при монтировании
  useEffect(() => {
    const initSession = async () => {
      if (!sessionId && userId) {
        try {
          const newSessionId = await createChatSession(userId, currentMode);
          setSessionId(newSessionId);
        } catch (err) {
          setError(
            err instanceof Error ? err.message : "Failed to create session"
          );
        }
      }
    };

    initSession();
  }, [userId, sessionId, currentMode, setSessionId, setError]);

  // Загрузка истории при смене режима или сессии
  useEffect(() => {
    const loadHistory = async () => {
      if (sessionId) {
        try {
          const history = await getChatHistory(sessionId);
          setMessages(history.items);
        } catch (err) {
          setError(
            err instanceof Error ? err.message : "Failed to load history"
          );
        }
      }
    };

    loadHistory();
  }, [sessionId, setMessages, setError]);

  /**
   * Отправить сообщение в чат
   */
  const sendMessage = useCallback(
    async (content: string) => {
      if (!sessionId || !content.trim()) return;

      try {
        clearError();
        setLoading(true);

        // Добавить сообщение пользователя
        const userMessage: ChatMessage = {
          id: uuidv4(),
          content,
          role: "user",
          mode: currentMode,
          timestamp: new Date(),
        };
        addMessage(userMessage);

        // Отправить на сервер и собрать ответ
        let assistantContent = "";

        try {
          for await (const chunk of apiChatMessage(
            content,
            sessionId,
            currentMode
          )) {
            assistantContent += chunk;
          }
        } catch (err) {
          throw new Error(
            err instanceof Error ? err.message : "Streaming error"
          );
        }

        // Добавить ответ ассистента
        const assistantMessage: ChatMessage = {
          id: uuidv4(),
          content: assistantContent,
          role: "assistant",
          mode: currentMode,
          timestamp: new Date(),
        };
        addMessage(assistantMessage);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to send message");
      } finally {
        setLoading(false);
      }
    },
    [sessionId, currentMode, setLoading, setError, addMessage, clearError]
  );

  /**
   * Переключить режим чата
   */
  const switchMode = useCallback(
    async (newMode: ChatMode) => {
      if (newMode === currentMode) return;

      try {
        clearError();
        // Режим автоматически переключается, история очищается (в store)
        setMode(newMode);

        // Опционально: создать новую сессию для нового режима
        if (userId) {
          const newSessionId = await createChatSession(userId, newMode);
          setSessionId(newSessionId);
        }
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to switch mode"
        );
      }
    },
    [currentMode, userId, setMode, setSessionId, setError, clearError]
  );

  /**
   * Очистить чат
   */
  const clearChat = useCallback(() => {
    clearMessages();
    clearError();
  }, [clearMessages, clearError]);

  return {
    // State
    sessionId,
    messages,
    currentMode,
    isLoading,
    error,

    // Actions
    sendMessage,
    switchMode,
    clearChat,
  };
}

/**
 * Hook для управления только состоянием чата
 */
export function useChatState() {
  const { messages, currentMode, isLoading, error, isOpen } = useChatStore();
  const { setLoading, setError, setOpen } = useChatStore();

  return {
    messages,
    currentMode,
    isLoading,
    error,
    isOpen,
    setLoading,
    setError,
    setOpen,
  };
}
