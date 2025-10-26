"use client"

import { useState, useEffect } from "react";
import { PromptTemplate, PerformanceResponse } from "@/types/prompts";
import TemplateForm from "./TemplateForm";
import { Plus, Edit, Trash2, BarChart3, FileText, RefreshCw } from "lucide-react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";

export default function PromptTemplates({ promptTemplates, performanceData }: { promptTemplates: PromptTemplate[], performanceData: PerformanceResponse }) {
  const [templates, setTemplates] = useState<PromptTemplate[]>(promptTemplates);
  const [performanceDataState, setPerformanceDataState] = useState<PerformanceResponse>(performanceData);
  const [showForm, setShowForm] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<PromptTemplate | undefined>();
  const [isLoading, setIsLoading] = useState(false);

  // Function to refresh performance data
  const refreshPerformanceData = async () => {
    try {
      const response = await fetch("http://localhost:8000/templates/performance");
      if (response.ok) {
        const data = await response.json();
        setPerformanceDataState(data);
      }
    } catch (error) {
      console.error("Error fetching performance data:", error);
    }
  };

  // Refresh performance data on component mount
  useEffect(() => {
    refreshPerformanceData();
  }, []);

  // Periodically refresh performance data to catch new questions
  useEffect(() => {
    const interval = setInterval(() => {
      refreshPerformanceData();
    }, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, []);


  const handleCreate = async (templateData: Omit<PromptTemplate, 'id' | 'created_at'>) => {
    setIsLoading(true);
    try {
      const response = await fetch("http://localhost:8000/templates/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(templateData),
      });
      
      if (response.ok) {
        const newTemplate = await response.json();
        setTemplates([...templates, newTemplate]);
        setShowForm(false);
        // Refresh performance data after creating a new template
        await refreshPerformanceData();
      }
    } catch (error) {
      console.error("Error creating template:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdate = async (templateData: Omit<PromptTemplate, 'id' | 'created_at'>) => {
    if (!editingTemplate) return;
    
    setIsLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/templates/${editingTemplate.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(templateData),
      });
      
      if (response.ok) {
        const updatedTemplate = await response.json();
        setTemplates(templates.map(t => t.id === editingTemplate.id ? updatedTemplate : t));
        setEditingTemplate(undefined);
        setShowForm(false);
        // Refresh performance data after updating a template
        await refreshPerformanceData();
      }
    } catch (error) {
      console.error("Error updating template:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this template?")) return;
    
    setIsLoading(true);
    try {
      const response = await fetch(`http://localhost:8000/templates/${id}`, {
        method: "DELETE",
      });
      
      if (response.ok) {
        setTemplates(templates.filter(t => t.id !== id));
        // Refresh performance data after deleting a template
        await refreshPerformanceData();
      }
    } catch (error) {
      console.error("Error deleting template:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center gap-3">
            <FileText className="w-6 h-6 text-gray-600" />
            <h1 className="text-2xl font-semibold text-gray-800">Template Management</h1>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={refreshPerformanceData}
              className="flex items-center gap-2 bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Refresh Data</span>
            </button>
            <button
              onClick={() => setShowForm(true)}
              className="flex items-center gap-2 bg-gray-800 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              <span>New Template</span>
            </button>
          </div>
        </div>

        {/* Performance Overview */}
        <div className="mb-8">
          <div className="flex items-center gap-2 mb-6">
            <BarChart3 className="w-5 h-5 text-gray-600" />
            <h2 className="text-lg font-semibold text-gray-800">Performance Overview</h2>
          </div>
          
          {/* Combined Line Chart for All Questions */}
          {performanceDataState.by_question && Array.isArray(performanceDataState.by_question) && performanceDataState.by_question.length > 0 ? (
            <div className="mb-8">
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-sm font-medium text-gray-700 mb-4">Template Performance Across Questions</h3>
                <div style={{ width: '100%', height: '320px', minHeight: '320px' }}>
                  <ResponsiveContainer width="100%" height={320}>
                    <LineChart data={(() => {
                      // Collect all unique templates from all questions
                      const uniqueTemplates = new Map();
                      performanceDataState.by_question.forEach(question => {
                        question.template_performance?.forEach(template => {
                          if (!uniqueTemplates.has(template.template_id)) {
                            uniqueTemplates.set(template.template_id, template);
                          }
                        });
                      });
                      
                      const allTemplates = Array.from(uniqueTemplates.values());
                      
                      // Create data points for each question with all template win rates
                      return performanceDataState.by_question.map(question => {
                        const dataPoint: Record<string, string | number> = {
                          question: `Q${question.question_id}`,
                          questionText: question.question_text
                        };
                        
                        // Initialize all templates with 0 win rate
                        allTemplates.forEach(template => {
                          dataPoint[template.template_name] = 0;
                        });
                        
                        // Override with actual win rates from this question
                        question.template_performance?.forEach(template => {
                          dataPoint[template.template_name] = template.win_rate;
                        });
                        
                        return dataPoint;
                      });
                    })()}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis 
                        dataKey="question" 
                        tick={{ fontSize: 12, fill: '#6b7280' }}
                        tickMargin={8}
                      />
                      <YAxis 
                        tick={{ fontSize: 12, fill: '#6b7280' }}
                        domain={[0, 100]}
                        label={{ value: 'Win Rate (%)', angle: -90, position: 'insideLeft' }}
                      />
                      <Tooltip 
                        contentStyle={{
                          backgroundColor: '#f9fafb',
                          border: '1px solid #e5e7eb',
                          borderRadius: '6px',
                          fontSize: '12px'
                        }}
                        formatter={(value: number, name: string) => [`${value.toFixed(1)}%`, name]}
                        labelFormatter={(label, payload) => {
                          const data = payload?.[0]?.payload;
                          return data ? `Question ${data.question}: ${data.questionText}` : label;
                        }}
                      />
                      <Legend />
                      {/* Generate lines for each unique template */}
                      {(() => {
                        // Collect all unique templates from all questions
                        const uniqueTemplates = new Map();
                        performanceDataState.by_question.forEach(question => {
                          question.template_performance?.forEach(template => {
                            if (!uniqueTemplates.has(template.template_id)) {
                              uniqueTemplates.set(template.template_id, template);
                            }
                          });
                        });
                        
                        const allTemplates = Array.from(uniqueTemplates.values());
                        const colors = ['#374151', '#6b7280', '#9ca3af', '#d1d5db', '#f3f4f6', '#4b5563'];
                        
                        return allTemplates.map((template, index) => (
                          <Line
                            key={template.template_id}
                            type="monotone"
                            dataKey={template.template_name}
                            stroke={colors[index % colors.length]}
                            strokeWidth={2}
                            dot={{ fill: colors[index % colors.length], strokeWidth: 2, r: 4 }}
                            activeDot={{ r: 6, stroke: colors[index % colors.length], strokeWidth: 2 }}
                          />
                        ));
                      })()}
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          ) : (
            /* Fallback to Overall Performance */
            <div className="mb-8">
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-sm font-medium text-gray-700 mb-4">Overall Performance</h3>
                <div style={{ width: '100%', height: '256px', minHeight: '256px' }}>
                  <ResponsiveContainer width="100%" height={256}>
                    <LineChart data={performanceDataState.overall.map(template => ({
                      name: template.template_name,
                      winRate: template.win_rate,
                      wins: template.wins,
                      totalDuels: template.total_duels,
                      key: template.template_key
                    }))}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                      <XAxis 
                        dataKey="name" 
                        tick={{ fontSize: 12, fill: '#6b7280' }}
                        angle={-45}
                        textAnchor="end"
                        height={80}
                      />
                      <YAxis 
                        tick={{ fontSize: 12, fill: '#6b7280' }}
                        domain={[0, 100]}
                      />
                      <Tooltip 
                        contentStyle={{
                          backgroundColor: '#f9fafb',
                          border: '1px solid #e5e7eb',
                          borderRadius: '6px',
                          fontSize: '12px'
                        }}
                        formatter={(value: number) => [`${value.toFixed(1)}%`, 'Win Rate']}
                        labelFormatter={(label) => `Template: ${label}`}
                      />
                      <Line 
                        type="monotone" 
                        dataKey="winRate" 
                        stroke="#374151" 
                        strokeWidth={2}
                        dot={{ fill: '#374151', strokeWidth: 2, r: 4 }}
                        activeDot={{ r: 6, stroke: '#374151', strokeWidth: 2 }}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          )}

          {/* Performance Cards */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {performanceDataState.overall.slice(0, 6).map((template) => (
              <div key={template.template_id} className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 transition-colors">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-gray-800 text-sm truncate">{template.template_name}</h3>
                  <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                    {template.template_key}
                  </span>
                </div>
                <div className="flex items-center gap-2 mb-2">
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-gray-600 h-2 rounded-full transition-all duration-300" 
                      style={{ width: `${template.win_rate}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium text-gray-700">
                    {template.win_rate.toFixed(1)}%
                  </span>
                </div>
                <div className="text-xs text-gray-500">
                  {template.wins} wins / {template.total_duels} duels
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Templates List */}
        <div>
          <h2 className="text-lg font-semibold text-gray-800 mb-4">Templates</h2>
          {templates.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No templates found</p>
            </div>
          ) : (
            <div className="space-y-4">
              {templates.map((template) => (
                <div key={template.id} className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="font-medium text-gray-800">{template.name}</h3>
                        <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                          {template.key}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 mb-3 bg-gray-50 p-3 rounded">
                        {template.template_text}
                      </p>
                      <div className="text-xs text-gray-400">
                        Created {new Date(template.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                      <button
                        onClick={() => {
                          setEditingTemplate(template);
                          setShowForm(true);
                        }}
                        className="text-gray-400 hover:text-gray-600 transition-colors"
                      >
                        <Edit className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(template.id)}
                        className="text-gray-400 hover:text-red-600 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Form Modal */}
        {showForm && (
          <TemplateForm
            template={editingTemplate}
            onSave={editingTemplate ? handleUpdate : handleCreate}
            onCancel={() => {
              setShowForm(false);
              setEditingTemplate(undefined);
            }}
            isLoading={isLoading}
          />
        )}
      </div>
    </div>
  );
}