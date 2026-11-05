import { useState, type FormEvent } from 'react'
import { Alert, Button, Dialog, DialogActions, DialogContent, DialogTitle, Stack, TextField } from '@mui/material'
import type { User } from '../entities/types'
import { useAuth } from './auth'
import { api } from '../shared/api/client'
import { validNamePart } from '../shared/search'

export function ProfileEditor({ user }: { user: User }) {
  const { reloadUser } = useAuth()
  const [open, setOpen] = useState(false)
  const [name, setName] = useState(user.name)
  const [age, setAge] = useState(user.age?.toString() ?? '')
  const [sport, setSport] = useState(user.sport ?? '')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const show = () => {
    setName(user.name); setAge(user.age?.toString() ?? ''); setSport(user.sport ?? '')
    setError(''); setOpen(true)
  }
  const save = async (event: FormEvent) => {
    event.preventDefault()
    const parts = name.trim().split(/\s+/)
    if (parts.length !== 3 || !parts.every(validNamePart)) { setError('Укажите фамилию, имя и отчество.'); return }
    if (age && (!Number.isInteger(Number(age)) || Number(age) < 0 || Number(age) > 120)) { setError('Возраст должен быть от 0 до 120 лет.'); return }
    setBusy(true); setError('')
    try {
      await api('/users/me', { method: 'PATCH', body: JSON.stringify({ name: parts.join(' '), age: age ? Number(age) : null, sport: sport.trim() || null }) })
      await reloadUser()
      setOpen(false)
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Не удалось обновить профиль') }
    finally { setBusy(false) }
  }
  return <><Button size="small" onClick={show}>Изменить профиль</Button>
    <Dialog open={open} onClose={() => setOpen(false)} fullWidth maxWidth="sm"><DialogTitle>Мой профиль</DialogTitle>
      <form onSubmit={(event) => void save(event)}><DialogContent><Stack spacing={2}>
        {error && <Alert severity="error">{error}</Alert>}
        <TextField label="Фамилия Имя Отчество" value={name} onChange={(event) => setName(event.target.value)} inputProps={{ maxLength: 200 }} required />
        <TextField label="Возраст" type="number" value={age} onChange={(event) => setAge(event.target.value)} inputProps={{ min: 0, max: 120 }} />
        <TextField label="Вид спорта" value={sport} onChange={(event) => setSport(event.target.value)} inputProps={{ maxLength: 100 }} />
      </Stack></DialogContent><DialogActions><Button onClick={() => setOpen(false)}>Отмена</Button>
        <Button type="submit" variant="contained" disabled={busy}>Сохранить</Button></DialogActions></form>
    </Dialog>
  </>
}
