import { api } from '@/lib/api'
import type { AdminDashboard } from '@/types/dashboard'
import { useQuery } from '@tanstack/react-query'

export function useAdminDashboard(params: { date_from?: string; date_to?: string } = {}) {
  const search = new URLSearchParams()
  if (params.date_from) search.set('date_from', params.date_from)
  if (params.date_to) search.set('date_to', params.date_to)
  const qs = search.toString()

  return useQuery<AdminDashboard>({
    queryKey: ['dashboard', 'admin', params],
    queryFn: () => api.get(`/api/dashboard/admin${qs ? `?${qs}` : ''}`),
  })
}
