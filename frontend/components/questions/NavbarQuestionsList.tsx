"use client";

import type { QuestionType } from "@/types/question";
import Link from "next/link";
import { useEffect, useEffectEvent, useState } from "react";
import { useQuestionRefresh } from "@/contexts/QuestionRefreshContext";

export default function NavbarQuestionsList({ limit = 10, className }: { limit?: number, className?: string }) {
    const [questions, setQuestions] = useState<QuestionType[]>([]);
    const [statuses, setStatuses] = useState<Record<number, 'completed' | 'pending'>>({});
    const { refreshTrigger } = useQuestionRefresh();
    
    const fetchQuestions = useEffectEvent(async () => {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/questions/?limit=${limit}`);
        const data = await response.json();
        setQuestions(data);
        
        // Fetch status for each question
        const statusPromises = data.map(async (q: QuestionType) => {
            try {
                const statusResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/questions/${q.id}`);
                if (statusResponse.ok) {
                    const questionData = await statusResponse.json();
                    return { id: q.id, status: questionData.selected_generation_id ? 'completed' : 'pending' };
                }
            } catch (error) {
                console.error(`Error fetching status for question ${q.id}:`, error);
            }
            return { id: q.id, status: 'pending' };
        });
        
        const results = await Promise.all(statusPromises);
        const statusMap: Record<number, 'completed' | 'pending'> = {};
        results.forEach(({ id, status }) => {
            statusMap[id] = status;
        });
        setStatuses(statusMap);
    });
    
    useEffect(() => {
        fetchQuestions();
    }, [refreshTrigger]);

    if (questions.length === 0) {
        return (
            <div className="text-gray-500 text-sm">No questions asked yet</div>
        );
    }

    return (
        <div className={`flex flex-col gap-1  ${className}` }>
            {questions.map((question) => (
                <Link 
                    key={question.id} 
                    href={`/questions/${question.id}`} 
                    className="flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 transition-colors"
                >
                    <div className="flex items-start gap-3 flex-1 min-w-0">
                        {/* Status Dot */}
                        <div className="mt-1.5 shrink-0">
                            {statuses[question.id] === 'completed' ? (
                                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                            ) : (
                                <div className="w-2 h-2 bg-gray-300 rounded-full"></div>
                            )}
                        </div>
                        
                        {/* Question Text */}
                        <div className="flex-1 min-w-0">
                            <p className="text-sm text-gray-700 line-clamp-1">
                                {question.text}
                            </p>
                            
                        </div>
                    </div>
                    
                    
                </Link>
            ))}
        </div>
    );
}