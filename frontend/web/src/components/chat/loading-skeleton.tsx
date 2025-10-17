"use client";

import { useEffect, useState } from "react";

interface LoadingSkeletonProps {
  count?: number;
  show?: boolean;
}

export function LoadingSkeleton({ count = 3, show = true }: LoadingSkeletonProps) {
  const [isVisible, setIsVisible] = useState(show);

  useEffect(() => {
    setIsVisible(show);
  }, [show]);

  if (!isVisible) return null;

  return (
    <div className="space-y-4 animate-fade-in">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="flex gap-3">
          {/* Avatar skeleton */}
          <div className="w-8 h-8 rounded-full bg-gray-300 flex-shrink-0 animate-pulse" />

          {/* Message skeleton */}
          <div className="flex flex-col gap-2 flex-1 max-w-[80%]">
            {/* Badge skeleton (optional) */}
            {Math.random() > 0.5 && (
              <div className="w-12 h-6 bg-gray-300 rounded-full animate-pulse" />
            )}

            {/* Message bubble skeleton */}
            <div className="space-y-2">
              {Array.from({ length: Math.floor(Math.random() * 2) + 2 }).map(
                (_, lineIdx) => (
                  <div
                    key={lineIdx}
                    className={`h-4 bg-gray-300 rounded animate-pulse ${
                      lineIdx === 0 ? "w-full" : "w-5/6"
                    }`}
                  />
                )
              )}
            </div>

            {/* Timestamp skeleton */}
            <div className="w-20 h-3 bg-gray-300 rounded animate-pulse mt-1" />
          </div>
        </div>
      ))}
    </div>
  );
}
