import { api } from '@/lib/api'
import type { PagedResponse } from '@/types/attendance'
import type { AuditLog } from '@/types/audit'
import { useQuery } from '@tanstack/react-query'

export function useAuditLogs(page: number, pageSize = 20) {
  return useQuery<PagedResponse<AuditLog>>({
    queryKey: ['audit-logs', page, pageSize],
    queryFn: () => api.get(`/api/audit-logs?page=${page}&page_size=${pageSize}`),
    placeholderData: (previous) => previous,
  })
}

export function useAttendanceAuditLogs(attendanceId: string | null) {
  return useQuery<AuditLog[]>({
    queryKey: ['audit-logs', 'attendance', attendanceId],
    queryFn: () => api.get(`/api/audit-logs/${attendanceId}`),
    enabled: !!attendanceId,
  })
}
