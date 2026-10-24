import type { Athlete } from '../entities/types'

export function matchesAthlete(athlete: Athlete, rawQuery: string): boolean {
  const query = rawQuery.trim().replace(/\s+/g, ' ').toLocaleLowerCase('ru-RU')
  if (!query) return true
  if (/^\d+$/.test(query)) return athlete.id === Number(query)

  const name = athlete.name.toLocaleLowerCase('ru-RU')
  return query.split(' ').every((part) => name.includes(part))
}
