import QuestionsList from "@/components/questions/QuestionsList";
import QuestionsListSkeleton from "@/components/questions/QuestionsListSkeleton";
import { Suspense } from "react";
import type { QuestionType } from "@/types/question";

async function fetchQuestions(): Promise<QuestionType[]> {
  const response = await fetch(`http://localhost:8000/questions?details=true&limit=30`, {
    cache: 'no-store', // Ensure fresh data
  });
  
  if (!response.ok) {
    throw new Error("Failed to fetch questions");
  }
  
  return response.json();
}

async function QuestionsListWrapper() {
  const questions = await fetchQuestions();
  return <QuestionsList initialQuestions={questions} />;
}

export default function QuestionsPage() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Asked Questions</h1>
      <Suspense fallback={<QuestionsListSkeleton />}>
        <QuestionsListWrapper />
      </Suspense>
    </div>
  );
}
