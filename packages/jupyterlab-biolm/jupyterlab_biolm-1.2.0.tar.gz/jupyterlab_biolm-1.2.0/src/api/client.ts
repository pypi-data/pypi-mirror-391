/**
 * BioLM API Client
 */
import { BioLMModel, BioLMAPIModel, APIError } from './types';

// Try direct API first, fall back to server proxy if CORS blocks
const MODELS_ENDPOINT_DIRECT = 'https://biolm.ai/api/ui/community-api-models/';
const MODELS_ENDPOINT_PROXY = '/biolm/api/models';
const TEST_CONNECTION_ENDPOINT_DIRECT = 'https://biolm.ai/api/ui/community-api-models/';
const TEST_CONNECTION_ENDPOINT_PROXY = '/biolm/api/test-connection';
const CACHE_TTL = 5 * 60 * 1000; // 5 minutes

interface CacheEntry {
  data: BioLMModel[];
  timestamp: number;
}

let cache: CacheEntry | null = null;

/**
 * Convert API model to internal model format
 */
function convertAPIModel(apiModel: BioLMAPIModel): BioLMModel {
  // Derive actions from boolean flags
  const actions: string[] = [];
  if (apiModel.predictor) actions.push('predict');
  if (apiModel.encoder) actions.push('encode');
  if (apiModel.generator) actions.push('generate');
  if (apiModel.classifier) actions.push('classify');
  if (apiModel.similarity) actions.push('similarity');
  if (apiModel.explainer) actions.push('explain');
  if (apiModel.transformer) actions.push('transform');
  
  // If no specific actions, default to predict
  if (actions.length === 0) {
    actions.push('predict');
  }

  return {
    id: apiModel.model_slug,
    name: apiModel.model_name,
    description: apiModel.description,
    tags: apiModel.tags || [],
    apiVersion: apiModel.api_version,
    communityModel: apiModel.community_model,
    companyModel: apiModel.company_model,
    actions: actions,
    apiDocsLink: apiModel.api_docs_link,
  };
}

/**
 * Fetch models from BioLM API
 */
export async function fetchModels(apiKey?: string): Promise<BioLMModel[]> {
  // Check cache first
  if (cache && Date.now() - cache.timestamp < CACHE_TTL) {
    return cache.data;
  }

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  // Try direct API first, fall back to proxy if CORS fails
  let url = MODELS_ENDPOINT_DIRECT;
  let useProxy = false;
  if (apiKey) {
    url += `?api_key=${encodeURIComponent(apiKey)}`;
    headers['Authorization'] = `Bearer ${apiKey}`;
  }

  // Always try proxy first in browser environment to avoid CORS issues
  // The proxy endpoint is same-origin so it won't have CORS problems
  console.log('[BioLM] Fetching models via server proxy...');
  useProxy = true;
  url = MODELS_ENDPOINT_PROXY;
  const proxyHeaders: HeadersInit = {
    'Content-Type': 'application/json',
  };
  if (apiKey) {
    url += `?api_key=${encodeURIComponent(apiKey)}`;
    proxyHeaders['Authorization'] = `Bearer ${apiKey}`;
  }

  try {
    let response = await fetch(url, {
      method: 'GET',
      headers: proxyHeaders,
      credentials: 'same-origin',
    });
    
    console.log('[BioLM] Proxy response received:', response.status);
    
    console.log('[BioLM] Response status:', response.status, response.statusText);
    console.log('[BioLM] Response URL:', response.url);
    console.log('[BioLM] Response ok:', response.ok);
    console.log('[BioLM] Using proxy:', useProxy);

    if (!response.ok) {
      // Try to get error details from response
      let errorMessage = `Failed to fetch models: ${response.status} ${response.statusText}`;
      let errorDetails: any = null;
      try {
        const text = await response.text();
        console.log('[BioLM] Error response body:', text);
        try {
          errorDetails = JSON.parse(text);
          if (errorDetails.message) {
            errorMessage = errorDetails.message;
          } else if (errorDetails.error) {
            errorMessage = errorDetails.error;
          }
        } catch {
          // If not JSON, use the text
          if (text) {
            errorMessage = `${errorMessage}: ${text.substring(0, 200)}`;
          }
        }
      } catch (e) {
        console.error('[BioLM] Error reading response:', e);
      }
      
      console.error('[BioLM] API Error:', errorMessage, errorDetails);
      const error: APIError = {
        message: errorMessage,
        status: response.status,
      };
      throw error;
    }

    const data: BioLMAPIModel[] = await response.json();
    
    // Convert API models to internal format
    const models: BioLMModel[] = Array.isArray(data)
      ? data.map(convertAPIModel)
      : [];

    // Update cache
    cache = {
      data: models,
      timestamp: Date.now(),
    };

    return models;
  } catch (error) {
    console.error('[BioLM] Proxy fetch failed:', error);
    
    // If we have cached data, return it even if stale
    if (cache) {
      console.warn('Using cached models due to fetch error:', error);
      return cache.data;
    }
    
    // Re-throw with more helpful error message
    if (error instanceof Error) {
      const errorMessage = error.message.includes('fetch') || error.message.includes('CORS') || error.message.includes('Failed to fetch')
        ? 'Unable to connect to BioLM API via server proxy. Please check your internet connection and ensure the server extension is loaded.'
        : error.message;
      
      const apiError: APIError = {
        message: errorMessage,
      };
      throw apiError;
    }
    throw error;
  }
}

