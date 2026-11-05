import { useState, type FormEvent } from 'react'
import { Alert, Box, Button, Dialog, DialogActions, DialogContent, DialogTitle, Divider, MenuItem, Stack, TextField, Typography } from '@mui/material'
import type { Injury, Nutrition } from '../entities/types'
import { api } from '../shared/api/client'
import { useResource } from '../shared/api/useResource'
import { RemoteDataBoundary } from '../shared/RemoteDataBoundary'
import { isoLocalDate } from '../shared/date'

type Kind = 'injuries' | 'nutrition'
type RecordItem = Injury | Nutrition

export function HealthRecords({ athletePublicId, editable }: { athletePublicId: string; editable: boolean }) {
  const endpoint = `/athletes/${encodeURIComponent(athletePublicId)}`
  const resource = useResource(athletePublicId, async (signal) => {
    const [injuries, nutrition] = await Promise.all([
      api<Injury[]>(`${endpoint}/injuries`, { signal }),
      api<Nutrition[]>(`${endpoint}/nutrition`, { signal }),
    ])
    return { injuries, nutrition }
  })
  const [editing, setEditing] = useState<{ kind: Kind; item: RecordItem | null } | null>(null)
  const [deleting, setDeleting] = useState<{ kind: Kind; id: number } | null>(null)
  const [title, setTitle] = useState('')
  const [date, setDate] = useState('')
  const [note, setNote] = useState('')
  const [severity, setSeverity] = useState<Injury['severity']>('mild')
  const [status, setStatus] = useState<Injury['status']>('active')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')

  const open = (kind: Kind, item: RecordItem | null = null) => {
    setEditing({ kind, item }); setTitle(item?.title ?? ''); setDate(item?.date ?? isoLocalDate(new Date()))
    setNote(item?.note ?? ''); setSeverity(item && 'severity' in item ? item.severity : 'mild')
    setStatus(item && 'status' in item ? item.status : 'active'); setError('')
  }
  const save = async (event: FormEvent) => {
    event.preventDefault()
    if (!editing || !title.trim() || !date) { setError('Укажите название и дату.'); return }
    setBusy(true); setError('')
    const body = editing.kind === 'injuries'
      ? { title: title.trim(), date, note, severity, status }
      : { title: title.trim(), date, note }
    const path = editing.item ? `/${editing.kind}/${editing.item.id}` : `${endpoint}/${editing.kind}`
    try {
      await api(path, { method: editing.item ? 'PATCH' : 'POST', body: JSON.stringify(body) })
      setEditing(null); resource.refresh()
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Не удалось сохранить запись') }
    finally { setBusy(false) }
  }
  const remove = async () => {
    if (!deleting) return
    setBusy(true); setError('')
    try { await api(`/${deleting.kind}/${deleting.id}`, { method: 'DELETE' }); setDeleting(null); resource.refresh() }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Не удалось удалить запись') }
    finally { setBusy(false) }
  }
  const section = (kind: Kind, items: RecordItem[]) => <Box>
    <Stack direction="row" justifyContent="space-between" alignItems="center">
      <Typography variant="h6">{kind === 'injuries' ? 'Травмы' : 'Питание'}</Typography>
      {editable && <Button size="small" onClick={() => open(kind)}>Добавить</Button>}
    </Stack>
    {items.length === 0 && <Typography color="text.secondary">Записей пока нет</Typography>}
    {items.map((item) => <Box key={item.id} sx={{ py: 1 }}>
      <Typography fontWeight={600}>{item.title} · {item.date}</Typography>
      <Typography variant="body2" color="text.secondary">{item.note}</Typography>
      {'severity' in item && <Typography variant="body2" color="text.secondary">Тяжесть: {item.severity}; статус: {item.status}</Typography>}
      {editable && <Stack direction="row" spacing={1}>
        <Button size="small" onClick={() => open(kind, item)}>Изменить</Button>
        <Button size="small" color="error" onClick={() => { setDeleting({ kind, id: item.id }); setError('') }}>Удалить</Button>
      </Stack>}
    </Box>)}
  </Box>
  return <>
    <RemoteDataBoundary loading={resource.loading} error={resource.error} retry={resource.refresh}>
      {resource.data && <Stack spacing={2}>{section('injuries', resource.data.injuries)}<Divider />{section('nutrition', resource.data.nutrition)}</Stack>}
    </RemoteDataBoundary>
    <Dialog open={Boolean(editing)} onClose={() => setEditing(null)} fullWidth maxWidth="sm">
      <DialogTitle>{editing?.item ? 'Изменить запись' : 'Добавить запись'}</DialogTitle>
      <Box component="form" onSubmit={(event) => void save(event)}>
        <DialogContent><Stack spacing={2}>
          {error && <Alert severity="error">{error}</Alert>}
          <TextField label="Название" value={title} onChange={(event) => setTitle(event.target.value)} inputProps={{ maxLength: 200 }} required />
          <TextField label="Дата" type="date" value={date} onChange={(event) => setDate(event.target.value)} InputLabelProps={{ shrink: true }} required />
          <TextField label="Описание" multiline minRows={2} value={note} onChange={(event) => setNote(event.target.value)} />
          {editing?.kind === 'injuries' && <>
            <TextField select label="Степень тяжести" value={severity} onChange={(event) => setSeverity(event.target.value as Injury['severity'])}>
              <MenuItem value="mild">Лёгкая</MenuItem><MenuItem value="moderate">Средняя</MenuItem><MenuItem value="severe">Тяжёлая</MenuItem>
            </TextField>
            <TextField select label="Статус" value={status} onChange={(event) => setStatus(event.target.value as Injury['status'])}>
              <MenuItem value="active">Активная</MenuItem><MenuItem value="healed">Залечена</MenuItem>
            </TextField>
          </>}
        </Stack></DialogContent>
        <DialogActions><Button onClick={() => setEditing(null)}>Отмена</Button><Button type="submit" variant="contained" disabled={busy}>Сохранить</Button></DialogActions>
      </Box>
    </Dialog>
    <Dialog open={Boolean(deleting)} onClose={() => setDeleting(null)}>
      <DialogTitle>Удалить запись?</DialogTitle><DialogContent>{error && <Alert severity="error">{error}</Alert>}</DialogContent>
      <DialogActions><Button onClick={() => setDeleting(null)}>Отмена</Button><Button color="error" disabled={busy} onClick={() => void remove()}>Удалить</Button></DialogActions>
    </Dialog>
  </>
}
