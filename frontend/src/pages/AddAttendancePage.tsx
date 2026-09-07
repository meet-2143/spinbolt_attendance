import { AttendanceForm, type AttendanceFormValues } from '@/components/AttendanceForm'
import { BulkAttendanceGrid } from '@/components/BulkAttendanceGrid'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { useCreateAttendance, useUpdateAttendance } from '@/hooks/useAttendance'
import { useToast } from '@/hooks/useToast'
import { ApiError } from '@/lib/api'
import { todayIso } from '@/lib/date'
import { AppLayout } from '@/layouts/AppLayout'
import { SUPERVISOR_NAV } from '@/layouts/nav'
import type { AttendanceRowInput } from '@/types/attendance'
import { cn } from '@/lib/utils'
import { useState } from 'react'

type Tab = 'single' | 'bulk'

export function AddAttendancePage() {
  const [tab, setTab] = useState<Tab>('single')
  const { toast } = useToast()
  const createMutation = useCreateAttendance()
  const updateMutation = useUpdateAttendance()
  const [duplicate, setDuplicate] = useState<{ existingId: string; row: AttendanceRowInput } | null>(null)
  const [formKey, setFormKey] = useState(0)

  const defaultValues: AttendanceFormValues = {
    attendance_date: todayIso(),
    worker_name: '',
    attendance_status: 'PRESENT',
    input_parts: 0,
    total_working_hours: 0,
    machine_stopped_time: 0,
    remarks: '',
  }

  async function handleSubmit(row: AttendanceRowInput) {
    try {
      await createMutation.mutateAsync(row)
      toast(`Attendance saved for ${row.worker_name}.`, 'success')
      setDuplicate(null)
      setFormKey((k) => k + 1)
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setDuplicate({ existingId: err.body?.existing_id as string, row })
      } else {
        toast(err instanceof ApiError ? err.message : 'Could not save attendance.', 'error')
      }
    }
  }

  async function handleUpdateExisting() {
    if (!duplicate) return
    try {
      await updateMutation.mutateAsync({ id: duplicate.existingId, row: duplicate.row })
      toast(`Existing entry updated for ${duplicate.row.worker_name}.`, 'success')
      setDuplicate(null)
      setFormKey((k) => k + 1)
    } catch (err) {
      toast(err instanceof ApiError ? err.message : 'Could not update attendance.', 'error')
    }
  }

  return (
    <AppLayout title="Add Attendance" navItems={SUPERVISOR_NAV}>
      <div className="mb-4 flex gap-1 rounded-md border border-[var(--color-border)] bg-white p-1 w-fit">
        {(['single', 'bulk'] as Tab[]).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={cn(
              'rounded px-4 py-1.5 text-sm font-medium transition-colors',
              tab === t ? 'bg-[var(--color-primary)] text-[var(--color-primary-foreground)]' : 'text-[var(--color-muted)] hover:bg-gray-50',
            )}
          >
            {t === 'single' ? 'Single Entry' : 'Bulk Entry'}
          </button>
        ))}
      </div>

      {tab === 'single' ? (
        <Card className="max-w-2xl">
          <CardContent className="pt-5">
            {duplicate && (
              <div className="mb-4 flex items-center justify-between gap-3 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-[var(--color-warning)]">
                <span>
                  Attendance already exists for {duplicate.row.worker_name} on this date.
                </span>
                <Button size="sm" variant="secondary" onClick={handleUpdateExisting}>
                  Update existing entry
                </Button>
              </div>
            )}
            <AttendanceForm
              key={formKey}
              defaultValues={defaultValues}
              onSubmit={handleSubmit}
              isSubmitting={createMutation.isPending}
            />
          </CardContent>
        </Card>
      ) : (
        <BulkAttendanceGrid />
      )}
    </AppLayout>
  )
}
