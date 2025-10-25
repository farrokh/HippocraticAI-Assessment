

import PromptsListsLoading from "@/components/templates/PromptsListsLoading";
import PromptTemplates from "@/components/templates/PromptTemplates";
import { PromptTemplate, PerformanceResponse } from "@/types/prompts";
import { Suspense } from "react";


export default async function PromptTemplatesPage() {
  // Fetch templates
  const templatesResponse = await fetch("http://localhost:8000/templates/");
  if (!templatesResponse.ok) {
    throw new Error("Failed to fetch templates");
  }
  const templates = (await templatesResponse.json()) as PromptTemplate[];

  // Fetch performance data
  const performanceResponse = await fetch("http://0.0.0.0:8000/templates/performance?overall_only=true");
  if (!performanceResponse.ok) {
    throw new Error("Failed to fetch performance data");
  }
  const performanceData = (await performanceResponse.json()) as PerformanceResponse;

  return(
    <Suspense fallback={<PromptsListsLoading />}>
      <PromptTemplates promptTemplates={templates} performanceData={performanceData} />
    </Suspense>
  )
}
