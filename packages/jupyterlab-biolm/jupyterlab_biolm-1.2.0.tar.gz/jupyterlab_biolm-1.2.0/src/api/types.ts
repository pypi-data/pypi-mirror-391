/**
 * Type definitions for BioLM API responses
 */

export interface BioLMAPIModel {
  api_version: string;
  model_slug: string;
  model_name: string;
  community_model: boolean;
  company_model: boolean;
  predictor: boolean;
  encoder: boolean;
  transformer: boolean;
  explainer: boolean;
  generator: boolean;
  classifier: boolean;
  similarity: boolean;
  description: string;
  created_at: string;
  tags: string[];
  docs_link: string | null;
  api_docs_link: string | null;
  code_examples?: CodeExample[]; // Added for detail endpoint
}

export interface CodeExample {
  action: string;
  code: string;
  description?: string;
  [key: string]: any;
}

export interface BioLMModel {
  id: string;
  name: string;
  description?: string;
  tags: string[];
  apiVersion?: string;
  communityModel?: boolean;
  companyModel?: boolean;
  actions?: string[]; // Derived from boolean flags (predictor, encoder, etc.)
  apiDocsLink?: string | null;
  codeExamples?: CodeExample[]; // Added for code examples
  [key: string]: any; // Allow for additional metadata fields
}

export interface APIError {
  message: string;
  status?: number;
  code?: string;
}

