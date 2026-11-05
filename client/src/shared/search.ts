export function normalizeFullName(value: string): string {
  return value.trim().replace(/\s+/g, ' ').toLocaleLowerCase('ru-RU')
}

export function validNamePart(value: string): boolean {
  const part = value.trim()
  return part.length >= 1 && part.length <= 60 && /^\p{L}+(?:-\p{L}+)*$/u.test(part)
}
