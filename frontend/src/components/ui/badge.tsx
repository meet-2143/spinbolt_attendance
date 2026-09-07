import { cn } from '@/lib/utils'
import type { AttendanceStatus } from '@/types/attendance'

const STATUS_STYLES: Record<AttendanceStatus, string> = {
  PRESENT: 'bg-green-50 text-[var(--color-success)] border-green-200',
  ABSENT: 'bg-red-50 text-[var(--color-danger)] border-red-200',
  HALF_DAY: 'bg-amber-50 text-[var(--color-warning)] border-amber-200',
  LEAVE: 'bg-blue-50 text-[var(--color-accent)] border-blue-200',
}

const STATUS_LABELS: Record<AttendanceStatus, string> = {
  PRESENT: 'Present',
  ABSENT: 'Absent',
  HALF_DAY: 'Half Day',
  LEAVE: 'Leave',
}

export function StatusBadge({ status, className }: { status: AttendanceStatus; className?: string }) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium',
        STATUS_STYLES[status],
        className,
      )}
    >
      {STATUS_LABELS[status]}
    </span>
  )
}
