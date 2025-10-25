"use client";

import type { QuestionType } from "@/types/question";
import Link from "next/link";
import { useEffect, useEffectEvent, useState } from "react";

export default function QuestionsList({ limit = 10, className }: { limit?: number, className?: string }) {
    const [questions, setQuestions] = useState<QuestionType[]>([]);
    const fetchQuestions = useEffectEvent(async () => {
        const response = await fetch(`http://localhost:8000/questions?limit=${limit}`);
        const data = await response.json();
        setQuestions(data);
    });
    useEffect(() => {
        fetchQuestions();
    }, []);

    if (questions.length === 0) {
        return (
            <div className="flex flex-col w-full  overflow-y-auto h-full">
                <p className="text-gray-500 text-center text-sm">No questions asked yet</p>
            </div>
        )
    }

    return (
       
            <div className={`flex flex-col w-full  overflow-y-auto h-full ${className}`}>
                {questions.map((question) => (
                    <Link key={question.id} href={`/questions/${question.id}`} className="hover:font-bold p-2 rounded-lg block truncate" >
                        {question.text}
                    </Link>
                ))}
            </div>
        
    );
}