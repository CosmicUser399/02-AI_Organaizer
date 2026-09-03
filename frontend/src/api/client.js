/**
 * API client for backend communication.
 * All requests go through Vite dev proxy: /api -> backend
 */

const API_BASE = '/api';
// Longer than backend OpenAI timeout so the server can reply first.
const DEFAULT_TIMEOUT_MS = 90000;

export class ApiError extends Error {
  constructor(message, status, data) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

function extractDetail(data) {
  if (!data) {
    return null;
  }
  const detail = data.detail;
  if (typeof detail === 'string' && detail.trim()) {
    return detail;
  }
  if (Array.isArray(detail)) {
    const parts = detail
      .map((item) => item?.msg || item?.message || '')
      .filter(Boolean);
    if (parts.length > 0) {
      return parts.join('; ');
    }
  }
  return null;
}

function messageForStatus(status, fallback) {
  if (status === 429) {
    return 'Слишком много запросов к OpenAI. Подождите немного.';
  }
  if (status === 502 || status === 503) {
    return 'Сервис OpenAI временно недоступен. Попробуйте позже.';
  }
  if (status === 504) {
    return 'Превышено время ожидания ответа AI. Попробуйте ещё раз.';
  }
  return fallback;
}

async function request(endpoint, options = {}) {
  const { timeoutMs = DEFAULT_TIMEOUT_MS, headers, ...fetchOptions } = options;
  const url = `${API_BASE}${endpoint}`;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  const defaultHeaders = { Accept: 'application/json' };
  if (fetchOptions.body !== undefined) {
    defaultHeaders['Content-Type'] = 'application/json';
  }

  const config = {
    ...fetchOptions,
    headers: {
      ...defaultHeaders,
      ...headers,
    },
    signal: controller.signal,
  };

  try {
    const response = await fetch(url, config);

    if (response.status === 204) {
      return null;
    }

    const data = await response.json().catch(() => null);

    if (!response.ok) {
      const fallback = `Ошибка запроса (${response.status})`;
      throw new ApiError(
        extractDetail(data) || messageForStatus(response.status, fallback),
        response.status,
        data
      );
    }

    return data;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    if (error?.name === 'AbortError') {
      throw new ApiError(
        'Превышено время ожидания ответа. Попробуйте ещё раз.',
        408,
        null
      );
    }
    throw new ApiError(
      'Нет связи с сервером. Проверьте, что backend запущен.',
      0,
      null
    );
  } finally {
    clearTimeout(timeoutId);
  }
}

export const api = {
  get: (endpoint, options = {}) =>
    request(endpoint, { method: 'GET', ...options }),
  post: (endpoint, data, options = {}) =>
    request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
      ...options,
    }),
  patch: (endpoint, data, options = {}) =>
    request(endpoint, {
      method: 'PATCH',
      body: JSON.stringify(data),
      ...options,
    }),
  delete: (endpoint, options = {}) =>
    request(endpoint, { method: 'DELETE', ...options }),
};

export default api;
