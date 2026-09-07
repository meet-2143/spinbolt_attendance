import { useAuth } from '@/hooks/useAuth'
import type { UserRole } from '@/types/user'
import type { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'

export function ProtectedRoute({ allowedRoles, children }: { allowedRoles: UserRole[]; children: ReactNode }) {
  const { user, isLoading } = useAuth()

  if (isLoading) {
    return <div className="flex h-screen items-center justify-center text-[var(--color-muted)]">Loading…</div>
  }

  if (!user) {
    return <Navigate to="/login" replace />
  }

  if (!allowedRoles.includes(user.role)) {
    return <Navigate to={user.role === 'ADMIN' ? '/admin' : '/supervisor'} replace />
  }

  return <>{children}</>
}
