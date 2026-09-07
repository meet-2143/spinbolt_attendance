import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useAdminDashboard } from '@/hooks/useAdminDashboard'
import { AppLayout } from '@/layouts/AppLayout'
import { ADMIN_NAV } from '@/layouts/nav'
import { formatDate } from '@/lib/date'
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'

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

export function AdminDashboardPage() {
  const { data, isLoading } = useAdminDashboard()

  return (
    <AppLayout title="Admin Dashboard" navItems={ADMIN_NAV}>
      {isLoading || !data ? (
        <p className="text-sm text-[var(--color-muted)]">Loading dashboard…</p>
      ) : (
        <>
          <div className="mb-6 grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-7">
            <StatCard label="Total Records" value={data.total_attendance_records} />
            <StatCard label="Today's Attendance" value={data.today_count} />
            <StatCard label="Present Today" value={data.present_today} />
            <StatCard label="Absent Today" value={data.absent_today} />
            <StatCard label="Total Working Hours" value={data.total_working_hours} />
            <StatCard label="Machine Stopped" value={data.total_machine_stopped_time} />
            <StatCard label="Input Parts" value={data.total_input_parts} />
          </div>

          <div className="mb-6 grid gap-4 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Attendance Trend (last 14 days)</CardTitle>
              </CardHeader>
              <CardContent className="h-64 pt-0">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={data.trend}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis
                      dataKey="period"
                      tickFormatter={(v) => formatDate(v)}
                      tick={{ fontSize: 11 }}
                    />
                    <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                    <Tooltip labelFormatter={(v) => formatDate(v as string)} />
                    <Line type="monotone" dataKey="present" stroke="var(--color-success)" name="Present" />
                    <Line type="monotone" dataKey="absent" stroke="var(--color-danger)" name="Absent" />
                    <Line type="monotone" dataKey="total" stroke="var(--color-accent)" name="Total" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Supervisor Summary (last 14 days)</CardTitle>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-[var(--color-border)] text-left text-xs uppercase text-[var(--color-muted)]">
                        <th className="py-2">Supervisor</th>
                        <th className="py-2">Entries</th>
                        <th className="py-2">Hours</th>
                        <th className="py-2">Stop</th>
                        <th className="py-2">Parts</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.supervisor_summary.length === 0 ? (
                        <tr>
                          <td colSpan={5} className="py-4 text-center text-[var(--color-muted)]">
                            No data for this range.
                          </td>
                        </tr>
                      ) : (
                        data.supervisor_summary.map((row) => (
                          <tr key={row.supervisor_id} className="border-b border-[var(--color-border)]/60">
                            <td className="py-2">{row.supervisor_name}</td>
                            <td className="py-2">{row.entries}</td>
                            <td className="py-2">{row.total_working_hours}</td>
                            <td className="py-2">{row.total_machine_stopped_time}</td>
                            <td className="py-2">{row.total_input_parts}</td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </div>
        </>
      )}
    </AppLayout>
  )
}