/**
 * Clear the models cache
 */
export function clearCache(): void {
  cache = null;
}

/**
 * Fetch detailed model information including code examples
 */
export async function fetchModelDetails(
  modelSlug: string,
  apiKey?: string
): Promise<BioLMAPIModel> {
  // Always use proxy first to avoid CORS issues
  // The proxy endpoint is same-origin so it won't have CORS problems
  console.log('[BioLM] Fetching model details via server proxy...');
  let url = `/biolm/api/models/${modelSlug}`;
  const proxyHeaders: HeadersInit = {
    'Content-Type': 'application/json',
  };
  if (apiKey) {
    url += `?api_key=${encodeURIComponent(apiKey)}`;
    proxyHeaders['Authorization'] = `Bearer ${apiKey}`;
  }

  try {
    const response = await fetch(url, {
      method: 'GET',
      headers: proxyHeaders,
      credentials: 'same-origin',
    });
    
    console.log('[BioLM] Proxy response received:', response.status);

    if (!response.ok) {
      let errorMessage = `Failed to fetch model details: ${response.status} ${response.statusText}`;
      try {
        const text = await response.text();
        try {
          const errorDetails = JSON.parse(text);
          if (errorDetails.message) {
            errorMessage = errorDetails.message;
          } else if (errorDetails.error) {
            errorMessage = errorDetails.error;
          }
        } catch {
          if (text) {
            errorMessage = `${errorMessage}: ${text.substring(0, 200)}`;
          }
        }
      } catch (e) {
        console.error('[BioLM] Error reading response:', e);
      }
      
      const error: APIError = {
        message: errorMessage,
        status: response.status,
      };
      throw error;
    }

    const data: BioLMAPIModel = await response.json();
    return data;
  } catch (error) {
    console.error('[BioLM] Proxy fetch failed:', error);
    
    if (error instanceof Error) {
      const apiError: APIError = {
        message: error.message,
      };
      throw apiError;
    }
    throw error;
  }
}

/**
 * Test API connection with authentication
 */
export async function testConnection(apiKey: string): Promise<{ valid: boolean; message?: string; accountInfo?: any }> {
  // Try direct API first, fall back to proxy if CORS fails
  let url = TEST_CONNECTION_ENDPOINT_DIRECT;
  let useProxy = false;
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${apiKey}`,
  };

  try {
    // Try direct API call first
    let response: Response | null = null;
    let directFailed = false;
    
    try {
      response = await fetch(url, {
        method: 'GET',
        headers,
        mode: 'cors',
      });
      
      // Check if response indicates CORS failure
      if (response.status === 0 || response.type === 'opaque') {
        directFailed = true;
        response = null;
      }
    } catch (fetchError: any) {
      // CORS error - fetch throws before we get a response
      console.log('[BioLM] Direct API test failed with error:', fetchError.message);
      directFailed = true;
      response = null;
    }
    
    // If direct failed, use proxy
    if (directFailed || !response) {
      console.log('[BioLM] Using server proxy for connection test due to CORS/network issue...');
      useProxy = true;
      url = TEST_CONNECTION_ENDPOINT_PROXY;
      
      // Proxy expects POST with JSON body
      response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
        body: JSON.stringify({ api_key: apiKey }),
      });
    }

    if (response.ok) {
      const result = await response.json();
      return {
        valid: result.valid || false,
        message: result.message || 'Connection test completed',
        accountInfo: result.accountInfo,
      };
    } else {
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      try {
        const error = await response.json().catch(() => ({}));
        if (error.message) {
          errorMessage = error.message;
        }
      } catch (e) {
        // Ignore JSON parse errors
      }
      return {
        valid: false,
        message: errorMessage,
      };
    }
  } catch (error) {
    // If direct API failed with CORS, try server proxy
    if (!useProxy && error instanceof Error && 
        (error.message.includes('CORS') || error.message.includes('Failed to fetch') || error.message.includes('network'))) {
      console.log('[BioLM] CORS error detected for connection test, trying server proxy...');
      try {
        const proxyResponse = await fetch(TEST_CONNECTION_ENDPOINT_PROXY, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'same-origin',
          body: JSON.stringify({ api_key: apiKey }),
        });
        
        if (proxyResponse.ok) {
          const result = await proxyResponse.json();
          return {
            valid: result.valid || false,
            message: result.message || 'Connection test completed',
            accountInfo: result.accountInfo,
          };
        } else {
          const error = await proxyResponse.json().catch(() => ({}));
          return {
            valid: false,
            message: error.message || `HTTP ${proxyResponse.status}: ${proxyResponse.statusText}`,
          };
        }
      } catch (proxyError) {
        console.error('[BioLM] Proxy also failed:', proxyError);
      }
    }
    
    return {
      valid: false,
      message: error instanceof Error ? error.message : 'Connection failed',
    };
  }
}

