import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Dialog } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  useCreateSupervisor,
  useResetSupervisorPassword,
  useSetSupervisorStatus,
  useSupervisors,
  useUpdateSupervisor,
} from '@/hooks/useSupervisors'
import { useToast } from '@/hooks/useToast'
import { AppLayout } from '@/layouts/AppLayout'
import { ADMIN_NAV } from '@/layouts/nav'
import { ApiError } from '@/lib/api'
import type { User } from '@/types/user'
import { useEffect, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'

function CreateSupervisorDialog({ open, onClose }: { open: boolean; onClose: () => void }) {
  const { toast } = useToast()
  const createMutation = useCreateSupervisor()
  const [form, setForm] = useState({ name: '', email: '', password: '', phone: '', department: '' })

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    try {
      await createMutation.mutateAsync(form)
      toast(`Supervisor ${form.name} created.`, 'success')
      setForm({ name: '', email: '', password: '', phone: '', department: '' })
      onClose()
    } catch (err) {
      toast(err instanceof ApiError ? err.message : 'Could not create supervisor.', 'error')
    }
  }

  return (
    <Dialog open={open} onClose={onClose} title="Add Supervisor">
      <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
        <div>
          <Label htmlFor="new-name">Name</Label>
          <Input id="new-name" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        </div>
        <div>
          <Label htmlFor="new-email">Email</Label>
          <Input id="new-email" type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
        </div>
        <div>
          <Label htmlFor="new-password">Temporary Password</Label>
          <Input id="new-password" type="text" required minLength={8} value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="new-phone">Phone</Label>
            <Input id="new-phone" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
          </div>
          <div>
            <Label htmlFor="new-department">Department / Work Area</Label>
            <Input id="new-department" value={form.department} onChange={(e) => setForm({ ...form, department: e.target.value })} />
          </div>
        </div>
        <Button type="submit" disabled={createMutation.isPending} className="w-fit">
          {createMutation.isPending ? 'Creating…' : 'Create Supervisor'}
        </Button>
      </form>
    </Dialog>
  )
}

function EditSupervisorDialog({ supervisor, onClose }: { supervisor: User | null; onClose: () => void }) {
  const { toast } = useToast()
  const updateMutation = useUpdateSupervisor()
  const [form, setForm] = useState({ name: '', phone: '', department: '' })

  useEffect(() => {
    if (supervisor) {
      setForm({ name: supervisor.name, phone: supervisor.phone ?? '', department: supervisor.department ?? '' })
    }
  }, [supervisor])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!supervisor) return
    try {
      await updateMutation.mutateAsync({ id: supervisor.id, payload: form })
      toast('Supervisor updated.', 'success')
      onClose()
    } catch (err) {
      toast(err instanceof ApiError ? err.message : 'Could not update supervisor.', 'error')
    }
  }

  return (
    <Dialog open={!!supervisor} onClose={onClose} title="Edit Supervisor">
      {supervisor && (
        <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
          <div>
            <Label htmlFor="edit-name">Name</Label>
            <Input id="edit-name" value={form.name} onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))} />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="edit-phone">Phone</Label>
              <Input id="edit-phone" value={form.phone} onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))} />
            </div>
            <div>
              <Label htmlFor="edit-department">Department</Label>
              <Input id="edit-department" value={form.department} onChange={(e) => setForm((f) => ({ ...f, department: e.target.value }))} />
            </div>
          </div>
          <Button type="submit" disabled={updateMutation.isPending} className="w-fit">
            {updateMutation.isPending ? 'Saving…' : 'Save Changes'}
          </Button>
        </form>
      )}
    </Dialog>
  )
}

