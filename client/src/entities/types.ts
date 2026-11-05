export type Role = 'trainer' | 'athlete'
export type Attendance = 'planned' | 'attended' | 'missed'
export type RelationshipStatus = 'available' | 'pending' | 'team' | 'unavailable'

export interface User {
  public_id: string
  name: string
  role: Role
  age: number | null
  sport: string | null
  created_at: string
}

export interface SearchUser {
  public_id: string
  name: string
  sport: string | null
  relationship_status: RelationshipStatus
}

export interface Invitation {
  id: number
  trainer_public_id: string
  athlete_public_id: string
  trainer_name: string
  athlete_name: string
  status: 'pending' | 'accepted' | 'rejected' | 'cancelled'
  created_at: string
  responded_at: string | null
}

export interface Training {
  id: number
  athlete_public_id: string
  date: string
  time: string
  duration_minutes: number
  title: string
  description: string
  attendance: Attendance
  created_at: string
}

export interface Injury {
  id: number
  athlete_public_id: string
  title: string
  date: string
  note: string
  severity: 'mild' | 'moderate' | 'severe'
  status: 'active' | 'healed'
}

export interface Nutrition {
  id: number
  athlete_public_id: string
  date: string
  title: string
  note: string
}

export interface Summary {
  week_start: string
  athlete_count: number | null
  training_count: number
  attended: number
  missed: number
  attendance_percent: number
}
