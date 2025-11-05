"use client";

import { useEffect, useState } from "react";
import { usePollDuels } from "@/hooks/usePollDuels";

interface ProcessingQuestionProps {
  questionId: string;
}

export default function ProcessingQuestion({ questionId }: ProcessingQuestionProps) {
  const [dots, setDots] = useState("");

  // Animate dots
  useEffect(() => {
    const interval = setInterval(() => {
      setDots(prev => prev.length >= 3 ? "" : prev + ".");
    }, 500);
    return () => clearInterval(interval);
  }, []);

  // Poll for duels to become available with exponential backoff
  usePollDuels({ questionId });

  return (
    <div className="p-8 h-full flex flex-col justify-center items-center gap-6">
      <div className="relative">
        <div className="animate-spin rounded-full h-16 w-16 border-4 border-gray-200 border-t-blue-600"></div>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="w-6 h-6 bg-blue-600 rounded-full animate-pulse"></div>
        </div>
      </div>
      
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Processing Question</h2>
        <p className="text-gray-600 text-lg">
          Generating AI responses{dots}
        </p>
        <p className="text-gray-500 text-sm mt-2 max-w-md">
          We&apos;re creating multiple AI responses and setting up comparisons. This usually takes 10-30 seconds.
        </p>
      </div>

      <div className="flex space-x-1 mt-4">
        <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
        <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
        <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
      </div>
    </div>
  );
}
