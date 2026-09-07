import { api } from '@/lib/api'
import type {
  Attendance,
  AttendanceRowInput,
  BulkRowError,
  PagedResponse,
  SupervisorDashboard,
} from '@/types/attendance'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

export interface AttendanceListParams {
  date_from?: string
  date_to?: string
  status?: string
  search?: string
  supervisor_id?: string
  sort_by?: string
  sort_dir?: string
  page?: number
  page_size?: number
}

function toQueryString(params: AttendanceListParams) {
  const search = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== '') search.set(key, String(value))
  })
  const qs = search.toString()
  return qs ? `?${qs}` : ''
}

export function useAttendanceList(params: AttendanceListParams) {
  return useQuery<PagedResponse<Attendance>>({
    queryKey: ['attendance', 'list', params],
    queryFn: () => api.get(`/api/attendance${toQueryString(params)}`),
    placeholderData: (previous) => previous,
  })
}

export function useSupervisorDashboard() {
  return useQuery<SupervisorDashboard>({
    queryKey: ['dashboard', 'supervisor'],
    queryFn: () => api.get('/api/dashboard/supervisor'),
  })
}

export function useWorkerNames(q: string) {
  return useQuery<string[]>({
    queryKey: ['attendance', 'worker-names', q],
    queryFn: () => api.get(`/api/attendance/worker-names?q=${encodeURIComponent(q)}`),
    enabled: q.length > 0,
    staleTime: 30_000,
  })
}

function invalidateAttendance(queryClient: ReturnType<typeof useQueryClient>) {
  queryClient.invalidateQueries({ queryKey: ['attendance'] })
  queryClient.invalidateQueries({ queryKey: ['dashboard'] })
}

export function useCreateAttendance() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (row: AttendanceRowInput) => api.post<Attendance>('/api/attendance', row),
    onSuccess: () => invalidateAttendance(queryClient),
  })
}

export function useUpdateAttendance() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, row }: { id: string; row: AttendanceRowInput }) =>
      api.put<Attendance>(`/api/attendance/${id}`, row),
    onSuccess: () => invalidateAttendance(queryClient),
  })
}

export interface BulkErrorResponse {
  message: string
  errors: BulkRowError[]
}

export function useBulkCreateAttendance() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (rows: AttendanceRowInput[]) => api.post<Attendance[]>('/api/attendance/bulk', { rows }),
    onSuccess: () => invalidateAttendance(queryClient),
  })
}

export function useVoidAttendance() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) =>
      api.delete(`/api/attendance/${id}`, { reason }),
    onSuccess: () => invalidateAttendance(queryClient),
  })
}
