export interface TrendPoint {
  period: string
  total: number
  present: number
  absent: number
}

export interface SupervisorSummaryRow {
  supervisor_id: string
  supervisor_name: string
  entries: number
  total_working_hours: string
  total_machine_stopped_time: string
  total_input_parts: string
}

export interface AdminDashboard {
  total_attendance_records: number
  today_count: number
  present_today: number
  absent_today: number
  total_working_hours: string
  total_machine_stopped_time: string
  total_input_parts: string
  trend: TrendPoint[]
  supervisor_summary: SupervisorSummaryRow[]
}
