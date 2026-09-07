import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select } from '@/components/ui/select'
import { Textarea } from '@/components/ui/textarea'
import { WorkerNameField } from '@/components/WorkerNameField'
import type { AttendanceRowInput, AttendanceStatus } from '@/types/attendance'
import { ATTENDANCE_STATUSES } from '@/types/attendance'
import { zodResolver } from '@hookform/resolvers/zod'
import { Controller, useForm } from 'react-hook-form'
import { z } from 'zod'

const STATUS_LABELS: Record<AttendanceStatus, string> = {
  PRESENT: 'Present',
  ABSENT: 'Absent',
  HALF_DAY: 'Half Day',
  LEAVE: 'Leave',
}

const attendanceRowSchema = z
  .object({
    attendance_date: z.string().min(1, 'Attendance date is required'),
    worker_name: z.string().min(1, 'Worker name is required').max(150),
    attendance_status: z.enum(['PRESENT', 'ABSENT', 'HALF_DAY', 'LEAVE']),
    input_parts: z.coerce.number({ invalid_type_error: 'Enter a valid number' }).min(0, 'Must be 0 or greater'),
    total_working_hours: z.coerce
      .number({ invalid_type_error: 'Enter a valid number' })
      .min(0, 'Must be 0 or greater'),
    machine_stopped_time: z.coerce
      .number({ invalid_type_error: 'Enter a valid number' })
      .min(0, 'Must be 0 or greater'),
    remarks: z.string().max(2000),
  })
  .refine(
    (data) => data.attendance_status === 'ABSENT' || data.machine_stopped_time <= data.total_working_hours,
    { message: 'Machine stopped time cannot exceed total working hours.', path: ['machine_stopped_time'] },
  )

export type AttendanceFormValues = z.infer<typeof attendanceRowSchema>

export function AttendanceForm({
  defaultValues,
  onSubmit,
  submitLabel = 'Save Attendance',
  isSubmitting = false,
}: {
  defaultValues: AttendanceFormValues
  onSubmit: (values: AttendanceRowInput) => Promise<void> | void
  submitLabel?: string
  isSubmitting?: boolean
}) {
  const {
    register,
    handleSubmit,
    control,
    watch,
    formState: { errors },
  } = useForm<AttendanceFormValues>({
    resolver: zodResolver(attendanceRowSchema),
    defaultValues,
  })

  const status = watch('attendance_status')
  const isAbsent = status === 'ABSENT'

  return (
    <form
      className="flex flex-col gap-4"
      onSubmit={handleSubmit((values) => onSubmit(values))}
      noValidate
    >
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="attendance_date">Attendance Date</Label>
          <Input id="attendance_date" type="date" {...register('attendance_date')} />
          {errors.attendance_date && (
            <p className="mt-1 text-xs text-[var(--color-danger)]">{errors.attendance_date.message}</p>
          )}
        </div>
        <div>
          <Label htmlFor="attendance_status">Attendance Status</Label>
          <Select id="attendance_status" {...register('attendance_status')}>
            {ATTENDANCE_STATUSES.map((s) => (
              <option key={s} value={s}>
                {STATUS_LABELS[s]}
              </option>
            ))}
          </Select>
        </div>
      </div>

      <div>
        <Label htmlFor="worker_name">Worker / Employee Name</Label>
        <Controller
          control={control}
          name="worker_name"
          render={({ field }) => (
            <WorkerNameField id="worker_name" value={field.value} onChange={field.onChange} />
          )}
        />
        {errors.worker_name && <p className="mt-1 text-xs text-[var(--color-danger)]">{errors.worker_name.message}</p>}
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div>
          <Label htmlFor="input_parts">Input Parts Number</Label>
          <Input
            id="input_parts"
            type="number"
            min={0}
            step="1"
            disabled={isAbsent}
            {...register('input_parts')}
          />
          {errors.input_parts && <p className="mt-1 text-xs text-[var(--color-danger)]">{errors.input_parts.message}</p>}
        </div>
        <div>
          <Label htmlFor="total_working_hours">Total Working Hours</Label>
          <Input
            id="total_working_hours"
            type="number"
            min={0}
            step="0.5"
            disabled={isAbsent}
            {...register('total_working_hours')}
          />
          {errors.total_working_hours && (
            <p className="mt-1 text-xs text-[var(--color-danger)]">{errors.total_working_hours.message}</p>
          )}
        </div>
        <div>
          <Label htmlFor="machine_stopped_time">Machine Stopped Time</Label>
          <Input
            id="machine_stopped_time"
            type="number"
            min={0}
            step="0.25"
            disabled={isAbsent}
            {...register('machine_stopped_time')}
          />
          {errors.machine_stopped_time && (
            <p className="mt-1 text-xs text-[var(--color-danger)]">{errors.machine_stopped_time.message}</p>
          )}
        </div>
      </div>
      {isAbsent && (
        <p className="-mt-2 text-xs text-[var(--color-muted)]">
          Input parts, working hours, and machine stopped time are set to 0 automatically for Absent status.
        </p>
      )}

      <div>
        <Label htmlFor="remarks">Remarks (optional)</Label>
        <Textarea id="remarks" rows={2} {...register('remarks')} />
      </div>

      <Button type="submit" disabled={isSubmitting} className="w-fit">
        {isSubmitting ? 'Saving…' : submitLabel}
      </Button>
    </form>
  )
}
