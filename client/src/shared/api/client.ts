let accessToken: string | null = null
let pendingRefresh: Promise<string | null> | null = null
let sessionLost: (() => void) | null = null
let authEpoch = 0

export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message) }
}

export function setAccessToken(token: string | null) { authEpoch += 1; accessToken = token }
export function onSessionLost(callback: (() => void) | null) { sessionLost = callback }

async function messageFrom(response: Response): Promise<string> {
  try {
    const body: unknown = await response.json()
    if (body && typeof body === 'object' && 'detail' in body) {
      const detail = body.detail
      if (typeof detail === 'string') return detail
      if (Array.isArray(detail)) {
        const names: Record<string, string> = {
          last_name: 'Фамилия', first_name: 'Имя', patronymic: 'Отчество',
          name: 'ФИО', password: 'Пароль', role: 'Роль', title: 'Название',
          date: 'Дата', time: 'Время', duration_minutes: 'Продолжительность',
          athlete_public_id: 'Спортсмен', attendance: 'Посещаемость',
        }
        const reasons: Record<string, string> = {
          missing: 'обязательное поле', string_too_short: 'слишком короткое значение',
          string_too_long: 'слишком длинное значение', greater_than: 'значение должно быть больше нуля',
          literal_error: 'недопустимое значение', uuid_parsing: 'недопустимый идентификатор',
        }
        return detail.map((item: { loc?: unknown[]; type?: string }) => {
          const key = String(item.loc?.[item.loc.length - 1] ?? '')
          return `${names[key] ?? 'Поле'}: ${reasons[item.type ?? ''] ?? 'проверьте значение'}`
        }).join('; ')
      }
    }
  } catch { /* The server may return an empty or non-JSON response. */ }
  return response.status >= 500 ? 'Ошибка сервера. Попробуйте позже.' : `Ошибка запроса (${response.status})`
}

async function send(path: string, init: RequestInit = {}, token: string | null = accessToken): Promise<Response> {
  try {
    return await fetch(`/api/v1${path}`, {
      ...init,
      credentials: 'same-origin',
      headers: {
        ...(init.body ? { 'Content-Type': 'application/json' } : {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...init.headers,
      },
    })
  } catch {
    throw new ApiError(0, 'Нет соединения с сервером. Проверьте запуск backend.')
  }
}

export async function refreshSession(): Promise<string | null> {
  if (!pendingRefresh) {
    const epoch = authEpoch
    pendingRefresh = (async () => {
      const response = await send('/auth/refresh', { method: 'POST' }, null)
      if (!response.ok) {
        if (response.status === 401) {
          if (epoch === authEpoch) accessToken = null
          return null
        }
        throw new ApiError(response.status, await messageFrom(response))
      }
      const result = await response.json() as { access_token: string }
      if (epoch !== authEpoch) return null
      accessToken = result.access_token
      return accessToken
    })().finally(() => { pendingRefresh = null })
  }
  return pendingRefresh
}

export async function api<T>(path: string, init: RequestInit = {}, retry = true): Promise<T> {
  let response = await send(path, init)
  if (response.status === 401 && retry && !path.startsWith('/auth/')) {
    const token = await refreshSession()
    if (token) response = await send(path, init, token)
    else sessionLost?.()
  }
  if (!response.ok) {
    if (response.status === 401 && !path.startsWith('/auth/')) sessionLost?.()
    throw new ApiError(response.status, await messageFrom(response))
  }
  if (response.status === 204) return undefined as T
  return await response.json() as T
}

export async function signIn(name: string, password: string): Promise<string> {
  const result = await api<{ access_token: string }>('/auth/login', {
    method: 'POST', body: JSON.stringify({ name, password }),
  }, false)
  setAccessToken(result.access_token)
  return result.access_token
}

export async function signOut(): Promise<void> {
  try {
    let response = await send('/auth/logout', { method: 'POST' })
    if (response.status === 401 && await refreshSession()) response = await send('/auth/logout', { method: 'POST' })
    if (!response.ok) throw new ApiError(response.status, await messageFrom(response))
  } finally { setAccessToken(null) }
}
