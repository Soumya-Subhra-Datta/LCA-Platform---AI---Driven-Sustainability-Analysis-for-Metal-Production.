const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');

export class ApiError extends Error {
  constructor(message, status = 0, data = null) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

function getErrorMessage(data, fallback) {
  if (!data) return fallback;
  if (typeof data.detail === 'string') return data.detail;
  if (Array.isArray(data.detail)) {
    return data.detail
      .map((err) => (err && err.msg ? err.msg : String(err)))
      .join(' ');
  }
  if (data.message) return data.message;
  return fallback;
}

export async function apiRequest(path, { method = 'GET', body = null, token = null } = {}) {
  const headers = { Accept: 'application/json' };
  if (body !== null) headers['Content-Type'] = 'application/json';
  if (token) headers.Authorization = `Bearer ${token}`;

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers,
      body: body !== null ? JSON.stringify(body) : undefined,
    });
  } catch (err) {
    throw new ApiError(
      'Network error. Please check your connection and try again.',
      0,
    );
  }

  let data = null;
  try {
    data = await response.json();
  } catch (err) {
    data = null;
  }

  if (!response.ok) {
    if (response.status === 401) {
      throw new ApiError('Invalid email or password.', 401, data);
    }
    if (response.status === 409) {
      throw new ApiError(getErrorMessage(data, 'This account already exists.'), 409, data);
    }
    if (response.status >= 500) {
      throw new ApiError(
        'Something went wrong on our side. Please try again later.',
        response.status,
        data,
      );
    }
    throw new ApiError(getErrorMessage(data, 'Request failed. Please try again.'), response.status, data);
  }

  return data;
}
