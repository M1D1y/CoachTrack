export type Role = 'trainer' | 'athlete'
export type Attendance = 'attended' | 'missed' | 'planned'

export interface Injury { title: string; date: string; note: string }
export interface Nutrition { date: string; title: string; note: string }
export interface Athlete {
  id: number
  name: string
  sport: string
  age: number
  trainerId: number | null
  injuries: Injury[]
  nutrition: Nutrition[]
}
export interface Training {
  id: number
  athleteId: number
  day: number
  time: string
  title: string
  description: string
  attendance: Attendance
}
export interface Invitation {
  id: number
  trainerId: number
  athleteId: number
  status: 'pending' | 'accepted' | 'rejected'
}
