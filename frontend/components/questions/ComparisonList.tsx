"use client";

  import type { ComparisonType } from "@/types/question";

export default function ComparisonList({ comparisons }: { comparisons: ComparisonType[] }) {
  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold text-gray-800">COMPARISON LIST</h1>
      <div className="grid grid-cols-2 gap-6">

        {comparisons.map((comparison) => (
            <div key={comparison.id} className="space-y-4">
                <h2 className="text-lg font-semibold text-gray-700"></h2>
               
                </div>
        ))}
      </div>
    </div>
  );
}