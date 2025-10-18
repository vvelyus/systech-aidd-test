import { StatsResponse, Period } from "@/types/stats";
import type {
  ChatMode,
  ChatMessage,
  TextToSqlResponse,
} from "@/types/chat";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Timeout configuration for different request types (in milliseconds)
const TIMEOUT_CONFIG = {
  default: 30000,      // 30s for regular requests
  chat: 180000,        // 3 minutes for chat messages (admin mode can take longer)
  stats: 60000,        // 1 minute for statistics
  session: 30000,      // 30s for session creation
  history: 30000,      // 30s for history retrieval
} as const;

/**
 * Helper to add timeout to fetch requests
 */
function withTimeout(timeoutMs: number): AbortSignal {
  const controller = new AbortController();
  setTimeout(() => controller.abort(), timeoutMs);

  return controller.signal;
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function getStats(
  period: Period = "week"
): Promise<StatsResponse> {
  try {
    const response = await fetch(`${API_URL}/stats?period=${period}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      signal: withTimeout(TIMEOUT_CONFIG.stats),
    });

    if (!response.ok) {
      throw new ApiError(`API error: ${response.statusText}`, response.status);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError(`Request timeout after ${TIMEOUT_CONFIG.stats / 1000}s`);
    }
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError("Failed to fetch stats");
  }
}

/**
 * Отправляет сообщение в чат и возвращает streaming ответ
 * Использует Server-Sent Events (SSE) для получения chunks ответа
 * Поддерживает увеличенный таймаут для админ-режима (сложные запросы SQL)
 */
export async function* chatMessage(
  message: string,
  sessionId: string,
  mode: ChatMode = "normal"
): AsyncGenerator<string> {
  const params = new URLSearchParams({
    message,
    session_id: sessionId,
    mode,
  });

  const url = `${API_URL}/api/chat/message?${params}`;

  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      signal: withTimeout(TIMEOUT_CONFIG.chat),
    });

    if (!response.ok) {
      throw new ApiError(
        `Chat error: ${response.statusText}`,
        response.status
      );
    }

    const reader = response.body?.getReader();
    if (!reader) {
      throw new Error("Response body is not readable");
    }

    const decoder = new TextDecoder();
    let buffer = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines[lines.length - 1] || "";

      for (let i = 0; i < lines.length - 1; i++) {
        const line = lines[i];
        if (!line) continue;

        // Парсим SSE формат: data: {...}
        if (line.startsWith("data: ")) {
          const data = line.slice(6);
          if (data === "[DONE]") {
            break;
          }

          try {
            const json = JSON.parse(data);
            if (json.content) {
              yield json.content;
            }
          } catch {
            // Ignore parsing errors
          }
        }
      }
    }
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError(`Chat request timeout after ${TIMEOUT_CONFIG.chat / 1000}s`);
    }
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(
      error instanceof Error ? error.message : "Failed to send chat message"
    );
  }
}

/**
 * Получает историю сообщений для сессии с поддержкой pagination
 */
export interface ChatHistoryResponse {
  items: ChatMessage[];
  total: number;
  offset: number;
  limit: number;
  hasMore: boolean;
}

export async function getChatHistory(
  sessionId: string,
  limit: number = 50,
  offset: number = 0
): Promise<ChatHistoryResponse> {
  try {
    const params = new URLSearchParams({
      session_id: sessionId,
      limit: limit.toString(),
      offset: offset.toString(),
    });

    const response = await fetch(`${API_URL}/api/chat/history?${params}`, {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      signal: withTimeout(TIMEOUT_CONFIG.history),
    });

    if (!response.ok) {
      throw new ApiError(
        `Failed to fetch chat history: ${response.statusText}`,
        response.status
      );
    }

    const data: ChatHistoryResponse = await response.json();
    return data;
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError(`History request timeout after ${TIMEOUT_CONFIG.history / 1000}s`);
    }
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError("Failed to fetch chat history");
  }
}

/**
 * Для админ-режима: показать сгенерированный SQL без выполнения
 */
export async function debugSql(
  question: string,
  context?: Record<string, unknown>
): Promise<TextToSqlResponse> {
  try {
    const response = await fetch(`${API_URL}/api/chat/debug/sql`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question,
        context: context || {},
      }),
      signal: withTimeout(TIMEOUT_CONFIG.chat),
    });

    if (!response.ok) {
      throw new ApiError(
        `SQL debug error: ${response.statusText}`,
        response.status
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError(`SQL debug timeout after ${TIMEOUT_CONFIG.chat / 1000}s`);
    }
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError("Failed to debug SQL");
  }
}

/**
 * Создает новую сессию чата
 */
export async function createChatSession(
  userId: number,
  mode: ChatMode = "normal"
): Promise<string> {
  try {
    const params = new URLSearchParams({
      user_id: userId.toString(),
      mode,
    });

    const response = await fetch(`${API_URL}/api/chat/session?${params}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      signal: withTimeout(TIMEOUT_CONFIG.session),
    });

    if (!response.ok) {
      throw new ApiError(
        `Session creation error: ${response.statusText}`,
        response.status
      );
    }

    const data = await response.json();
    return data.session_id;
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new ApiError(`Session creation timeout after ${TIMEOUT_CONFIG.session / 1000}s`);
    }
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError("Failed to create chat session");
  }
}
