import type { Athlete } from '../entities/types'

export function normalizeFullName(value: string): string {
  return value.trim().replace(/\s+/g, ' ').toLocaleLowerCase('ru-RU')
}

export function validNamePart(value: string): boolean {
  const part = value.trim()
  return part.length >= 1 && part.length <= 60 && /^\p{L}+(?:-\p{L}+)*$/u.test(part)
}

export function matchesAthlete(athlete: Athlete, rawQuery: string): boolean {
  const query = normalizeFullName(rawQuery)
  if (!query) return true
  if (/^\d+$/.test(query)) return athlete.id === Number(query)

  const name = normalizeFullName(athlete.name)
  return query.split(' ').every((part) => name.includes(part))
}
