export type AuditAction = 'CREATED' | 'UPDATED' | 'DELETED'

export interface AuditLog {
  id: string
  attendance_id: string
  action: AuditAction
  old_data: Record<string, unknown> | null
  new_data: Record<string, unknown> | null
  changed_by: string
  changed_by_name: string
  changed_at: string
}
