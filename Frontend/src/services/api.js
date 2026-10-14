import { formatValidationError } from '../utils/apiErrors.js';

export const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
export const API_ENABLED = Boolean(API_BASE_URL);
export const AUTH_TOKEN_KEY = 'pageturners-token';

export async function apiRequest(path, options = {}) {
  if (!API_ENABLED) {
    throw new Error('VITE_API_BASE_URL is not configured.');
  }

  const headers = new Headers(options.headers);
  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const token = localStorage.getItem(AUTH_TOKEN_KEY);
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  if (!response.ok) {
    let message = `API request failed (${response.status}).`;
    try {
      const body = await response.json();
      const detail = body.detail;
      message = Array.isArray(detail)
        ? detail.map(formatValidationError).join(' ')
        : typeof detail === 'string'
          ? detail
          : message;
    } catch {
      // Keep the status-based message when the server does not return JSON.
    }
    throw new Error(message);
  }

  if (response.status === 204) return null;
  return response.json();
}

export const apiGet = (path) => apiRequest(path);
export const apiPost = (path, body) =>
  apiRequest(path, { method: 'POST', body: JSON.stringify(body) });
