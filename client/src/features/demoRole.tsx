import { createContext, useContext, useState, type ReactNode } from 'react'
import type { Role } from '../entities/types'
import { initialAthleteId } from '../shared/demoData'

interface DemoRoleContextValue {
  role: Role
  setRole: (role: Role) => void
  athleteId: number
  setAthleteId: (id: number) => void
}
const DemoRoleContext = createContext<DemoRoleContextValue | null>(null)

export function DemoRoleProvider({ children }: { children: ReactNode }) {
  const [role, setRole] = useState<Role>('trainer')
  const [athleteId, setAthleteId] = useState(initialAthleteId)
  return <DemoRoleContext.Provider value={{ role, setRole, athleteId, setAthleteId }}>{children}</DemoRoleContext.Provider>
}

export function useDemoRole() {
  const value = useContext(DemoRoleContext)
  if (!value) throw new Error('Демонстрационный режим не подключён')
  return value
}
