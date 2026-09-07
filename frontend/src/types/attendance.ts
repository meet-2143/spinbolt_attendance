export type AttendanceStatus = 'PRESENT' | 'ABSENT' | 'HALF_DAY' | 'LEAVE'

export const ATTENDANCE_STATUSES: AttendanceStatus[] = ['PRESENT', 'ABSENT', 'HALF_DAY', 'LEAVE']

export interface Attendance {
  id: string
  attendance_date: string
  attendance_taker_id: string
  attendance_taker_name: string
  worker_name: string
  input_parts: string
  total_working_hours: string
  machine_stopped_time: string
  attendance_status: AttendanceStatus
  remarks: string | null
  created_at: string
  updated_at: string
  created_by: string
  updated_by: string | null
}

export interface AttendanceRowInput {
  attendance_date: string
  worker_name: string
  input_parts: number
  total_working_hours: number
  machine_stopped_time: number
  attendance_status: AttendanceStatus
  remarks: string
}

export interface PagedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

export interface SupervisorDashboard {
  today_count: number
  present_count: number
  absent_count: number
  total_working_hours: string
  total_machine_stopped_time: string
  total_input_parts: string
  recent_entries: Attendance[]
}

export interface BulkRowError {
  row: number
  worker_name: string
  message: string
  existing_id?: string
}
