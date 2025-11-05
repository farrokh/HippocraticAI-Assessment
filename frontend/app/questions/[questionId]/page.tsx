import Comparison from "@/components/questions/Comparison";
import ProcessingQuestion from "@/components/questions/ProcessingQuestion";
import QuestionWithSelectedAnswer from "@/components/questions/QuestionWithSelectedAnswer";
import type { ComparisonType, QuestionResultsType } from "@/types/question";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

/**
 * Fetches question results including selected generation if available.
 * cache: 'no-store' ensures fresh data after router.refresh()
 */
async function fetchQuestionResults(questionId: string): Promise<QuestionResultsType> {
  const response = await fetch(`${API_URL}/questions/${questionId}/results`, {
    cache: 'no-store'
  });

  if (!response.ok) {
    throw new Error("Failed to fetch question results");
  }

  return response.json();
}

/**
 * Fetches the next available duel for comparison.
 * Returns null if still processing (202) or all duels completed (204)
 */
async function fetchNextDuel(questionId: string): Promise<ComparisonType | null> {
  const response = await fetch(`${API_URL}/questions/${questionId}/duels/next`, {
    cache: 'no-store'
  });

  // Still processing or all duels completed - show processing state
  if (response.status === 202 || response.status === 204) {
    return null;
  }

  if (response.status === 404) {
    throw new Error("Question not found");
  }

  if (!response.ok) {
    throw new Error("Failed to fetch duel");
  }

  return response.json();
}

/**
 * Server component that determines which UI to render based on question state:
 * 1. QuestionWithSelectedAnswer - if winner has been selected
 * 2. Comparison - if duels are available for decision
 * 3. ProcessingQuestion - if still generating or processing
 */
export default async function QuestionPage({
  params,
}: {
  params: Promise<{ questionId: string }>;
}) {
  const { questionId } = await params;

  // Check if question has been fully processed with a winner
  const questionData = await fetchQuestionResults(questionId);

  if (questionData.selected_generation?.id) {
    return <QuestionWithSelectedAnswer question={questionData} />;
  }

  // Try to fetch next duel for comparison
  const comparisonData = await fetchNextDuel(questionId);

  if (!comparisonData) {
    // Still processing or waiting for duels to be generated
    return <ProcessingQuestion questionId={questionId} />;
  }

  // Show comparison interface
  return <Comparison comparison={comparisonData} />;
}
