export interface PromptTemplate {
  id: number;
  key: string;
  name: string;
  template_text: string;
  created_at: string;
}

export interface TemplatePerformance {
  template_id: number;
  template_name: string;
  template_key: string;
  wins: number;
  total_duels: number;
  win_rate: number;
}

export interface PerformanceResponse {
  overall: TemplatePerformance[];
}