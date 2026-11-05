import { useState, type FormEvent } from 'react'
import {
  Alert, Box, Button, Card, CardContent, Chip, Dialog, DialogActions, DialogContent,
  DialogTitle, Grid, MenuItem, Stack, TextField, Typography,
} from '@mui/material'
import type { Attendance, Training, User } from '../entities/types'
import { useAuth } from '../features/auth'
import { api } from '../shared/api/client'
import { useResource } from '../shared/api/useResource'
import { RemoteDataBoundary } from '../shared/RemoteDataBoundary'
import { addDays, formatDate, isoLocalDate, weekStart } from '../shared/date'
import { SectionHeader } from '../shared/SectionHeader'

const weekdays = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
const status: Record<Attendance, { label: string; color: 'success' | 'error' | 'default' }> = {
  attended: { label: 'Посещено', color: 'success' },
  missed: { label: 'Пропущено', color: 'error' },
  planned: { label: 'Запланировано', color: 'default' },
}

export function CalendarPage() {
  const { user } = useAuth()
  const [offset, setOffset] = useState(0)
  const start = addDays(weekStart(new Date()), offset * 7)
  const week = isoLocalDate(start)
  const resource = useResource(`${user?.public_id}:${week}`, async (signal) => {
    const [trainings, members] = await Promise.all([
      api<Training[]>(`/trainings?week_start=${week}`, { signal }),
      user?.role === 'trainer' ? api<User[]>('/athletes', { signal }) : Promise.resolve([]),
    ])
    return { trainings, members }
  })
  const [editor, setEditor] = useState<Training | 'new' | null>(null)
  const [deleting, setDeleting] = useState<Training | null>(null)
  const [athletePublicId, setAthletePublicId] = useState('')
  const [date, setDate] = useState(week)
  const [time, setTime] = useState('09:00')
  const [duration, setDuration] = useState(45)
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const open = (item?: Training) => {
    setEditor(item ?? 'new'); setError('')
    setAthletePublicId(item?.athlete_public_id ?? resource.data?.members[0]?.public_id ?? '')
    setDate(item?.date ?? week); setTime(item?.time.slice(0, 5) ?? '09:00')
    setDuration(item?.duration_minutes ?? 45); setTitle(item?.title ?? ''); setDescription(item?.description ?? '')
  }
  const save = async (event: FormEvent) => {
    event.preventDefault()
    if (!editor || !title.trim() || !date || !time || duration <= 0 || (editor === 'new' && !athletePublicId)) {
      setError('Заполните обязательные поля.'); return
    }
    setBusy(true); setError('')
    const values = { date, time, duration_minutes: duration, title: title.trim(), description }
    try {
      if (editor === 'new') await api('/trainings', { method: 'POST', body: JSON.stringify({ ...values, athlete_public_id: athletePublicId }) })
      else await api(`/trainings/${editor.id}`, { method: 'PATCH', body: JSON.stringify(values) })
      setEditor(null); resource.refresh()
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Не удалось сохранить тренировку') }
    finally { setBusy(false) }
  }
  const remove = async () => {
    if (!deleting) return
    setBusy(true); setError('')
    try { await api<void>(`/trainings/${deleting.id}`, { method: 'DELETE' }); setDeleting(null); resource.refresh() }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Не удалось удалить тренировку') }
    finally { setBusy(false) }
  }
  const attendance = async (item: Training, value: Attendance) => {
    setBusy(true); setError('')
    try { await api(`/trainings/${item.id}/attendance`, { method: 'PATCH', body: JSON.stringify({ attendance: value }) }); resource.refresh() }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Не удалось изменить посещаемость') }
    finally { setBusy(false) }
  }

  return <>
    <SectionHeader title="Календарь" subtitle={user?.role === 'trainer' ? 'Недельное расписание команды' : 'Мои тренировки на неделю'}
      action={user?.role === 'trainer' && <Button variant="contained" disabled={!resource.data?.members.length} onClick={() => open()}>Назначить тренировку</Button>} />
    {error && !editor && !deleting && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
    <Stack direction="row" spacing={1} alignItems="center" justifyContent="space-between" sx={{ mb: 2, flexWrap: 'wrap', gap: 1 }}>
      <Button variant="outlined" onClick={() => setOffset((value) => value - 1)}>← Ранее</Button>
      <Typography fontWeight={700} textAlign="center">{formatDate(start, { day: 'numeric', month: 'long' })} — {formatDate(addDays(start, 6), { day: 'numeric', month: 'long', year: 'numeric' })}</Typography>
      <Button variant="outlined" onClick={() => setOffset((value) => value + 1)}>Позже →</Button>
    </Stack>
    <RemoteDataBoundary loading={resource.loading} error={resource.error} retry={resource.refresh}>
      {resource.data?.trainings.length === 0 && <Typography color="text.secondary" sx={{ mb: 2 }}>Тренировок на эту неделю нет.</Typography>}
      <Grid container spacing={2}>{weekdays.map((name, day) => {
        const currentDate = isoLocalDate(addDays(start, day))
        const items = resource.data?.trainings.filter((item) => item.date === currentDate) ?? []
        return <Grid item xs={12} sm={6} md={4} key={name}><Card sx={{ height: '100%' }}><CardContent>
          <Typography fontWeight={700}>{name}</Typography>
          <Typography color="text.secondary" sx={{ mb: 2 }}>{formatDate(addDays(start, day), { day: 'numeric', month: 'long' })}</Typography>
          {items.map((item) => <Box key={item.id} sx={{ borderTop: '1px solid #e6ecef', pt: 1.5, pb: 1 }}>
            <Typography fontWeight={700}>{item.time.slice(0, 5)} · {item.title}</Typography>
            {user?.role === 'trainer' && <Typography variant="body2">{resource.data?.members.find((member) => member.public_id === item.athlete_public_id)?.name}</Typography>}
            <Typography variant="body2">{item.duration_minutes} мин.</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ my: 1 }}>{item.description}</Typography>
            <Chip size="small" label={status[item.attendance].label} color={status[item.attendance].color} variant="outlined" />
            {user?.role === 'trainer' && <Stack direction="row" spacing={1} sx={{ mt: 1 }} flexWrap="wrap">
              <Button size="small" disabled={busy} onClick={() => open(item)}>Изменить</Button>
              <Button size="small" color="error" disabled={busy} onClick={() => { setDeleting(item); setError('') }}>Удалить</Button>
              <TextField size="small" select label="Посещаемость" value={item.attendance} disabled={busy}
                onChange={(event) => void attendance(item, event.target.value as Attendance)} sx={{ minWidth: 150 }}>
                <MenuItem value="planned">Запланировано</MenuItem><MenuItem value="attended">Посещено</MenuItem><MenuItem value="missed">Пропущено</MenuItem>
              </TextField>
            </Stack>}
          </Box>)}
          {items.length === 0 && <Typography variant="body2" color="text.secondary">Тренировок нет</Typography>}
        </CardContent></Card></Grid>
      })}</Grid>
    </RemoteDataBoundary>
    <Dialog open={Boolean(editor)} onClose={() => setEditor(null)} fullWidth maxWidth="sm"><DialogTitle>{editor === 'new' ? 'Назначить тренировку' : 'Изменить тренировку'}</DialogTitle>
      <Box component="form" onSubmit={(event) => void save(event)}><DialogContent><Stack spacing={2}>
        {error && <Alert severity="error">{error}</Alert>}
        {editor === 'new' && <TextField select label="Спортсмен" value={athletePublicId} onChange={(event) => setAthletePublicId(event.target.value)} required>
          {resource.data?.members.map((member) => <MenuItem key={member.public_id} value={member.public_id}>{member.name}</MenuItem>)}
        </TextField>}
        <TextField label="Дата" type="date" value={date} onChange={(event) => setDate(event.target.value)} InputLabelProps={{ shrink: true }} required />
        <TextField label="Время" type="time" value={time} onChange={(event) => setTime(event.target.value)} InputLabelProps={{ shrink: true }} required />
        <TextField label="Продолжительность, мин." type="number" value={duration} onChange={(event) => setDuration(Number(event.target.value))} inputProps={{ min: 1 }} required />
        <TextField label="Название" value={title} onChange={(event) => setTitle(event.target.value)} inputProps={{ maxLength: 200 }} required />
        <TextField label="Описание" value={description} onChange={(event) => setDescription(event.target.value)} multiline minRows={2} />
      </Stack></DialogContent><DialogActions><Button onClick={() => setEditor(null)}>Отмена</Button>
        <Button type="submit" variant="contained" disabled={busy}>Сохранить</Button></DialogActions></Box>
    </Dialog>
    <Dialog open={Boolean(deleting)} onClose={() => setDeleting(null)}><DialogTitle>Удалить тренировку «{deleting?.title}»?</DialogTitle>
      <DialogContent>{error && <Alert severity="error">{error}</Alert>}</DialogContent>
      <DialogActions><Button onClick={() => setDeleting(null)}>Отмена</Button><Button color="error" disabled={busy} onClick={() => void remove()}>Удалить</Button></DialogActions>
    </Dialog>
  </>
}
