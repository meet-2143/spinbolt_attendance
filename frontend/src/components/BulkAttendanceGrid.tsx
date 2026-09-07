import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { WorkerNameField } from '@/components/WorkerNameField'
import { useAuth } from '@/hooks/useAuth'
import { useBulkCreateAttendance } from '@/hooks/useAttendance'
import { useToast } from '@/hooks/useToast'
import { ApiError } from '@/lib/api'
import { todayIso } from '@/lib/date'
import { cn } from '@/lib/utils'
import type { AttendanceStatus, BulkRowError } from '@/types/attendance'
import { ATTENDANCE_STATUSES } from '@/types/attendance'
import { Trash2 } from 'lucide-react'
import { useState } from 'react'

interface BulkRow {
  worker_name: string
  attendance_status: AttendanceStatus
  input_parts: string
  total_working_hours: string
  machine_stopped_time: string
  remarks: string
}

const STATUS_LABELS: Record<AttendanceStatus, string> = {
  PRESENT: 'Present',
  ABSENT: 'Absent',
  HALF_DAY: 'Half Day',
  LEAVE: 'Leave',
}

function emptyRow(): BulkRow {
  return {
    worker_name: '',
    attendance_status: 'PRESENT',
    input_parts: '0',
    total_working_hours: '8',
    machine_stopped_time: '0',
    remarks: '',
  }
}

function validateRow(row: BulkRow): string | null {
  if (!row.worker_name.trim()) return 'Worker name is required.'
  const parts = Number(row.input_parts)
  const hours = Number(row.total_working_hours)
  const stop = Number(row.machine_stopped_time)
  if ([parts, hours, stop].some((n) => Number.isNaN(n))) return 'Enter valid numbers.'
  if (parts < 0 || hours < 0 || stop < 0) return 'Values must be 0 or greater.'
  if (row.attendance_status !== 'ABSENT' && stop > hours) {
    return 'Machine stopped time cannot exceed working hours.'
  }
  return null
}

