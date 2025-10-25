import Comparison from "@/components/questions/Comparison";
import ProcessingQuestion from "@/components/questions/ProcessingQuestion";
import QuestionWithSelectedAnswer from "@/components/questions/QuestionWithSelectedAnswer";
import type { ComparisonType, QuestionResultsType } from "@/types/question";

export default async function QuestionPage({ params }: { params: Promise<{ questionId: string }> }) {
  const { questionId } = await params;
  
  // First, fetch the question to check if it has a selected_generation_id
  const questionResponse = await fetch(
    `http://0.0.0.0:8000/questions/${questionId}/results`
  );
  
  if (!questionResponse.ok) {
    throw new Error("Failed to fetch question");
  }
  
  const questionData = (await questionResponse.json()) as QuestionResultsType;
  
  // Check if the question has a selected_generation_id in the response
  if (questionData.selected_generation?.id) {
    return <QuestionWithSelectedAnswer question={questionData} />;
  }
  
  // If no selected_generation_id, fetch the next duel
  const comparisonResponse = await fetch(`http://localhost:8000/questions/${questionId}/duels/next`);
  
  if (!comparisonResponse.ok) {
    if (comparisonResponse.status === 404) {
      // No duels available yet - show a loading/processing state
      return <ProcessingQuestion questionId={questionId} />;
    }
    throw new Error("Failed to fetch duel");
  }
  
  const comparisonData = (await comparisonResponse.json()) as ComparisonType;

  return <Comparison comparison={comparisonData} />;
}
