"use client";

import { useState, useRef, useEffect } from "react";
import { Textarea } from "../ui/textarea";
import { Button } from "../ui/button";
import { useRouter } from "next/navigation";
import { Send, Loader2, Sparkles } from "lucide-react";

interface QuestionResponse {
  id: number;
}

export default function AskQuestion() {
  const [question, setQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const router = useRouter();
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [question]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setIsTyping(true);
    if (!question.trim()) return;

    try {
      // Step 1: Create the question
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/questions/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text: question }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Error response:", errorText);
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = (await response.json()) as QuestionResponse;
      console.log("Question created:", data);
      setQuestion("");

      // Navigate directly to the question page - it will handle showing comparison or processing state
      console.log("Navigating to question page");
      router.push(`/questions/${data.id}`);
    } catch (error) {
      console.error("Error creating question:", error);
    } finally {
      setIsLoading(false);
      setIsTyping(false);
    }
  };

  return (
    <div className="min-h-screen bg-linear-to-br from-gray-50 to-gray-100 flex items-center justify-center p-4">
      <div className="w-full max-w-2xl mx-auto">
        {/* Header with animation */}
        <div className="text-center mb-8 animate-fade-in">
          <div className="inline-flex items-center gap-2 mb-4">
            <Sparkles className="w-8 h-8 text-blue-600 animate-pulse" />
            <h1 className="text-4xl font-bold bg-linear-to-r from-gray-800 to-gray-600 bg-clip-text text-transparent">
              Ask a Question
            </h1>
          </div>
          <p className="text-gray-600 text-lg">
            Get AI-powered answers with competitive evaluation
          </p>
        </div>

        {/* Main form container */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden animate-slide-up">
          <form onSubmit={handleSubmit} className="p-6">
            <div className="relative">
              <Textarea
                ref={textareaRef}
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="What would you like to know? Ask any question..."
                className="w-full min-h-[120px] max-h-[300px] resize-none border-0 focus:ring-0 text-lg placeholder:text-gray-400 pr-12 transition-all duration-200"
                disabled={isLoading}
              />
              
              {/* Send button */}
              <div className="absolute bottom-3 right-3">
                <Button
                  type="submit"
                  size="sm"
                  disabled={!question.trim() || isLoading}
                  className="rounded-full w-10 h-10 p-0 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 transition-all duration-200 hover:scale-105"
                >
                  {isLoading ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </Button>
              </div>
            </div>

            {/* Loading animation */}
            {isTyping && (
              <div className="mt-4 flex items-center gap-2 text-blue-600 animate-fade-in">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                  <div className="w-2 h-2 bg-blue-600 rounded-full animate-bounce"></div>
                </div>
                <span className="text-sm font-medium">Processing your question...</span>
              </div>
            )}

            {/* Character count */}
            <div className="mt-4 text-right">
              <span className="text-xs text-gray-400">
                {question.length > 0 && `${question.length} characters`}
              </span>
            </div>
          </form>
        </div>

        {/* Example questions */}
        <div className="mt-8 animate-fade-in-delayed">
          <p className="text-sm text-gray-500 text-center mb-4">Try asking:</p>
          <div className="flex flex-wrap gap-2 justify-center">
            {[
              "How does photosynthesis work?",
              "Explain quantum computing",
              "What are the benefits of exercise?",
              "How to learn programming?"
            ].map((example, index) => (
              <button
                key={index}
                onClick={() => setQuestion(example)}
                className="px-3 py-1 text-sm bg-white border border-gray-200 rounded-full hover:bg-gray-50 hover:border-gray-300 transition-all duration-200 hover:scale-105"
                disabled={isLoading}
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Custom animations */}
      <style jsx>{`
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        @keyframes slide-up {
          from { opacity: 0; transform: translateY(40px); }
          to { opacity: 1; transform: translateY(0); }
        }
        
        .animate-fade-in {
          animation: fade-in 0.6s ease-out;
        }
        
        .animate-slide-up {
          animation: slide-up 0.8s ease-out;
        }
        
        .animate-fade-in-delayed {
          animation: fade-in 0.6s ease-out 0.3s both;
        }
      `}</style>
    </div>
  );
}