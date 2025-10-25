"use client";

import type { GenerationPerformanceType, QuestionResultsType } from "@/types/question";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import ReactMarkdown from "react-markdown";

export default function QuestionWithSelectedAnswer({ question }: { question: QuestionResultsType }) {
    const otherGenerations = question.generation_performance.filter((gen: GenerationPerformanceType) => 
        gen.generation_id !== question.selected_generation?.id
      )
    const templateName = question.generation_performance.find(
      (gen: GenerationPerformanceType) =>
        gen.generation_id === question.selected_generation?.id
    )?.template_name;
    return (
      <div className="p-8">
        <div className="flex justify-between items-start mb-4">
          <h1 className="text-2xl font-bold text-gray-800">{question.question.text}</h1>
          {question.selected_generation && (
            <div className="flex items-center gap-2 text-sm text-gray-500 bg-gray-50 px-3 py-1 rounded-full">
              <div className="w-2 h-2 bg-green-500 rounded-full"></div>
              <span>Selected Answer</span>
            </div>
          )}
        </div>
        
        {question.selected_generation && (
          <div className="mb-4">
            <Accordion type="single" collapsible className="w-full">
              <AccordionItem value="selected-details" >
                <AccordionTrigger className="px-3 py-2 hover:cursor-pointer ">
                  <div className="flex items-center gap-2 ">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="font-medium text-green-800">Selected Answer Details</span>
                  </div>
                </AccordionTrigger>
                <AccordionContent className="px-3 pb-3">
                  <div className="text-sm text-gray-400">
                    <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
                      <div>
                        <span className="font-medium">Model:</span>
                        <br />
                        <span className="text-gray-600">{question.selected_generation.llm_model}</span>
                      </div>
                      <div>
                        <span className="font-medium">Template:</span>
                        <br />
                        <span className="text-gray-600">{templateName}</span>
                      </div>
                      <div>
                        <span className="font-medium">Tokens:</span>
                        <br />
                        <span className="text-gray-600">{question.selected_generation.output_tokens}</span>
                      </div>
                      <div>
                        <span className="font-medium">Latency:</span>
                        <br />
                        <span className="text-gray-600">{(question.selected_generation.latency * 1000).toFixed(0)}ms</span>
                      </div>
                      <div>
                        <span className="font-medium">Win Rate:</span>
                        <br />
                        <span className="text-green-600 font-semibold">100%</span>
                      </div>
                      <div>
                        <span className="font-medium">Created:</span>
                        <br />
                        <span className="text-gray-600">
                          {new Date(question.selected_generation.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>
            </Accordion>
          </div>
        )}
        <div className="mt-4">
          <div className="text-gray-700 prose prose-sm max-w-none">
            <ReactMarkdown>{question.selected_generation?.output_text || ""}</ReactMarkdown>
          </div>
        </div>
        
        {otherGenerations.length > 0 && (
          <div className="mt-8">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Other Answers</h2>
            <Accordion type="single" collapsible className="w-full">
              {otherGenerations.map((generation) => (
                <AccordionItem key={generation.generation_id} value={`item-${generation.generation_id}`}>
                  <AccordionTrigger className="text-left">
                    <div className="flex flex-col items-start">
                      <span className="font-medium">{generation.template_name}</span>
                      <div className="flex flex-wrap gap-4 text-sm text-gray-500 mt-1">
                        <span>Model: {generation.llm_model}</span>
                        <span>Tokens: {generation.output_tokens}</span>
                        <span>Latency: {(generation.latency * 1000).toFixed(0)}ms</span>
                        <span className="text-green-600">Win Rate: {generation.win_rate.toFixed(1)}%</span>
                      </div>
                    </div>
                  </AccordionTrigger>
                  <AccordionContent>
                    <div className="text-gray-700 prose prose-sm max-w-none pt-2">
                      <ReactMarkdown>{generation.output_text}</ReactMarkdown>
                    </div>
                  </AccordionContent>
                </AccordionItem>
              ))}
            </Accordion>
          </div>
        )}
        
      </div>
    );
}