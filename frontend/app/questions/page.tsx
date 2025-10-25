import QuestionsList from "@/components/questions/QuestionsList";

export default function QuestionsPage() {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">List of Asked Questions</h1>
      <QuestionsList limit={10} />
    </div>
  );
}
