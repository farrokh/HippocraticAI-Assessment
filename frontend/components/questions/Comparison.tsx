"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import type { ComparisonType } from "@/types/question";
import { toast } from "sonner";
import NoComparison from "./NoComparison";
import ReactMarkdown from "react-markdown";
import { CheckCircle, Loader2, Trophy, Zap, Clock, Target } from "lucide-react";

// Word-by-word animation component with opacity
function TypingText({ text, speed = 100 }: { text: string; speed?: number }) {
  const [displayedWords, setDisplayedWords] = useState<string[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  
  // Split text into words
  const words = text.split(' ');

  useEffect(() => {
    if (currentIndex < words.length) {
      const timeout = setTimeout(() => {
        setDisplayedWords(prev => [...prev, words[currentIndex]]);
        setCurrentIndex(prev => prev + 1);
      }, speed);
      return () => clearTimeout(timeout);
    }
  }, [currentIndex, words, speed]);

  return (
    <div className="prose prose-sm max-w-none text-gray-700">
      <ReactMarkdown>
        {displayedWords.join(' ')}
      </ReactMarkdown>
    </div>
  );
}

export default function Comparison({  comparison }: { comparison: ComparisonType }) {
  const [currentComparison, setCurrentComparison] = useState<ComparisonType | null>(comparison);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const router = useRouter();

  const decideWinner = async (winnerId: number) => {
    if (!comparison) return;
    setIsLoading(true);

    try {
      const response = await fetch(
        `http://localhost:8000/questions/${currentComparison?.question.id}/duels/${currentComparison?.id}/decide`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ winner_id: winnerId }),
        }
      );

      if (response.ok) {
        setIsLoading(false);
        await fetchNextComparison();
      } else {
        throw new Error("Failed to decide winner");
      }
    } catch (error) {
      console.error("Error deciding winner:", error);
      toast.error("Error deciding winner");
      setIsLoading(false);
    }
  };

  const fetchNextComparison = async () => {
    if (!currentComparison) return;
    setIsLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/questions/${currentComparison.question.id}/duels/next`);
      if (!response.ok) {
        // If no more duels available, redirect to question page to show selected answer
        if (response.status === 404) {
          router.push(`/questions/${currentComparison.question.id}`);
          return;
        }
        throw new Error("Failed to fetch next comparison");
      }
      const data = await response.json();
      
      // Check if the response is the "No next duel found" message
      if (data.detail === "No next duel found") {
        // Redirect to question page to show selected answer
        router.push(`/questions/${currentComparison.question.id}`);
        return;
      } else {
        const nextComparison = data as ComparisonType;
        setCurrentComparison(nextComparison);
        setErrorMessage(null);
      }
    } catch (error) {
      console.error("Error fetching next comparison:", error);
      toast.error("Error fetching next comparison");
    } finally {
      setIsLoading(false);
    }
  };
  if (!currentComparison && !isLoading) {
    return <NoComparison message={errorMessage || "You've completed all available comparisons"} />;
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-linear-to-br from-gray-50 to-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="relative mb-6">
            <div className="animate-spin rounded-full h-16 w-16 border-4 border-gray-200 border-t-blue-600 mx-auto"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <Loader2 className="w-6 h-6 text-blue-600 animate-spin" />
            </div>
          </div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Loading Next Comparison</h2>
          <p className="text-gray-600">Preparing the next set of responses...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12 animate-fade-in">
          <div className="inline-flex items-center gap-2 mb-4">
            <Target className="w-6 h-6 text-gray-600" />
            <h1 className="text-2xl font-semibold text-gray-800">
              Compare AI Responses
            </h1>
          </div>
          <div className="max-w-4xl mx-auto">
            <h2 className="text-lg font-medium text-gray-700 mb-4">
              {currentComparison?.question.text}
            </h2>
            <div className="flex items-center justify-center gap-6 text-sm text-gray-500">
              <div className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                <span>{new Date(currentComparison?.created_at ?? "").toLocaleDateString()}</span>
              </div>
              <div className="flex items-center gap-1">
                <Zap className="w-4 h-4" />
                <span>Comparison #{currentComparison?.id}</span>
              </div>
            </div>
          </div>
        </div>

        {currentComparison?.winner_id ? (
          /* Winner Decided State */
          <div className="animate-slide-up">
            <div className="text-center mb-8">
              <div className="flex items-center justify-center gap-2 mb-2">
                <CheckCircle className="w-5 h-5 text-gray-600" />
                <span className="text-sm font-medium text-gray-600">Winner Decided</span>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
              {/* Response A */}
              <div className={`flex flex-col transition-all duration-300 ${
                currentComparison.winner_id === currentComparison.generation_a.id 
                  ? 'opacity-100' 
                  : 'opacity-50'
              }`}>
                <div className="flex-1 min-h-96">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-sm font-medium text-gray-600 uppercase tracking-wide">Response A</h3>
                    {currentComparison.winner_id === currentComparison.generation_a.id && (
                      <div className="flex items-center gap-1 text-xs font-medium text-gray-600">
                        <Trophy className="w-3 h-3" />
                        <span>WINNER</span>
                      </div>
                    )}
                  </div>
                  <TypingText key={`winner-a-${currentComparison.generation_a.id}`} text={currentComparison.generation_a.output_text} speed={20} />
                </div>
              </div>

              {/* Response B */}
              <div className={`flex flex-col transition-all duration-300 ${
                currentComparison.winner_id === currentComparison.generation_b.id 
                  ? 'opacity-100' 
                  : 'opacity-50'
              }`}>
                <div className="flex-1 min-h-96">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-sm font-medium text-gray-600 uppercase tracking-wide">Response B</h3>
                    {currentComparison.winner_id === currentComparison.generation_b.id && (
                      <div className="flex items-center gap-1 text-xs font-medium text-gray-600">
                        <Trophy className="w-3 h-3" />
                        <span>WINNER</span>
                      </div>
                    )}
                  </div>
                  <TypingText key={`winner-b-${currentComparison.generation_b.id}`} text={currentComparison.generation_b.output_text} speed={20} />
                </div>
              </div>
            </div>
          </div>
        ) : (
          /* Active Comparison State */
          <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto animate-slide-up">
            {/* Response A */}
            <div className="flex flex-col">
              <div className="flex-1 min-h-96 mb-8">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-medium text-gray-600 uppercase tracking-wide">Response A</h3>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                </div>
                <TypingText key={`active-a-${currentComparison?.generation_a.id}`} text={currentComparison?.generation_a.output_text || ""} speed={50} />
              </div>
              <button
                onClick={() => decideWinner(currentComparison?.generation_a.id ?? 0)}
                disabled={isLoading}
                className="w-full border border-gray-300 text-gray-700 py-2 px-4 text-sm font-medium hover:bg-gray-50 hover:border-gray-400 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 rounded-lg"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-3 h-3 animate-spin" />
                    <span>Processing...</span>
                  </>
                ) : (
                  <span>Select A</span>
                )}
              </button>
            </div>

            {/* Response B */}
            <div className="flex flex-col">
              <div className="flex-1 min-h-96 mb-8">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-sm font-medium text-gray-600 uppercase tracking-wide">Response B</h3>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-pulse"></div>
                </div>
                <TypingText key={`active-b-${currentComparison?.generation_b.id}`} text={currentComparison?.generation_b.output_text || ""} speed={50} />
              </div>
              <button
                onClick={() => decideWinner(currentComparison?.generation_b.id ?? 0)}
                disabled={isLoading}
                className="w-full border border-gray-300 text-gray-700 py-2 px-4 text-sm font-medium hover:bg-gray-50 hover:border-gray-400 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 rounded-lg"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-3 h-3 animate-spin" />
                    <span>Processing...</span>
                  </>
                ) : (
                  <span>Select B</span>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Instructions */}
        <div className="mt-12 text-center animate-fade-in-delayed">
          <p className="text-sm text-gray-500 max-w-2xl mx-auto">
            Read both responses carefully and select the one that provides the most accurate, 
            helpful, and well-structured answer to the question.
          </p>
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
        
        @keyframes fade-in-word {
          from { opacity: 0; transform: translateY(10px); }
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
        
        .animate-fade-in-word {
          animation: fade-in-word 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}