export function BulkAttendanceGrid() {
  const { user } = useAuth()
  const { toast } = useToast()
  const bulkMutation = useBulkCreateAttendance()
  const [attendanceDate, setAttendanceDate] = useState(todayIso())
  const [rows, setRows] = useState<BulkRow[]>([emptyRow(), emptyRow(), emptyRow()])
  const [serverErrors, setServerErrors] = useState<Record<number, string>>({})

  function updateRow(index: number, patch: Partial<BulkRow>) {
    setRows((prev) =>
      prev.map((row, i) => {
        if (i !== index) return row
        const next = { ...row, ...patch }
        if (patch.attendance_status === 'ABSENT') {
          next.input_parts = '0'
          next.total_working_hours = '0'
          next.machine_stopped_time = '0'
        }
        return next
      }),
    )
    setServerErrors((prev) => {
      if (!(index in prev)) return prev
      const next = { ...prev }
      delete next[index]
      return next
    })
  }

  function addRow() {
    setRows((prev) => [...prev, emptyRow()])
  }

  function removeRow(index: number) {
    setRows((prev) => prev.filter((_, i) => i !== index))
    setServerErrors((prev) => {
      const next: Record<number, string> = {}
      Object.entries(prev).forEach(([key, value]) => {
        const i = Number(key)
        if (i < index) next[i] = value
        if (i > index) next[i - 1] = value
      })
      return next
    })
  }

  const clientErrors = rows.map(validateRow)
  const hasClientErrors = clientErrors.some(Boolean)

  async function handleSave() {
    if (hasClientErrors) {
      toast('Fix the highlighted rows before saving.', 'error')
      return
    }
    setServerErrors({})

    const payload = rows.map((row) => ({
      attendance_date: attendanceDate,
      worker_name: row.worker_name.trim(),
      attendance_status: row.attendance_status,
      input_parts: Number(row.input_parts),
      total_working_hours: Number(row.total_working_hours),
      machine_stopped_time: Number(row.machine_stopped_time),
      remarks: row.remarks,
    }))

    try {
      const created = await bulkMutation.mutateAsync(payload)
      toast(`Saved attendance for ${created.length} worker(s).`, 'success')
      setRows([emptyRow(), emptyRow(), emptyRow()])
    } catch (err) {
      if (err instanceof ApiError && err.status === 422 && Array.isArray(err.body?.errors)) {
        const errors = err.body.errors as BulkRowError[]
        const mapped: Record<number, string> = {}
        errors.forEach((e) => {
          mapped[e.row] = e.message
        })
        setServerErrors(mapped)
        toast('Some rows could not be saved. No records were created - fix the highlighted rows and try again.', 'error')
      } else {
        toast(err instanceof ApiError ? err.message : 'Could not save attendance.', 'error')
      }
    }
  }

  return (
    <Card>
      <CardContent className="pt-5">
        <div className="mb-4 flex flex-wrap items-end gap-6">
          <div>
            <Label htmlFor="bulk-date">Attendance Date</Label>
            <Input
              id="bulk-date"
              type="date"
              value={attendanceDate}
              onChange={(e) => setAttendanceDate(e.target.value)}
              className="w-44"
            />
          </div>
          <div>
            <Label>Attendance Taker</Label>
            <p className="flex h-9 items-center text-sm font-medium">{user?.name}</p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full min-w-[900px] border-collapse text-sm">
            <thead>
              <tr className="border-b border-[var(--color-border)] text-left text-xs font-semibold uppercase text-[var(--color-muted)]">
                <th className="py-2 pr-2">Worker Name</th>
                <th className="py-2 px-2">Status</th>
                <th className="py-2 px-2">Input Parts</th>
                <th className="py-2 px-2">Working Hours</th>
                <th className="py-2 px-2">Machine Stop</th>
                <th className="py-2 px-2">Remarks</th>
                <th className="py-2 pl-2" />
              </tr>
            </thead>
            <tbody>
              {rows.map((row, index) => {
                const error = serverErrors[index] ?? (row.worker_name ? clientErrors[index] : null)
                const isAbsent = row.attendance_status === 'ABSENT'
                return (
                  <tr
                    key={index}
                    className={cn('border-b border-[var(--color-border)]/60', error && 'bg-red-50/60')}
                  >
                    <td className="py-2 pr-2 align-top">
                      <WorkerNameField
                        value={row.worker_name}
                        onChange={(value) => updateRow(index, { worker_name: value })}
                      />
                    </td>
                    <td className="px-2 align-top">
                      <Select
                        value={row.attendance_status}
                        onChange={(e) => updateRow(index, { attendance_status: e.target.value as AttendanceStatus })}
                      >
                        {ATTENDANCE_STATUSES.map((s) => (
                          <option key={s} value={s}>
                            {STATUS_LABELS[s]}
                          </option>
                        ))}
                      </Select>
                    </td>
                    <td className="px-2 align-top">
                      <Input
                        type="number"
                        min={0}
                        disabled={isAbsent}
                        value={row.input_parts}
                        onChange={(e) => updateRow(index, { input_parts: e.target.value })}
                        className="w-24"
                      />
                    </td>
                    <td className="px-2 align-top">
                      <Input
                        type="number"
                        min={0}
                        step="0.5"
                        disabled={isAbsent}
                        value={row.total_working_hours}
                        onChange={(e) => updateRow(index, { total_working_hours: e.target.value })}
                        className="w-24"
                      />
                    </td>
                    <td className="px-2 align-top">
                      <Input
                        type="number"
                        min={0}
                        step="0.25"
                        disabled={isAbsent}
                        value={row.machine_stopped_time}
                        onChange={(e) => updateRow(index, { machine_stopped_time: e.target.value })}
                        className="w-24"
                      />
                    </td>
                    <td className="px-2 align-top">
                      <Input
                        value={row.remarks}
                        onChange={(e) => updateRow(index, { remarks: e.target.value })}
                        className="w-36"
                      />
                    </td>
                    <td className="py-2 pl-2 align-top">
                      <Button variant="ghost" size="icon" onClick={() => removeRow(index)} type="button">
                        <Trash2 className="h-4 w-4 text-[var(--color-danger)]" />
                      </Button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
        {Object.entries(serverErrors).length > 0 && (
          <div className="mt-2 flex flex-col gap-1">
            {rows.map((row, index) =>
              serverErrors[index] ? (
                <p key={index} className="text-xs text-[var(--color-danger)]">
                  Row {index + 1} ({row.worker_name || 'unnamed'}): {serverErrors[index]}
                </p>
              ) : null,
            )}
          </div>
        )}

        <div className="mt-4 flex gap-2">
          <Button variant="secondary" type="button" onClick={addRow}>
            + Add Row
          </Button>
          <Button type="button" onClick={handleSave} disabled={bulkMutation.isPending}>
            {bulkMutation.isPending ? 'Saving…' : 'Save Attendance'}
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
