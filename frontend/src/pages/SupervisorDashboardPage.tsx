import { AttendanceTable } from '@/components/AttendanceTable'
import { buttonVariants } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useSupervisorDashboard } from '@/hooks/useAttendance'
import { AppLayout } from '@/layouts/AppLayout'
import { SUPERVISOR_NAV } from '@/layouts/nav'
import { Link } from 'react-router-dom'

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{label}</CardTitle>
      </CardHeader>
      <CardContent className="pt-0">
        <p className="text-2xl font-semibold text-[var(--color-foreground)]">{value}</p>
      </CardContent>
    </Card>
  )
}

export function SupervisorDashboardPage() {
  const { data, isLoading } = useSupervisorDashboard()

  return (
    <AppLayout title="Supervisor Dashboard" navItems={SUPERVISOR_NAV}>
      <div className="mb-4 flex items-center justify-between">
        <p className="text-sm text-[var(--color-muted)]">Today's snapshot</p>
        <Link to="/supervisor/attendance/add" className={buttonVariants({ variant: 'default' })}>
          + Add Attendance
        </Link>
      </div>

      {isLoading || !data ? (
        <p className="text-sm text-[var(--color-muted)]">Loading dashboard…</p>
      ) : (
        <>
          <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
            <StatCard label="Today's Attendance" value={data.today_count} />
            <StatCard label="Present" value={data.present_count} />
            <StatCard label="Absent" value={data.absent_count} />
            <StatCard label="Working Hours" value={data.total_working_hours} />
            <StatCard label="Machine Stopped" value={data.total_machine_stopped_time} />
            <StatCard label="Input Parts" value={data.total_input_parts} />
          </div>

          <p className="mb-2 text-sm font-medium text-[var(--color-foreground)]">Recent attendance</p>
          <AttendanceTable items={data.recent_entries} />
        </>
      )}
    </AppLayout>
  )
}
