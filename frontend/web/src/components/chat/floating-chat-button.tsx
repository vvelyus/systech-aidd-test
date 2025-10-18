"use client";

import { Button } from "@/components/ui/button";
import { MessageCircle, X } from "lucide-react";

interface FloatingChatButtonProps {
  onToggle: (open: boolean) => void;
  isOpen?: boolean;
  unreadCount?: number;
}

export function FloatingChatButton({
  onToggle,
  isOpen = false,
  unreadCount = 0,
}: FloatingChatButtonProps) {
  return (
    <div className="fixed bottom-6 right-6 z-50">
      <Button
        onClick={() => onToggle(!isOpen)}
        size="lg"
        className={`rounded-full w-14 h-14 shadow-lg hover:shadow-xl transition-all ${
          isOpen
            ? "bg-red-500 hover:bg-red-600"
            : "bg-blue-500 hover:bg-blue-600"
        }`}
      >
        {isOpen ? (
          <X className="w-6 h-6" />
        ) : (
          <>
            <MessageCircle className="w-6 h-6" />
            {unreadCount > 0 && (
              <span className="absolute top-0 right-0 inline-flex items-center justify-center px-2 py-1 text-xs font-bold leading-none text-white transform translate-x-1/2 -translate-y-1/2 bg-red-600 rounded-full">
                {unreadCount}
              </span>
            )}
          </>
        )}
      </Button>
    </div>
  );
}
