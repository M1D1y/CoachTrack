import { createContext, useContext, useState, type ReactNode } from 'react'
import type { Athlete, Invitation } from '../entities/types'
import { athletes as initialAthletes, trainer } from '../shared/demoData'

interface DemoTeamContextValue {
  athletes: Athlete[]
  members: Athlete[]
  invitations: Invitation[]
  remove: (id: number) => void
  invite: (athleteId: number) => { ok: boolean; message: string }
  respond: (invitationId: number, athleteId: number, accept: boolean) => { ok: boolean; message: string }
}

const DemoTeamContext = createContext<DemoTeamContextValue | null>(null)

export function DemoTeamProvider({ children }: { children: ReactNode }) {
  const [athletes, setAthletes] = useState(initialAthletes)
  const [invitations, setInvitations] = useState<Invitation[]>([])
  const members = athletes.filter((athlete) => athlete.trainerId === trainer.id)

  const remove = (id: number) => {
    setAthletes((items) => items.map((athlete) =>
      athlete.id === id && athlete.trainerId === trainer.id
        ? { ...athlete, trainerId: null }
        : athlete,
    ))
  }

  const invite = (athleteId: number) => {
    const athlete = athletes.find((item) => item.id === athleteId)
    if (!athlete) return { ok: false, message: 'Спортсмен не найден. Проверьте ID или имя.' }
    if (athlete.trainerId !== null) return { ok: false, message: 'У этого спортсмена уже есть тренер.' }
    if (invitations.some((item) => item.athleteId === athleteId && item.trainerId === trainer.id && item.status === 'pending')) {
      return { ok: false, message: 'Ожидающее приглашение уже отправлено.' }
    }

    setInvitations((items) => [...items, {
      id: Math.max(0, ...items.map((item) => item.id)) + 1,
      trainerId: trainer.id,
      athleteId,
      status: 'pending',
    }])
    return { ok: true, message: `Приглашение для ${athlete.name} (ID ${athlete.id}) отправлено.` }
  }

  const respond = (invitationId: number, athleteId: number, accept: boolean) => {
    const invitation = invitations.find((item) => item.id === invitationId)
    const athlete = athletes.find((item) => item.id === athleteId)
    if (!invitation || invitation.athleteId !== athleteId || invitation.status !== 'pending' || !athlete) {
      return { ok: false, message: 'Приглашение уже обработано или недоступно.' }
    }
    if (accept && athlete.trainerId !== null) return { ok: false, message: 'У вас уже есть тренер.' }

    setInvitations((items) => items.map((item) => item.id === invitationId
      ? { ...item, status: accept ? 'accepted' : 'rejected' }
      : item))
    if (accept) {
      setAthletes((items) => items.map((item) => item.id === athleteId
        ? { ...item, trainerId: invitation.trainerId }
        : item))
    }
    return { ok: true, message: accept ? 'Приглашение принято. Тренер подключён.' : 'Приглашение отклонено.' }
  }

  return <DemoTeamContext.Provider value={{ athletes, members, invitations, remove, invite, respond }}>
    {children}
  </DemoTeamContext.Provider>
}

export function useDemoTeam() {
  const context = useContext(DemoTeamContext)
  if (!context) throw new Error('DemoTeamProvider is missing')
  return context
}
