import Comparison from "@/components/questions/Comparison";
import ProcessingQuestion from "@/components/questions/ProcessingQuestion";
import QuestionWithSelectedAnswer from "@/components/questions/QuestionWithSelectedAnswer";
import type { ComparisonType, QuestionResultsType } from "@/types/question";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

async function fetchQuestionResults(questionId: string): Promise<QuestionResultsType> {
  const response = await fetch(`${API_URL}/questions/${questionId}/results`);

  if (!response.ok) {
    throw new Error("Failed to fetch question");
  }

  return (await response.json()) as QuestionResultsType;
}

async function fetchNextDuel(questionId: string): Promise<ComparisonType | null> {
  const response = await fetch(`${API_URL}/questions/${questionId}/duels/next`);

  // Processing states - question is still being generated or all duels decided
  if (response.status === 202 || response.status === 204) {
    return null; // Signal to show processing state
  }

  // Real errors
  if (response.status === 404) {
    throw new Error("Question not found");
  }

  if (!response.ok) {
    throw new Error("Failed to fetch duel");
  }

  return (await response.json()) as ComparisonType;
}

function isValidComparison(comparison: ComparisonType | null): comparison is ComparisonType {
  return (
    comparison !== null &&
    comparison.question !== undefined &&
    comparison.generation_a !== undefined &&
    comparison.generation_b !== undefined
  );
}

export default async function QuestionPage({
  params,
}: {
  params: Promise<{ questionId: string }>;
}) {
  const { questionId } = await params;

  // Fetch question results to check for selected answer
  const questionData = await fetchQuestionResults(questionId);

  // If question already has a selected answer, show it
  if (questionData.selected_generation?.id) {
    return <QuestionWithSelectedAnswer question={questionData} />;
  }

  // Fetch next available duel for comparison
  const comparisonData = await fetchNextDuel(questionId);

  // If no duel available (still processing), show processing state
  if (!isValidComparison(comparisonData)) {
    return <ProcessingQuestion questionId={questionId} />;
  }

  // Show comparison interface
  return <Comparison comparison={comparisonData} />;
}
