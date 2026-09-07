import { ProtectedRoute } from '@/components/ProtectedRoute'
import { useAuth } from '@/hooks/useAuth'
import { AddAttendancePage } from '@/pages/AddAttendancePage'
import { AdminDashboardPage } from '@/pages/AdminDashboardPage'
import { AllAttendancePage } from '@/pages/AllAttendancePage'
import { AttendanceHistoryPage } from '@/pages/AttendanceHistoryPage'
import { AuditLogsPage } from '@/pages/AuditLogsPage'
import { LoginPage } from '@/pages/LoginPage'
import { ReportsPage } from '@/pages/ReportsPage'
import { SupervisorDashboardPage } from '@/pages/SupervisorDashboardPage'
import { SupervisorsPage } from '@/pages/SupervisorsPage'
import { TodaysAttendancePage } from '@/pages/TodaysAttendancePage'
import { Navigate, Route, Routes } from 'react-router-dom'

function RootRedirect() {
  const { user, isLoading } = useAuth()
  if (isLoading) return null
  if (!user) return <Navigate to="/login" replace />
  return <Navigate to={user.role === 'ADMIN' ? '/admin' : '/supervisor'} replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route
        path="/admin"
        element={
          <ProtectedRoute allowedRoles={['ADMIN']}>
            <AdminDashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/attendance"
        element={
          <ProtectedRoute allowedRoles={['ADMIN']}>
            <AllAttendancePage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/reports"
        element={
          <ProtectedRoute allowedRoles={['ADMIN']}>
            <ReportsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/supervisors"
        element={
          <ProtectedRoute allowedRoles={['ADMIN']}>
            <SupervisorsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/audit-logs"
        element={
          <ProtectedRoute allowedRoles={['ADMIN']}>
            <AuditLogsPage />
          </ProtectedRoute>
        }
      />

      <Route
        path="/supervisor"
        element={
          <ProtectedRoute allowedRoles={['SUPERVISOR']}>
            <SupervisorDashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/supervisor/attendance/add"
        element={
          <ProtectedRoute allowedRoles={['SUPERVISOR']}>
            <AddAttendancePage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/supervisor/attendance/today"
        element={
          <ProtectedRoute allowedRoles={['SUPERVISOR']}>
            <TodaysAttendancePage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/supervisor/attendance/history"
        element={
          <ProtectedRoute allowedRoles={['SUPERVISOR']}>
            <AttendanceHistoryPage />
          </ProtectedRoute>
        }
      />

      <Route path="/" element={<RootRedirect />} />
      <Route path="*" element={<RootRedirect />} />
    </Routes>
  )
}