function ResetPasswordDialog({ supervisor, onClose }: { supervisor: User | null; onClose: () => void }) {
  const { toast } = useToast()
  const resetMutation = useResetSupervisorPassword()
  const [newPassword, setNewPassword] = useState('')

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    if (!supervisor) return
    try {
      await resetMutation.mutateAsync({ id: supervisor.id, newPassword })
      toast(`Password reset for ${supervisor.name}.`, 'success')
      setNewPassword('')
      onClose()
    } catch (err) {
      toast(err instanceof ApiError ? err.message : 'Could not reset password.', 'error')
    }
  }

  return (
    <Dialog open={!!supervisor} onClose={onClose} title="Reset Password">
      <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
        <p className="text-sm text-[var(--color-muted)]">
          Set a new temporary password for {supervisor?.name}. Share it with them securely.
        </p>
        <div>
          <Label htmlFor="reset-password">New Password</Label>
          <Input id="reset-password" type="text" required minLength={8} value={newPassword} onChange={(e) => setNewPassword(e.target.value)} />
        </div>
        <Button type="submit" disabled={resetMutation.isPending} className="w-fit">
          {resetMutation.isPending ? 'Resetting…' : 'Reset Password'}
        </Button>
      </form>
    </Dialog>
  )
}

export function SupervisorsPage() {
  const { data: supervisors = [], isLoading } = useSupervisors()
  const statusMutation = useSetSupervisorStatus()
  const { toast } = useToast()

  const [createOpen, setCreateOpen] = useState(false)
  const [editing, setEditing] = useState<User | null>(null)
  const [resetting, setResetting] = useState<User | null>(null)

  async function toggleStatus(supervisor: User) {
    const next = supervisor.status === 'ACTIVE' ? 'INACTIVE' : 'ACTIVE'
    try {
      await statusMutation.mutateAsync({ id: supervisor.id, status: next })
      toast(`${supervisor.name} is now ${next.toLowerCase()}.`, 'success')
    } catch (err) {
      toast(err instanceof ApiError ? err.message : 'Could not update status.', 'error')
    }
  }

  return (
    <AppLayout title="Supervisors" navItems={ADMIN_NAV}>
      <div className="mb-4 flex justify-end">
        <Button onClick={() => setCreateOpen(true)}>+ Add Supervisor</Button>
      </div>

      <Card>
        <CardContent className="pt-5">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--color-border)] text-left text-xs uppercase text-[var(--color-muted)]">
                  <th className="py-2">Name</th>
                  <th className="py-2">Email</th>
                  <th className="py-2">Phone</th>
                  <th className="py-2">Department</th>
                  <th className="py-2">Status</th>
                  <th className="py-2" />
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  <tr><td colSpan={6} className="py-6 text-center text-[var(--color-muted)]">Loading…</td></tr>
                ) : supervisors.length === 0 ? (
                  <tr><td colSpan={6} className="py-6 text-center text-[var(--color-muted)]">No supervisors yet.</td></tr>
                ) : (
                  supervisors.map((s) => (
                    <tr key={s.id} className="border-b border-[var(--color-border)]/60">
                      <td className="py-2.5">{s.name}</td>
                      <td className="py-2.5">{s.email}</td>
                      <td className="py-2.5">{s.phone || '—'}</td>
                      <td className="py-2.5">{s.department || '—'}</td>
                      <td className="py-2.5">
                        <span className={s.status === 'ACTIVE' ? 'text-[var(--color-success)]' : 'text-[var(--color-danger)]'}>
                          {s.status}
                        </span>
                      </td>
                      <td className="py-2.5">
                        <div className="flex gap-2">
                          <Link
                            to={`/admin/attendance?supervisor_id=${s.id}`}
                            className="inline-flex h-8 items-center rounded-md border border-[var(--color-border)] px-3 text-xs font-medium hover:bg-gray-50"
                          >
                            View Attendance
                          </Link>
                          <Button variant="outline" size="sm" onClick={() => setEditing(s)}>Edit</Button>
                          <Button variant="outline" size="sm" onClick={() => setResetting(s)}>Reset Password</Button>
                          <Button
                            variant={s.status === 'ACTIVE' ? 'destructive' : 'secondary'}
                            size="sm"
                            onClick={() => toggleStatus(s)}
                          >
                            {s.status === 'ACTIVE' ? 'Deactivate' : 'Activate'}
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      <CreateSupervisorDialog open={createOpen} onClose={() => setCreateOpen(false)} />
      <EditSupervisorDialog supervisor={editing} onClose={() => setEditing(null)} />
      <ResetPasswordDialog supervisor={resetting} onClose={() => setResetting(null)} />
    </AppLayout>
  )
}
