import { AttendanceTable } from '@/components/AttendanceTable'
import { useAttendanceList } from '@/hooks/useAttendance'
import { AppLayout } from '@/layouts/AppLayout'
import { SUPERVISOR_NAV } from '@/layouts/nav'
import { todayIso } from '@/lib/date'

export function TodaysAttendancePage() {
  const today = todayIso()
  const { data, isLoading } = useAttendanceList({
    date_from: today,
    date_to: today,
    sort_by: 'created_at',
    sort_dir: 'desc',
    page_size: 100,
  })

  return (
    <AppLayout title="Today's Attendance" navItems={SUPERVISOR_NAV}>
      <AttendanceTable items={data?.items ?? []} isLoading={isLoading} />
    </AppLayout>
  )
}
