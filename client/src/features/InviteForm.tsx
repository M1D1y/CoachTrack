import { Alert, Box, Button, Chip, CircularProgress, Stack, TextField, Typography } from '@mui/material'
import { useEffect, useRef, useState, type FormEvent } from 'react'
import type { SearchUser } from '../entities/types'
import { api } from '../shared/api/client'

const labels = { available: 'Можно пригласить', pending: 'Приглашение отправлено', team: 'В команде', unavailable: 'Уже есть тренер' }

export function InviteForm({ onChanged }: { onChanged: () => void }) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchUser[]>([])
  const [searched, setSearched] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const searchController = useRef<AbortController | null>(null)
  useEffect(() => () => searchController.current?.abort(), [])
  const search = async (event: FormEvent) => {
    event.preventDefault()
    searchController.current?.abort()
    const controller = new AbortController()
    searchController.current = controller
    setError(''); setMessage('')
    const value = query.trim().replace(/\s+/g, ' ')
    if ((value.match(/\p{L}/gu) ?? []).length < 3) {
      setError('Введите не менее трёх букв ФИО.')
      return
    }
    setBusy(true)
    try {
      const found = await api<SearchUser[]>(`/athletes/search?q=${encodeURIComponent(value)}`, { signal: controller.signal })
      if (!controller.signal.aborted) { setResults(found); setSearched(true) }
    } catch (cause) { if (!controller.signal.aborted) setError(cause instanceof Error ? cause.message : 'Поиск не удался') }
    finally { if (!controller.signal.aborted) setBusy(false) }
  }
  const invite = async (athlete: SearchUser) => {
    setBusy(true); setError(''); setMessage('')
    try {
      await api('/invitations', { method: 'POST', body: JSON.stringify({ athlete_public_id: athlete.public_id }) })
      setMessage(`Приглашение для ${athlete.name} отправлено.`)
      setResults((items) => items.map((item) => item.public_id === athlete.public_id ? { ...item, relationship_status: 'pending' } : item))
      onChanged()
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Не удалось отправить приглашение') }
    finally { setBusy(false) }
  }
  return <Box>
    <Typography variant="h6" gutterBottom>Найти и пригласить спортсмена</Typography>
    <Box component="form" onSubmit={(event) => void search(event)}><Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
      <TextField label="ФИО спортсмена" size="small" inputProps={{ maxLength: 100 }} fullWidth value={query}
        onChange={(event) => { searchController.current?.abort(); setBusy(false); setQuery(event.target.value); setSearched(false); setResults([]); setError('') }} />
      <Button type="submit" variant="contained" disabled={busy}>{busy ? <CircularProgress size={20} /> : 'Найти'}</Button>
    </Stack></Box>
    {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
    {message && <Alert severity="success" sx={{ mt: 2 }}>{message}</Alert>}
    {searched && results.length === 0 && <Typography color="text.secondary" sx={{ mt: 2 }}>Спортсмены не найдены.</Typography>}
    <Stack spacing={1} sx={{ mt: 2 }}>
      {results.map((athlete) => <Box key={athlete.public_id} sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
        <Typography fontWeight={600}>{athlete.name}</Typography>
        {athlete.sport && <Typography color="text.secondary">{athlete.sport}</Typography>}
        <Chip size="small" label={labels[athlete.relationship_status]} />
        <Button size="small" disabled={busy || athlete.relationship_status !== 'available'} onClick={() => void invite(athlete)}>Пригласить</Button>
      </Box>)}
    </Stack>
  </Box>
}
