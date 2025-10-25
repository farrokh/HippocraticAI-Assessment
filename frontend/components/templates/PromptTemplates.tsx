"use client"

import { PromptTemplate, PerformanceResponse } from "@/types/prompts";

export default function PromptTemplates({ promptTemplates, performanceData }: { promptTemplates: PromptTemplate[], performanceData: PerformanceResponse }) {
    return (
        <div className="p-8">
          {/* Win Rates Table */}
          <div className="mb-8">
            <h2 className="text-xl font-bold text-gray-700 mb-4">
              TEMPLATE WIN RATES
            </h2>
            <div className="bg-white border border-gray-300 rounded-lg overflow-hidden">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Template Name
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Key
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Wins
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Total Duels
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Win Rate
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {performanceData.overall.map((template) => (
                    <tr key={template.template_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {template.template_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {template.template_key}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {template.wins}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {template.total_duels}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="flex items-center">
                          <div className="flex-1 bg-gray-200 rounded-full h-2 mr-3">
                            <div 
                              className="bg-green-500 h-2 rounded-full" 
                              style={{ width: `${template.win_rate}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-medium text-gray-900">
                            {template.win_rate.toFixed(1)}%
                          </span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* List of Prompt Templates (TODO: Implement pagination) */}
          <div>
            <h2 className="text-lg font-semibold text-gray-700 mb-4">
              LIST OF PROMPT TEMPLATES
            </h2>
            <div className="bg-white border border-gray-300 rounded-lg">
              {promptTemplates.length === 0 ? (
                <div className="p-8 text-center text-gray-500">
                  No templates found
                </div>
              ) : (
                <div className="divide-y divide-gray-200">
                  {promptTemplates.map((template: PromptTemplate) => (
                    <div key={template.id} className="p-4 hover:bg-gray-50">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h3 className="font-medium text-gray-900">
                            {template.name}
                          </h3>
                          <p className="text-sm text-gray-500 mt-1">
                            Key: {template.key}
                          </p>
                          <p className="text-sm text-gray-600 mt-2 bg-gray-100 p-2 rounded">
                            {template.template_text}
                          </p>
                        </div>
                        <div className="ml-4 text-xs text-gray-400">
                          {new Date(template.created_at).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      );
}