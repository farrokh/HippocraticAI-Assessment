"use client";

import { useState } from "react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Textarea } from "../ui/textarea";
import { X, Save, Loader2 } from "lucide-react";
import type { PromptTemplate } from "@/types/prompts";

interface TemplateFormProps {
  template?: PromptTemplate;
  onSave: (template: Omit<PromptTemplate, 'id' | 'created_at'>) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}

export default function TemplateForm({ template, onSave, onCancel, isLoading = false }: TemplateFormProps) {
  const [formData, setFormData] = useState({
    name: template?.name || "",
    key: template?.key || "",
    template_text: template?.template_text || "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name.trim() || !formData.key.trim() || !formData.template_text.trim()) {
      return;
    }
    await onSave(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-800">
              {template ? "Edit Template" : "Create Template"}
            </h2>
            <button
              onClick={onCancel}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Template Name
              </label>
              <Input
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Enter template name"
                className="w-full"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Template Key
              </label>
              <Input
                value={formData.key}
                onChange={(e) => setFormData({ ...formData, key: e.target.value })}
                placeholder="Enter template key (e.g., 'direct', 'cot_light')"
                className="w-full"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Template Text
              </label>
              <Textarea
                value={formData.template_text}
                onChange={(e) => setFormData({ ...formData, template_text: e.target.value })}
                placeholder="Enter the template text with {question} placeholder"
                className="w-full min-h-32"
                required
              />
            </div>

            <div className="flex gap-3 pt-4">
              <Button
                type="submit"
                disabled={isLoading || !formData.name.trim() || !formData.key.trim() || !formData.template_text.trim()}
                className="flex items-center gap-2 bg-gray-800 text-white hover:bg-gray-700"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Saving...</span>
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4" />
                    <span>{template ? "Update" : "Create"}</span>
                  </>
                )}
              </Button>
              <Button
                type="button"
                onClick={onCancel}
                className="border border-gray-300 text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
