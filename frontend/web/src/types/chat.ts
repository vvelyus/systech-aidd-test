/**
 * TypeScript типы для функциональности чата
 */

export type ChatMode = 'normal' | 'admin';
export type MessageRole = 'user' | 'assistant';

/**
 * Сообщение в чате
 */
export interface ChatMessage {
  id: string;
  content: string;
  role: MessageRole;
  mode: ChatMode;
  sqlQuery?: string;
  timestamp: Date;
  createdAt?: string; // ISO format from API
}

/**
 * Сессия чата
 */
export interface ChatSession {
  id: string;
  userId?: number;
  messages: ChatMessage[];
  mode: ChatMode;
  createdAt: Date;
}

/**
 * Ответ от API при отправке сообщения
 */
export interface ChatMessageResponse {
  id: string;
  userSessionId: string;
  content: string;
  role: MessageRole;
  mode: ChatMode;
  sqlQuery?: string;
  createdAt: string;
}

/**
 * Результат преобразования вопроса в SQL
 */
export interface TextToSqlResponse {
  sql: string;
  explanation: string;
}

/**
 * История чата
 */
export interface ChatHistory {
  sessionId: string;
  messages: ChatMessage[];
  totalMessages: number;
}

/**
 * Рекомендуемый вопрос
 */
export interface SuggestedQuestion {
  text: string;
  mode: ChatMode;
}

/**
 * Состояние чата для UI
 */
export interface ChatState {
  sessionId: string | null;
  messages: ChatMessage[];
  currentMode: ChatMode;
  isLoading: boolean;
  error: string | null;
  isOpen?: boolean;
}
