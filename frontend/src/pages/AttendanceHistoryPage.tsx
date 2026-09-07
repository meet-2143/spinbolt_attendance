import { AttendanceTable } from '@/components/AttendanceTable'
import { Pagination } from '@/components/Pagination'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { useAttendanceList } from '@/hooks/useAttendance'
import { AppLayout } from '@/layouts/AppLayout'
import { SUPERVISOR_NAV } from '@/layouts/nav'
import { ATTENDANCE_STATUSES } from '@/types/attendance'
import { useState } from 'react'

const PAGE_SIZE = 15

export function AttendanceHistoryPage() {
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [status, setStatus] = useState('')
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)
  const [sortBy, setSortBy] = useState('attendance_date')
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc')

  const { data, isLoading } = useAttendanceList({
    date_from: dateFrom || undefined,
    date_to: dateTo || undefined,
    status: status || undefined,
    search: search || undefined,
    sort_by: sortBy,
    sort_dir: sortDir,
    page,
    page_size: PAGE_SIZE,
  })

  function handleSort(key: string) {
    if (sortBy === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortBy(key)
      setSortDir('asc')
    }
  }

  function clearFilters() {
    setDateFrom('')
    setDateTo('')
    setStatus('')
    setSearch('')
    setPage(1)
  }

  return (
    <AppLayout title="Attendance History" navItems={SUPERVISOR_NAV}>
      <Card className="mb-4">
        <CardContent className="flex flex-wrap items-end gap-4 pt-5">
          <div>
            <Label htmlFor="date-from">From</Label>
            <Input
              id="date-from"
              type="date"
              value={dateFrom}
              onChange={(e) => {
                setDateFrom(e.target.value)
                setPage(1)
              }}
              className="w-40"
            />
          </div>
          <div>
            <Label htmlFor="date-to">To</Label>
            <Input
              id="date-to"
              type="date"
              value={dateTo}
              onChange={(e) => {
                setDateTo(e.target.value)
                setPage(1)
              }}
              className="w-40"
            />
          </div>
          <div>
            <Label htmlFor="status-filter">Status</Label>
            <Select
              id="status-filter"
              value={status}
              onChange={(e) => {
                setStatus(e.target.value)
                setPage(1)
              }}
              className="w-36"
            >
              <option value="">All</option>
              {ATTENDANCE_STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </Select>
          </div>
          <div className="flex-1 min-w-[200px]">
            <Label htmlFor="search">Search worker</Label>
            <Input
              id="search"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value)
                setPage(1)
              }}
              placeholder="Search by worker name…"
            />
          </div>
          <Button variant="outline" onClick={clearFilters}>
            Clear filters
          </Button>
        </CardContent>
      </Card>

      <AttendanceTable
        items={data?.items ?? []}
        isLoading={isLoading}
        sortBy={sortBy}
        sortDir={sortDir}
        onSort={handleSort}
      />
      {data && <Pagination page={page} pageSize={PAGE_SIZE} total={data.total} onPageChange={setPage} />}
    </AppLayout>
  )
}
