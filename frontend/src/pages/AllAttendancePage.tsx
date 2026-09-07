import { AttendanceForm, type AttendanceFormValues } from '@/components/AttendanceForm'
import { Pagination } from '@/components/Pagination'
import { StatusBadge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Dialog } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { useAttendanceList, useUpdateAttendance, useVoidAttendance } from '@/hooks/useAttendance'
import { useSupervisors } from '@/hooks/useSupervisors'
import { useToast } from '@/hooks/useToast'
import { AppLayout } from '@/layouts/AppLayout'
import { ADMIN_NAV } from '@/layouts/nav'
import { ApiError } from '@/lib/api'
import { formatDate } from '@/lib/date'
import type { Attendance, AttendanceRowInput } from '@/types/attendance'
import { ATTENDANCE_STATUSES } from '@/types/attendance'
import { useState } from 'react'
import { useSearchParams } from 'react-router-dom'

const PAGE_SIZE = 15

export function AllAttendancePage() {
  const { toast } = useToast()
  const { data: supervisors = [] } = useSupervisors()

  const [searchParams] = useSearchParams()

  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [status, setStatus] = useState('')
  const [search, setSearch] = useState('')
  const [supervisorId, setSupervisorId] = useState(searchParams.get('supervisor_id') ?? '')
  const [page, setPage] = useState(1)
  const [sortBy, setSortBy] = useState('attendance_date')
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc')

  const { data, isLoading } = useAttendanceList({
    date_from: dateFrom || undefined,
    date_to: dateTo || undefined,
    status: status || undefined,
    search: search || undefined,
    supervisor_id: supervisorId || undefined,
    sort_by: sortBy,
    sort_dir: sortDir,
    page,
    page_size: PAGE_SIZE,
  })

  const [editing, setEditing] = useState<Attendance | null>(null)
  const [voiding, setVoiding] = useState<Attendance | null>(null)
  const [voidReason, setVoidReason] = useState('')

  const updateMutation = useUpdateAttendance()
  const voidMutation = useVoidAttendance()

  function handleSort(key: string) {
    if (sortBy === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortBy(key)
      setSortDir('asc')
    }
  }

  async function handleUpdate(row: AttendanceRowInput) {
    if (!editing) return
    try {
      await updateMutation.mutateAsync({ id: editing.id, row })
      toast('Attendance record updated.', 'success')
      setEditing(null)
    } catch (err) {
      toast(err instanceof ApiError ? err.message : 'Could not update record.', 'error')
    }
  }

  async function handleVoid() {
    if (!voiding || !voidReason.trim()) return
    try {
      await voidMutation.mutateAsync({ id: voiding.id, reason: voidReason.trim() })
      toast(`Attendance record for ${voiding.worker_name} voided.`, 'success')
      setVoiding(null)
      setVoidReason('')
    } catch (err) {
      toast(err instanceof ApiError ? err.message : 'Could not void record.', 'error')
    }
  }

  return (
    <AppLayout title="All Attendance" navItems={ADMIN_NAV}>
      <Card className="mb-4">
        <CardContent className="flex flex-wrap items-end gap-4 pt-5">
          <div>
            <Label htmlFor="date-from">From</Label>
            <Input id="date-from" type="date" value={dateFrom} onChange={(e) => { setDateFrom(e.target.value); setPage(1) }} className="w-40" />
          </div>
          <div>
            <Label htmlFor="date-to">To</Label>
            <Input id="date-to" type="date" value={dateTo} onChange={(e) => { setDateTo(e.target.value); setPage(1) }} className="w-40" />
          </div>
          <div>
            <Label htmlFor="supervisor-filter">Supervisor</Label>
            <Select id="supervisor-filter" value={supervisorId} onChange={(e) => { setSupervisorId(e.target.value); setPage(1) }} className="w-44">
              <option value="">All</option>
              {supervisors.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </Select>
          </div>
          <div>
            <Label htmlFor="status-filter">Status</Label>
            <Select id="status-filter" value={status} onChange={(e) => { setStatus(e.target.value); setPage(1) }} className="w-36">
              <option value="">All</option>
              {ATTENDANCE_STATUSES.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </Select>
          </div>
          <div className="flex-1 min-w-[200px]">
            <Label htmlFor="search">Search</Label>
            <Input id="search" value={search} onChange={(e) => { setSearch(e.target.value); setPage(1) }} placeholder="Worker or supervisor name…" />
          </div>
          <Button variant="outline" onClick={() => { setDateFrom(''); setDateTo(''); setStatus(''); setSearch(''); setSupervisorId(''); setPage(1) }}>
            Clear filters
          </Button>
        </CardContent>
      </Card>

      <div className="overflow-x-auto rounded-lg border border-[var(--color-border)] bg-white">
        <table className="w-full min-w-[1100px] border-collapse text-sm">
          <thead>
            <tr className="border-b border-[var(--color-border)] bg-gray-50 text-left text-xs font-semibold uppercase text-[var(--color-muted)]">
              <th className="px-4 py-2.5"><button onClick={() => handleSort('attendance_date')}>Date</button></th>
              <th className="px-4 py-2.5"><button onClick={() => handleSort('supervisor_name')}>Attendance Taker</button></th>
              <th className="px-4 py-2.5"><button onClick={() => handleSort('worker_name')}>Worker</button></th>
              <th className="px-4 py-2.5">Status</th>
              <th className="px-4 py-2.5"><button onClick={() => handleSort('input_parts')}>Input Parts</button></th>
              <th className="px-4 py-2.5"><button onClick={() => handleSort('total_working_hours')}>Working Hours</button></th>
              <th className="px-4 py-2.5"><button onClick={() => handleSort('machine_stopped_time')}>Machine Stop</button></th>
              <th className="px-4 py-2.5">Remarks</th>
              <th className="px-4 py-2.5">Updated At</th>
              <th className="px-4 py-2.5" />
            </tr>
          </thead>
          <tbody>
            {isLoading ? (
              <tr><td colSpan={10} className="px-4 py-8 text-center text-[var(--color-muted)]">Loading…</td></tr>
            ) : (data?.items.length ?? 0) === 0 ? (
              <tr><td colSpan={10} className="px-4 py-8 text-center text-[var(--color-muted)]">No attendance records found.</td></tr>
            ) : (
              data!.items.map((item) => (
                <tr key={item.id} className="border-b border-[var(--color-border)]/60 last:border-0">
                  <td className="px-4 py-2.5 whitespace-nowrap">{formatDate(item.attendance_date)}</td>
                  <td className="px-4 py-2.5 whitespace-nowrap">{item.attendance_taker_name}</td>
                  <td className="px-4 py-2.5">{item.worker_name}</td>
                  <td className="px-4 py-2.5"><StatusBadge status={item.attendance_status} /></td>
                  <td className="px-4 py-2.5">{item.input_parts}</td>
                  <td className="px-4 py-2.5">{item.total_working_hours}</td>
                  <td className="px-4 py-2.5">{item.machine_stopped_time}</td>
                  <td className="px-4 py-2.5 max-w-[160px] truncate">{item.remarks || '—'}</td>
                  <td className="px-4 py-2.5 whitespace-nowrap text-xs text-[var(--color-muted)]">
                    {new Date(item.updated_at).toLocaleString()}
                  </td>
                  <td className="px-4 py-2.5 whitespace-nowrap">
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" onClick={() => setEditing(item)}>Edit</Button>
                      <Button variant="destructive" size="sm" onClick={() => setVoiding(item)}>Void</Button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      {data && <Pagination page={page} pageSize={PAGE_SIZE} total={data.total} onPageChange={setPage} />}

      <Dialog open={!!editing} onClose={() => setEditing(null)} title="Edit Attendance">
        {editing && (
          <AttendanceForm
            defaultValues={{
              attendance_date: editing.attendance_date,
              worker_name: editing.worker_name,
              attendance_status: editing.attendance_status,
              input_parts: Number(editing.input_parts),
              total_working_hours: Number(editing.total_working_hours),
              machine_stopped_time: Number(editing.machine_stopped_time),
              remarks: editing.remarks ?? '',
            } as AttendanceFormValues}
            onSubmit={handleUpdate}
            submitLabel="Save Changes"
            isSubmitting={updateMutation.isPending}
          />
        )}
      </Dialog>

      <Dialog open={!!voiding} onClose={() => { setVoiding(null); setVoidReason('') }} title="Void Attendance Record">
        {voiding && (
          <div className="flex flex-col gap-4">
            <p className="text-sm text-[var(--color-foreground)]">
              This will remove <strong>{voiding.worker_name}</strong>'s attendance for{' '}
              {formatDate(voiding.attendance_date)} from all views and reports, while keeping it in the audit
              trail. This action cannot be undone from the UI.
            </p>
            <div>
              <Label htmlFor="void-reason">Reason (required)</Label>
              <Textarea id="void-reason" rows={2} value={voidReason} onChange={(e) => setVoidReason(e.target.value)} />
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="secondary" onClick={() => { setVoiding(null); setVoidReason('') }}>Cancel</Button>
              <Button variant="destructive" disabled={!voidReason.trim() || voidMutation.isPending} onClick={handleVoid}>
                {voidMutation.isPending ? 'Voiding…' : 'Void Record'}
              </Button>
            </div>
          </div>
        )}
      </Dialog>
    </AppLayout>
  )
}
