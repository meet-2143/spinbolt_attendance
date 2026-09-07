import { api } from '@/lib/api'
import type { User, UserStatus } from '@/types/user'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'

export interface SupervisorInput {
  name: string
  email: string
  password: string
  phone?: string
  department?: string
}

export interface SupervisorUpdateInput {
  name?: string
  phone?: string
  department?: string
}

function invalidate(queryClient: ReturnType<typeof useQueryClient>) {
  queryClient.invalidateQueries({ queryKey: ['supervisors'] })
}

export function useSupervisors() {
  return useQuery<User[]>({
    queryKey: ['supervisors'],
    queryFn: () => api.get('/api/supervisors'),
  })
}

export function useCreateSupervisor() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (payload: SupervisorInput) => api.post<User>('/api/supervisors', payload),
    onSuccess: () => invalidate(queryClient),
  })
}

export function useUpdateSupervisor() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: SupervisorUpdateInput }) =>
      api.put<User>(`/api/supervisors/${id}`, payload),
    onSuccess: () => invalidate(queryClient),
  })
}

export function useSetSupervisorStatus() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: UserStatus }) =>
      api.patch<User>(`/api/supervisors/${id}/status`, { status }),
    onSuccess: () => invalidate(queryClient),
  })
}

export function useResetSupervisorPassword() {
  return useMutation({
    mutationFn: ({ id, newPassword }: { id: string; newPassword: string }) =>
      api.patch(`/api/supervisors/${id}/reset-password`, { new_password: newPassword }),
  })
}
