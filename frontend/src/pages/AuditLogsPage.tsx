import { Pagination } from '@/components/Pagination'
import { Card, CardContent } from '@/components/ui/card'
import { useAuditLogs } from '@/hooks/useAuditLogs'
import { AppLayout } from '@/layouts/AppLayout'
import { ADMIN_NAV } from '@/layouts/nav'
import type { AuditLog } from '@/types/audit'
import { useState } from 'react'

const PAGE_SIZE = 20

function formatFieldName(key: string): string {
  return key
    .split('_')
    .map((w) => w[0].toUpperCase() + w.slice(1))
    .join(' ')
}

function DiffLines({ log }: { log: AuditLog }) {
  if (log.action === 'CREATED') {
    return <p className="text-sm text-[var(--color-muted)]">New attendance record created.</p>
  }
  if (log.action === 'DELETED') {
    return <p className="text-sm text-[var(--color-muted)]">Attendance record voided.</p>
  }
  const oldData = log.old_data ?? {}
  const newData = log.new_data ?? {}
  const keys = Object.keys(newData)
  if (keys.length === 0) return null
  return (
    <div className="flex flex-col gap-0.5">
      {keys.map((key) => (
        <p key={key} className="text-sm text-[var(--color-foreground)]">
          <span className="text-[var(--color-muted)]">{formatFieldName(key)}:</span>{' '}
          {String(oldData[key])} → {String(newData[key])}
        </p>
      ))}
    </div>
  )
}

export function AuditLogsPage() {
  const [page, setPage] = useState(1)
  const { data, isLoading } = useAuditLogs(page, PAGE_SIZE)

  return (
    <AppLayout title="Audit Logs" navItems={ADMIN_NAV}>
      <div className="flex flex-col gap-3">
        {isLoading ? (
          <p className="text-sm text-[var(--color-muted)]">Loading…</p>
        ) : (data?.items.length ?? 0) === 0 ? (
          <p className="text-sm text-[var(--color-muted)]">No audit history yet.</p>
        ) : (
          data!.items.map((log) => (
            <Card key={log.id}>
              <CardContent className="flex items-start justify-between gap-4 pt-5">
                <div>
                  <p className="text-sm font-semibold text-[var(--color-foreground)]">
                    Attendance {log.action.charAt(0) + log.action.slice(1).toLowerCase()}
                  </p>
                  <p className="mb-2 text-xs text-[var(--color-muted)]">
                    Changed by {log.changed_by_name} · {new Date(log.changed_at).toLocaleString()}
                  </p>
                  <DiffLines log={log} />
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
      {data && <Pagination page={page} pageSize={PAGE_SIZE} total={data.total} onPageChange={setPage} />}
    </AppLayout>
  )
}
