import { Alert, Box, Button, Fade, Stack, TextField, Typography } from '@mui/material'
import { useState, type FormEvent } from 'react'
import type { Athlete } from '../entities/types'
import { matchesAthlete } from '../shared/search'
import { useDemoTeam } from './demoTeam'

export function InviteForm() {
  const { athletes, invite } = useDemoTeam()
  const [query, setQuery] = useState('')
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [choices, setChoices] = useState<Athlete[]>([])

  const send = (athlete: Athlete) => {
    const result = invite(athlete.id)
    setError(result.ok ? '' : result.message)
    setMessage(result.ok ? result.message : '')
    setChoices([])
    if (result.ok) setQuery('')
  }

  const submit = (event: FormEvent) => {
    event.preventDefault()
    setMessage('')
    setChoices([])
    if (!query.trim()) {
      setError('Введите ID или ФИО спортсмена.')
      return
    }
    const matches = athletes.filter((athlete) => matchesAthlete(athlete, query))
    if (matches.length === 0) {
      setError('Спортсмен не найден. Проверьте ID или имя.')
    } else if (matches.length === 1) {
      send(matches[0])
    } else {
      setError('Найдено несколько спортсменов. Выберите нужного по ID.')
      setChoices(matches)
    }
  }

  return <Box component="form" onSubmit={submit}>
    <Typography variant="h6" gutterBottom>Пригласить спортсмена</Typography>
    <Typography color="text.secondary" sx={{ mb: 2 }}>Демо-приглашение по ID или ФИО внутри приложения.</Typography>
    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.5}>
      <TextField label="ID или ФИО спортсмена" size="small" fullWidth value={query}
        error={Boolean(error)} helperText={error || undefined}
        onChange={(event) => { setQuery(event.target.value); setError(''); setMessage(''); setChoices([]) }} />
      <Button type="submit" variant="contained" sx={{ whiteSpace: 'nowrap' }}>Пригласить</Button>
    </Stack>
    {choices.length > 0 && <Stack spacing={1} sx={{ mt: 2 }}>
      {choices.map((athlete) => <Button key={athlete.id} variant="outlined" onClick={() => send(athlete)}>
        {athlete.name} · ID {athlete.id}
      </Button>)}
    </Stack>}
    {message && <Fade in><Alert severity="success" sx={{ mt: 2 }}>{message}</Alert></Fade>}
  </Box>
}
