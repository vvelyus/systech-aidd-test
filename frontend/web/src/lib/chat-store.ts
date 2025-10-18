/**
 * Zustand store для управления состоянием чата
 */

import { create } from "zustand";
import { ChatMode, ChatMessage } from "@/types/chat";

export interface ChatStore {
  // State
  sessionId: string | null;
  messages: ChatMessage[];
  currentMode: ChatMode;
  isLoading: boolean;
  error: string | null;
  isOpen: boolean;

  // Actions
  setSessionId: (id: string) => void;
  addMessage: (message: ChatMessage) => void;
  setMessages: (messages: ChatMessage[]) => void;
  setMode: (mode: ChatMode) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setOpen: (open: boolean) => void;

  // Bulk actions
  reset: () => void;
  clearMessages: () => void;
  clearError: () => void;
}

const initialState = {
  sessionId: null,
  messages: [],
  currentMode: "normal" as ChatMode,
  isLoading: false,
  error: null,
  isOpen: false,
};

export const useChatStore = create<ChatStore>((set) => ({
  ...initialState,

  setSessionId: (id: string) => set({ sessionId: id }),

  addMessage: (message: ChatMessage) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),

  setMessages: (messages: ChatMessage[]) => set({ messages }),

  setMode: (mode: ChatMode) =>
    set({
      currentMode: mode,
      messages: [], // Clear messages when switching modes
    }),

  setLoading: (loading: boolean) => set({ isLoading: loading }),

  setError: (error: string | null) => set({ error }),

  setOpen: (open: boolean) => set({ isOpen: open }),

  reset: () => set(initialState),

  clearMessages: () => set({ messages: [] }),

  clearError: () => set({ error: null }),
}));

/**
 * Selector для получения только необходимого состояния
 */
export const useChatMessages = () =>
  useChatStore((state) => ({ messages: state.messages, isLoading: state.isLoading }));

export const useChatMode = () =>
  useChatStore((state) => ({ mode: state.currentMode }));

export const useChatSession = () =>
  useChatStore((state) => ({ sessionId: state.sessionId }));

export const useChatError = () =>
  useChatStore((state) => ({ error: state.error }));
