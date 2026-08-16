/**
 * API Service - Handles all backend communication
 */

const API_BASE = '/api';

/**
 * Ask a question to the climate copilot
 */
export async function askQuestion({
  query,
  topK = 5,
  mode = 'hybrid',
  sourceFilter = null,
  includeSources = true,
  includeEvaluation = false,
  model = null   // null => server decides, via GROQ_MODEL in .env
}) {
  const response = await fetch(`${API_BASE}/ask`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      top_k: topK,
      mode,
      source_filter: sourceFilter,
      include_sources: includeSources,
      include_evaluation: includeEvaluation,
      model
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Search for passages without generating an answer
 */
export async function searchPassages({
  query,
  topK = 5,
  mode = 'hybrid',
  sourceFilter = null
}) {
  const response = await fetch(`${API_BASE}/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query,
      top_k: topK,
      mode,
      source_filter: sourceFilter
    }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Get available source documents
 */
export async function getSources() {
  const response = await fetch(`${API_BASE}/sources`);

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

/**
 * Health check
 */
export async function getHealth() {
  const response = await fetch(`${API_BASE}/health`);

  if (!response.ok) {
    throw new Error(`API is not available (HTTP ${response.status})`);
  }

  return response.json();
}
