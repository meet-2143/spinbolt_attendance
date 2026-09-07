import { AttendanceTable } from '@/components/AttendanceTable'
import { buttonVariants } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { buildExportUrl, useReport, type ReportMode } from '@/hooks/useReports'
import { AppLayout } from '@/layouts/AppLayout'
import { ADMIN_NAV } from '@/layouts/nav'
import { cn } from '@/lib/utils'
import { todayIso } from '@/lib/date'
import { useState } from 'react'

const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
]

export function ReportsPage() {
  const [mode, setMode] = useState<ReportMode>('daily')
  const [date, setDate] = useState(todayIso())
  const [dateFrom, setDateFrom] = useState(todayIso())
  const [dateTo, setDateTo] = useState(todayIso())
  const now = new Date()
  const [year, setYear] = useState(now.getFullYear())
  const [month, setMonth] = useState(now.getMonth() + 1)

  const params = { mode, date, dateFrom, dateTo, year, month }
  const { data = [], isLoading, isFetched } = useReport(params)

  return (
    <AppLayout title="Reports" navItems={ADMIN_NAV}>
      <Card className="mb-4">
        <CardContent className="flex flex-wrap items-end gap-4 pt-5">
          <div className="flex gap-1 rounded-md border border-[var(--color-border)] bg-white p-1">
            {(['daily', 'range', 'monthly'] as ReportMode[]).map((m) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={cn(
                  'rounded px-3 py-1.5 text-sm font-medium capitalize transition-colors',
                  mode === m
                    ? 'bg-[var(--color-primary)] text-[var(--color-primary-foreground)]'
                    : 'text-[var(--color-muted)] hover:bg-gray-50',
                )}
              >
                {m}
              </button>
            ))}
          </div>

          {mode === 'daily' && (
            <div>
              <Label htmlFor="report-date">Date</Label>
              <Input id="report-date" type="date" value={date} onChange={(e) => setDate(e.target.value)} className="w-44" />
            </div>
          )}
          {mode === 'range' && (
            <>
              <div>
                <Label htmlFor="report-from">From</Label>
                <Input id="report-from" type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} className="w-44" />
              </div>
              <div>
                <Label htmlFor="report-to">To</Label>
                <Input id="report-to" type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)} className="w-44" />
              </div>
            </>
          )}
          {mode === 'monthly' && (
            <>
              <div>
                <Label htmlFor="report-month">Month</Label>
                <Select id="report-month" value={month} onChange={(e) => setMonth(Number(e.target.value))} className="w-36">
                  {MONTH_NAMES.map((name, idx) => (
                    <option key={name} value={idx + 1}>{name}</option>
                  ))}
                </Select>
              </div>
              <div>
                <Label htmlFor="report-year">Year</Label>
                <Input
                  id="report-year"
                  type="number"
                  value={year}
                  onChange={(e) => setYear(Number(e.target.value))}
                  className="w-24"
                />
              </div>
            </>
          )}

          <div className="ml-auto flex gap-2">
            <a href={buildExportUrl(params, 'csv')} className={buttonVariants({ variant: 'secondary', size: 'sm' })}>
              Export CSV
            </a>
            <a href={buildExportUrl(params, 'excel')} className={buttonVariants({ variant: 'secondary', size: 'sm' })}>
              Export Excel
            </a>
            <a href={buildExportUrl(params, 'pdf')} className={buttonVariants({ variant: 'secondary', size: 'sm' })}>
              Export PDF
            </a>
          </div>
        </CardContent>
      </Card>

      {isLoading ? (
        <p className="text-sm text-[var(--color-muted)]">Generating report…</p>
      ) : isFetched && data.length === 0 ? (
        <p className="text-sm text-[var(--color-muted)]">No attendance records found for this period.</p>
      ) : (
        <AttendanceTable items={data} showSupervisor />
      )}
    </AppLayout>
  )
}
