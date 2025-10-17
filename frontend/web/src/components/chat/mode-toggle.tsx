"use client";

import { ChatMode } from "@/types/chat";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { AlertCircle } from "lucide-react";
import { useState } from "react";

interface ModeToggleProps {
  currentMode: ChatMode;
  onModeChange: (mode: ChatMode) => void;
}

export function ModeToggle({ currentMode, onModeChange }: ModeToggleProps) {
  const [showWarning, setShowWarning] = useState(false);

  const handleModeChange = (newMode: ChatMode) => {
    if (newMode !== currentMode) {
      setShowWarning(true);
      setTimeout(() => {
        onModeChange(newMode);
        setShowWarning(false);
      }, 500);
    }
  };

  return (
    <div className="flex items-center gap-3 p-3 bg-gray-50 border-b border-gray-200 rounded-t-lg">
      <span className="text-sm font-medium text-gray-700">Режим:</span>

      <div className="flex gap-2">
        <Button
          size="sm"
          variant={currentMode === "normal" ? "default" : "outline"}
          onClick={() => handleModeChange("normal")}
        >
          💬 Normal
        </Button>
        <Button
          size="sm"
          variant={currentMode === "admin" ? "default" : "outline"}
          onClick={() => handleModeChange("admin")}
        >
          ⚙️ Admin
        </Button>
      </div>

      {showWarning && (
        <div className="flex items-center gap-2 ml-auto text-sm text-amber-600 bg-amber-50 px-3 py-2 rounded">
          <AlertCircle className="w-4 h-4" />
          История будет иной в новом режиме
        </div>
      )}

      {currentMode === "admin" && (
        <Badge variant="secondary" className="ml-auto">
          SQL Query Debug Active
        </Badge>
      )}
    </div>
  );
}
