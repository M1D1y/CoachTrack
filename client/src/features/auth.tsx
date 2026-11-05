import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import type { User, Role } from '../entities/types'
import { ApiError, api, onSessionLost, refreshSession, setAccessToken, signIn, signOut } from '../shared/api/client'

interface AuthContextValue {
  user: User | null
  status: 'loading' | 'guest' | 'ready' | 'error'
  error: string
  restore: () => Promise<void>
  login: (name: string, password: string) => Promise<void>
  register: (body: { last_name: string; first_name: string; patronymic: string; password: string; role: Role }) => Promise<void>
  logout: () => Promise<void>
  reloadUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [status, setStatus] = useState<AuthContextValue['status']>('loading')
  const [error, setError] = useState('')

  const reloadUser = async () => {
    const profile = await api<User>('/users/me')
    setUser(profile)
    setStatus('ready')
  }

  const restore = async () => {
    setStatus('loading')
    setError('')
    if (sessionStorage.getItem('coachtrack_signed_out') === '1') {
      setUser(null)
      setStatus('guest')
      return
    }
    try {
      const token = await refreshSession()
      if (token) await reloadUser()
      else { setUser(null); setStatus('guest') }
    } catch (cause) {
      setUser(null)
      if (cause instanceof ApiError && cause.status === 401) setStatus('guest')
      else {
        setStatus('error')
        setError(cause instanceof Error ? cause.message : 'Не удалось проверить сессию')
      }
    }
  }

  useEffect(() => {
    onSessionLost(() => { setAccessToken(null); setUser(null); setStatus('guest') })
    void restore()
    return () => onSessionLost(null)
  }, [])

  const login = async (name: string, password: string) => {
    await signIn(name, password)
    try { await reloadUser(); sessionStorage.removeItem('coachtrack_signed_out') }
    catch (cause) { setAccessToken(null); throw cause }
  }

  const register = async (body: { last_name: string; first_name: string; patronymic: string; password: string; role: Role }) => {
    await api<User>('/auth/register', { method: 'POST', body: JSON.stringify(body) }, false)
    try { await login(`${body.last_name} ${body.first_name} ${body.patronymic}`, body.password) }
    catch { throw new Error('Аккаунт создан. Выполните вход по ФИО и паролю.') }
  }

  const logout = async () => {
    try { await signOut() }
    finally {
      sessionStorage.setItem('coachtrack_signed_out', '1')
      setAccessToken(null); setUser(null); setStatus('guest')
    }
  }

  return <AuthContext.Provider value={{ user, status, error, restore, login, register, logout, reloadUser }}>
    {children}
  </AuthContext.Provider>
}

export function useAuth() {
  const value = useContext(AuthContext)
  if (!value) throw new Error('AuthProvider is missing')
  return value
}
