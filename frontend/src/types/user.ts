export type UserRole = 'ADMIN' | 'SUPERVISOR'
export type UserStatus = 'ACTIVE' | 'INACTIVE'

export interface User {
  id: string
  name: string
  email: string
  role: UserRole
  phone: string | null
  department: string | null
  status: UserStatus
  created_at: string
  updated_at: string
}
