import { StatusBadge } from '@/components/ui/badge'
import { formatDate } from '@/lib/date'
import type { Attendance } from '@/types/attendance'
import { ArrowDown, ArrowUp } from 'lucide-react'

interface Column {
  key: string
  label: string
  sortable?: boolean
}

const BASE_COLUMNS: Column[] = [
  { key: 'attendance_date', label: 'Date', sortable: true },
  { key: 'worker_name', label: 'Worker', sortable: true },
  { key: 'attendance_status', label: 'Status' },
  { key: 'input_parts', label: 'Input Parts', sortable: true },
  { key: 'total_working_hours', label: 'Working Hours', sortable: true },
  { key: 'machine_stopped_time', label: 'Machine Stop', sortable: true },
  { key: 'remarks', label: 'Remarks' },
  { key: 'created_at', label: 'Created At' },
  { key: 'updated_at', label: 'Updated At' },
]

const SUPERVISOR_COLUMN: Column = { key: 'supervisor_name', label: 'Supervisor', sortable: true }

export function AttendanceTable({
  items,
  isLoading,
  showSupervisor = false,
  sortBy,
  sortDir,
  onSort,
}: {
  items: Attendance[]
  isLoading?: boolean
  showSupervisor?: boolean
  sortBy?: string
  sortDir?: 'asc' | 'desc'
  onSort?: (key: string) => void
}) {
  const columns = showSupervisor ? [BASE_COLUMNS[0], SUPERVISOR_COLUMN, ...BASE_COLUMNS.slice(1)] : BASE_COLUMNS

  return (
    <div className="overflow-x-auto rounded-lg border border-[var(--color-border)] bg-white">
      <table className="w-full min-w-[900px] border-collapse text-sm">
        <thead>
          <tr className="border-b border-[var(--color-border)] bg-gray-50 text-left text-xs font-semibold uppercase text-[var(--color-muted)]">
            {columns.map((col) => (
              <th key={col.key} className="px-4 py-2.5">
                {col.sortable && onSort ? (
                  <button
                    className="flex items-center gap-1 hover:text-[var(--color-foreground)]"
                    onClick={() => onSort(col.key)}
                  >
                    {col.label}
                    {sortBy === col.key &&
                      (sortDir === 'asc' ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />)}
                  </button>
                ) : (
                  col.label
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {isLoading ? (
            <tr>
              <td colSpan={columns.length} className="px-4 py-8 text-center text-[var(--color-muted)]">
                Loading…
              </td>
            </tr>
          ) : items.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="px-4 py-8 text-center text-[var(--color-muted)]">
                No attendance records found.
              </td>
            </tr>
          ) : (
            items.map((item) => (
              <tr key={item.id} className="border-b border-[var(--color-border)]/60 last:border-0">
                <td className="px-4 py-2.5 whitespace-nowrap">{formatDate(item.attendance_date)}</td>
                {showSupervisor && (
                  <td className="px-4 py-2.5 whitespace-nowrap">{item.attendance_taker_name}</td>
                )}
                <td className="px-4 py-2.5">{item.worker_name}</td>
                <td className="px-4 py-2.5">
                  <StatusBadge status={item.attendance_status} />
                </td>
                <td className="px-4 py-2.5">{item.input_parts}</td>
                <td className="px-4 py-2.5">{item.total_working_hours}</td>
                <td className="px-4 py-2.5">{item.machine_stopped_time}</td>
                <td className="px-4 py-2.5 max-w-[200px] truncate">{item.remarks || '—'}</td>
                <td className="px-4 py-2.5 whitespace-nowrap text-xs text-[var(--color-muted)]">
                  {new Date(item.created_at).toLocaleString()}
                </td>
                <td className="px-4 py-2.5 whitespace-nowrap text-xs text-[var(--color-muted)]">
                  {new Date(item.updated_at).toLocaleString()}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  )
}
