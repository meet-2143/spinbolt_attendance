import { api, ApiError } from '@/lib/api'
import type { User } from '@/types/user'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { createContext, useContext, useState, type ReactNode } from 'react'

interface LoginResponse {
  success: boolean
  user: User
}

interface AuthContextValue {
  user: User | null | undefined
  isLoading: boolean
  login: (email: string, password: string) => Promise<User>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient()
  const [checkedOnce, setCheckedOnce] = useState(false)

  const { data: user, isLoading } = useQuery<User | null>({
    queryKey: ['auth', 'me'],
    queryFn: async () => {
      try {
        const result = await api.get<User>('/api/auth/me')
        return result
      } catch (err) {
        if (err instanceof ApiError && err.status === 401) return null
        throw err
      } finally {
        setCheckedOnce(true)
      }
    },
    staleTime: 5 * 60 * 1000,
    retry: false,
  })

  async function login(email: string, password: string) {
    const result = await api.post<LoginResponse>('/api/auth/login', { email, password })
    queryClient.setQueryData(['auth', 'me'], result.user)
    return result.user
  }

  async function logout() {
    await api.post('/api/auth/logout')
    queryClient.setQueryData(['auth', 'me'], null)
  }

  return (
    <AuthContext.Provider value={{ user, isLoading: isLoading && !checkedOnce, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider')
  return ctx
}
