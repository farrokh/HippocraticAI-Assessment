export interface QuestionType {
  id: number;
  text: string;
  created_at: string;
  selected_generation_id: number | null;
  selected_generation?: GenerationType;
}

export interface GenerationType {
  id: number;
  output_text: string;
  latency: number;
  input_tokens: number;
  template_id: number;
  question_id: number;
  llm_model: string;
  output_tokens: number;
  created_at: string;
}

export interface ComparisonType {
  id: number;
  winner_id: number | null;
  created_at: string;
  decided_at: string | null;
  question: QuestionType;
  generation_a: GenerationType;
  generation_b: GenerationType;
  selected_generation_id?: number;
}

export interface GenerationPerformanceType {
  generation_id: number;
  template_id: number;
  template_name: string;
  template_key: string;
  output_text: string;
  llm_model: string;
  latency: number;
  output_tokens: number;
  input_tokens: number;
  created_at: string;
  wins: number;
  total_duels: number;
  win_rate: number;
}

export interface QuestionResultsType {
  question: QuestionType;
  selected_generation: GenerationType;
  generation_performance: GenerationPerformanceType[];
}
