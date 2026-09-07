// The httpOnly auth cookie is same-origin in every environment this app runs
// in: locally the Vite dev server proxies /api to the backend, and in prod
// frontend + /api share the same Vercel domain. So relative paths + credentials
// "include" is all that's ever needed - no CORS, no token juggling on the client.
const BASE_URL = ''

export class ApiError extends Error {
  status: number
  // Full JSON error body (e.g. duplicate attendance's `existing_id`, bulk's `errors[]`).
  body: Record<string, unknown> | null
  constructor(message: string, status: number, body: Record<string, unknown> | null = null) {
    super(message)
    this.status = status
    this.body = body
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })

  const isJson = res.headers.get('content-type')?.includes('application/json')
  const body = isJson ? await res.json() : null

  if (!res.ok) {
    throw new ApiError(body?.message ?? 'Something went wrong. Please try again.', res.status, body)
  }

  return body as T
}

export const api = {
  get: <T>(path: string) => request<T>(path, { method: 'GET' }),
  post: <T>(path: string, data?: unknown) =>
    request<T>(path, { method: 'POST', body: data !== undefined ? JSON.stringify(data) : undefined }),
  put: <T>(path: string, data?: unknown) =>
    request<T>(path, { method: 'PUT', body: data !== undefined ? JSON.stringify(data) : undefined }),
  patch: <T>(path: string, data?: unknown) =>
    request<T>(path, { method: 'PATCH', body: data !== undefined ? JSON.stringify(data) : undefined }),
  delete: <T>(path: string, data?: unknown) =>
    request<T>(path, { method: 'DELETE', body: data !== undefined ? JSON.stringify(data) : undefined }),
}
