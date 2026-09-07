import { api } from '@/lib/api'
import type { Attendance } from '@/types/attendance'
import { useQuery } from '@tanstack/react-query'

export type ReportMode = 'daily' | 'range' | 'monthly'

export interface ReportParams {
  mode: ReportMode
  date?: string
  dateFrom?: string
  dateTo?: string
  year?: number
  month?: number
}

function isReady(params: ReportParams): boolean {
  if (params.mode === 'daily') return !!params.date
  if (params.mode === 'range') return !!params.dateFrom && !!params.dateTo
  return !!params.year && !!params.month
}

function buildPath(params: ReportParams): string {
  if (params.mode === 'daily') return `/api/reports/daily?date=${params.date}`
  if (params.mode === 'range') return `/api/reports/range?date_from=${params.dateFrom}&date_to=${params.dateTo}`
  return `/api/reports/monthly?year=${params.year}&month=${params.month}`
}

export function useReport(params: ReportParams) {
  return useQuery<Attendance[]>({
    queryKey: ['reports', params],
    queryFn: () => api.get(buildPath(params)),
    enabled: isReady(params),
  })
}

export function buildExportUrl(params: ReportParams, format: 'csv' | 'excel' | 'pdf'): string {
  let dateFrom: string | undefined
  let dateTo: string | undefined

  if (params.mode === 'daily') {
    dateFrom = params.date
    dateTo = params.date
  } else if (params.mode === 'range') {
    dateFrom = params.dateFrom
    dateTo = params.dateTo
  } else if (params.year && params.month) {
    const lastDay = new Date(params.year, params.month, 0).getDate()
    dateFrom = `${params.year}-${String(params.month).padStart(2, '0')}-01`
    dateTo = `${params.year}-${String(params.month).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`
  }

  const search = new URLSearchParams({ format })
  if (dateFrom) search.set('date_from', dateFrom)
  if (dateTo) search.set('date_to', dateTo)
  return `/api/attendance/export?${search.toString()}`
}
