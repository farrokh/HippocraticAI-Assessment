"use client";

import type { QuestionType } from "@/types/question";
import Link from "next/link";

export default function QuestionsList({ 
    initialQuestions, 
    className 
}: { 
    initialQuestions: QuestionType[], 
    className?: string 
}) {
    const questions = initialQuestions;

    if (questions.length === 0) {
        return (
            <div className="text-gray-500 text-sm">No questions asked yet</div>
        );
    }

    return (
      <div className={`flex flex-col gap-1 ${className}`}>
        {questions.map((question) => (
          <Link
            key={question.id}
            href={`/questions/${question.id}`}
            className="flex items-start justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <div className="flex items-start gap-3 flex-1 min-w-0">
              {/* Question Text & Answer */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <p className="text-sm text-gray-700 line-clamp-2">
                    {question.text}
                  </p>
                  <p className="text-xs text-gray-400 mt-1">
                    {new Date(question.created_at).toLocaleDateString()} at{" "}
                    {new Date(question.created_at).toLocaleTimeString()}
                  </p>
                </div>
                {question.selected_generation?.output_text && (
                  <p className="text-xs text-gray-500 mt-1 line-clamp-2">
                    {question.selected_generation?.output_text}
                  </p>
                )}
              </div>
            </div>

            {/* Status Badge */}
            {question.selected_generation_id ? (
              <div className="flex items-center gap-2 text-xs text-gray-500 bg-gray-50 px-3 py-1 rounded-full ml-2 flex-shrink-0">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Completed</span>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-xs text-gray-500 bg-gray-50 px-3 py-1 rounded-full ml-2 flex-shrink-0">
                <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
                <span>Pending</span>
              </div>
            )}
          </Link>
        ))}
      </div>
    );
}