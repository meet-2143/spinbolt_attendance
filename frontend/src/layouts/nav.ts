import type { NavItem } from '@/layouts/AppLayout'

export const SUPERVISOR_NAV: NavItem[] = [
  { label: 'Dashboard', to: '/supervisor', end: true },
  { label: 'Add Attendance', to: '/supervisor/attendance/add' },
  { label: "Today's Attendance", to: '/supervisor/attendance/today' },
  { label: 'Attendance History', to: '/supervisor/attendance/history' },
]

export const ADMIN_NAV: NavItem[] = [
  { label: 'Dashboard', to: '/admin', end: true },
  { label: 'All Attendance', to: '/admin/attendance' },
  { label: 'Reports', to: '/admin/reports' },
  { label: 'Supervisors', to: '/admin/supervisors' },
  { label: 'Audit Logs', to: '/admin/audit-logs' },
]
