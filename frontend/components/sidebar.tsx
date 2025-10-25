"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import QuestionsList from "./questions/QuestionsList";

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="w-64 bg-gray-100 border-r border-gray-200 flex flex-col h-full">
      {/* Score Board */}
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-800">
          LLM Tournament Widget
        </h2>
      </div>
      {/* Navigation */}
      <div className="flex-1 p-4">
        <Link
          href="/questions"
          className={`block w-full text-left px-3 py-2 rounded text-sm font-medium mb-2 ${
            pathname === "/questions"
              ? "bg-blue-100 text-blue-700"
              : "text-gray-600 hover:bg-gray-50"
          }`}
        >
          Questions
        </Link>
        <Link
          href="/templates"
          className={`block w-full text-left px-3 py-2 rounded text-sm font-medium mb-2 ${
            pathname === "/templates"
              ? "bg-blue-100 text-blue-700"
              : "text-gray-600 hover:bg-gray-50"
          }`}
        >
          Prompt Templates
        </Link>
      </div>

      {/* Ask Section */}
      <div className="p-4 border-b border-gray-200 h-full">
        <h3 className="text-sm font-medium text-gray-600 mb-2">
          Recent Questions
        </h3>
        <QuestionsList limit={10} className="text-sm text-gray-600 " />
      </div>
      <div className="p-4">
      <Link
        href="/"
        className={`block w-full text-left px-3 py-2 rounded text-sm font-medium mb-2 ${
          pathname === "/"
            ? "bg-blue-100 text-blue-700"
            : "text-gray-600 hover:bg-gray-50"
        }`}
      >
        Ask a New Question
      </Link>
      </div>
    </div>
  );
}
