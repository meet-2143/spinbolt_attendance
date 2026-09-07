import { Input } from '@/components/ui/input'
import { useWorkerNames } from '@/hooks/useAttendance'
import { useId } from 'react'

export function WorkerNameField({
  id,
  value,
  onChange,
  placeholder = 'Start typing a worker name…',
}: {
  id?: string
  value: string
  onChange: (value: string) => void
  placeholder?: string
}) {
  const datalistId = useId()
  const { data: suggestions = [] } = useWorkerNames(value)

  return (
    <>
      <Input
        id={id}
        list={datalistId}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        autoComplete="off"
      />
      <datalist id={datalistId}>
        {suggestions.map((name) => (
          <option key={name} value={name} />
        ))}
      </datalist>
    </>
  )
}
