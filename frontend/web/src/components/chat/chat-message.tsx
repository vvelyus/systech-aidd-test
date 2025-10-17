"use client";

import { formatDistanceToNow } from "date-fns";
import { ru } from "date-fns/locale";
import ReactMarkdown from "react-markdown";
import { MessageRole, ChatMessage as ChatMessageType } from "@/types/chat";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Copy, Check, AlertCircle, Database } from "lucide-react";
import { useState, useMemo } from "react";

interface ChatMessageProps {
  message: ChatMessageType;
  isLoading?: boolean;
}

export function ChatMessage({ message, isLoading = false }: ChatMessageProps) {
  const isUser = message.role === "user";
  const [copied, setCopied] = useState(false);

  // Check if message contains SQL query (for admin mode)
  const sqlMatch = useMemo(() => {
    return message.content.match(/SQL Query:\s*(.+?)(?:\n\n|$)/s);
  }, [message.content]);

  const sqlQuery = sqlMatch?.[1]?.trim() || null;

  // Check if message is an error
  const isError = message.content.toLowerCase().includes("error");

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const formatTime = (date: Date | string) => {
    const dateObj = typeof date === "string" ? new Date(date) : date;
    return formatDistanceToNow(dateObj, { addSuffix: true, locale: ru });
  };

  // Render markdown content with code highlighting
  const renderContent = (content: string) => {
    // Special handling for rate limit error message
    if (content.includes("Лимит бесплатного плана исчерпан")) {
      const lines = content.split("\n");
      return (
        <div className="space-y-2">
          {lines.map((line, idx) => {
            if (line.match(/^\d+\./)) {
              // Numbered list item
              return (
                <div key={idx} className="ml-4">
                  {line}
                </div>
              );
            }
            if (line.trim() === "") {
              return <div key={idx} className="h-2"></div>;
            }
            return (
              <div key={idx}>
                {line}
              </div>
            );
          })}
        </div>
      );
    }

    if (sqlQuery) {
      // If there's a SQL query, show it and the rest separately
      const cleanContent = content.replace(/SQL Query:\s*.+?(?:\n\n|$)/s, "").trim();
      return (
        <div className="space-y-3">
          {sqlQuery && (
            <div className="bg-gray-900 text-gray-100 p-3 rounded font-mono text-xs overflow-x-auto">
              <div className="flex items-center justify-between mb-2">
                <span className="text-purple-400">{"<"} SQL Query {"/>"}</span>
                <button
                  onClick={() => copyToClipboard(sqlQuery)}
                  className="hover:text-purple-300 transition-colors"
                >
                  {copied ? (
                    <Check className="w-4 h-4" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                </button>
              </div>
              <pre className="whitespace-pre-wrap break-words">{sqlQuery}</pre>
            </div>
          )}
          {cleanContent && (
            <ReactMarkdown
              className="prose prose-sm max-w-none dark:prose-invert"
              components={{
                code: ({node, inline, className, children, ...props}) => (
                  <code
                    className={inline ? "bg-gray-200 px-1 rounded" : "bg-gray-100 p-2 rounded block overflow-x-auto"}
                    {...props}
                  >
                    {children}
                  </code>
                ),
              }}
            >
              {cleanContent}
            </ReactMarkdown>
          )}
        </div>
      );
    }

    return (
      <ReactMarkdown
        className="prose prose-sm max-w-none dark:prose-invert"
        components={{
          code: ({node, inline, className, children, ...props}) => (
            <code
              className={inline ? "bg-gray-200 px-1 rounded" : "bg-gray-100 p-2 rounded block overflow-x-auto"}
              {...props}
            >
              {children}
            </code>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    );
  };

  return (
    <div
      className={`flex gap-3 mb-4 animate-fade-in ${isUser ? "flex-row-reverse" : "flex-row"}`}
    >
      {/* Avatar */}
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
          isError
            ? "bg-red-500 text-white"
            : isUser
            ? "bg-blue-500 text-white"
            : "bg-purple-500 text-white"
        }`}
      >
        {isError ? "⚠️" : isUser ? "🧑" : "🤖"}
      </div>

      {/* Content */}
      <div className={`flex flex-col gap-2 max-w-[80%] ${isUser ? "items-end" : "items-start"}`}>
        {/* Badges */}
        <div className="flex gap-2">
          {message.mode === "admin" && !isUser && (
            <Badge variant="secondary" className="text-xs flex items-center gap-1">
              <Database className="w-3 h-3" />
              Admin
            </Badge>
          )}
          {isError && (
            <Badge variant="destructive" className="text-xs flex items-center gap-1">
              <AlertCircle className="w-3 h-3" />
              Error
            </Badge>
          )}
        </div>

        {/* Message content */}
        <div
          className={`px-4 py-3 rounded-lg prose-sm max-w-full ${
            isError
              ? "bg-red-100 text-red-900 border border-red-200"
              : isUser
              ? "bg-blue-100 text-blue-900 rounded-br-none"
              : "bg-gray-100 text-gray-900 rounded-bl-none"
          }`}
        >
          {isLoading ? (
            <div className="flex items-center gap-2">
              <div className="animate-pulse">
                <div className="h-4 bg-gray-300 rounded w-12"></div>
              </div>
              <span className="text-sm">typing...</span>
            </div>
          ) : (
            renderContent(message.content)
          )}
        </div>

        {/* Timestamp */}
        <span className="text-xs text-gray-500">
          {formatTime(message.timestamp)}
        </span>
      </div>
    </div>
  );
}
