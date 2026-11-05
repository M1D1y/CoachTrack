import { useState, type FormEvent } from 'react'
import { Alert, Box, Button, Card, CardContent, Chip, Divider, Stack, TextField, Typography } from '@mui/material'
import { AthleteDetails } from '../entities/AthleteDetails'
import type { Invitation, User } from '../entities/types'
import { HealthRecords } from '../features/HealthRecords'
import { IncomingInvitations } from '../features/IncomingInvitations'
import { InviteForm } from '../features/InviteForm'
import { ProfileEditor } from '../features/ProfileEditor'
import { useAuth } from '../features/auth'
import { api } from '../shared/api/client'
import { useResource } from '../shared/api/useResource'
import { RemoteDataBoundary } from '../shared/RemoteDataBoundary'
import { SectionHeader } from '../shared/SectionHeader'

function TrainerAthletes() {
  const { user } = useAuth()
  const [search, setSearch] = useState('')
  const [query, setQuery] = useState('')
  const [selected, setSelected] = useState<User | null>(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)
  const data = useResource(query, async (signal) => {
    const [members, sent] = await Promise.all([
      api<User[]>(`/athletes${query ? `?q=${encodeURIComponent(query)}` : ''}`, { signal }),
      api<Invitation[]>('/invitations/sent', { signal }),
    ])
    return { members, sent }
  })
  const remove = async (publicId: string) => {
    await api<void>(`/team/athletes/${encodeURIComponent(publicId)}`, { method: 'DELETE' })
    setSelected(null); data.refresh()
  }
  const cancel = async (id: number) => {
    setBusy(true); setError('')
    try { await api(`/invitations/${id}/cancel`, { method: 'POST' }); data.refresh() }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Не удалось отменить приглашение') }
    finally { setBusy(false) }
  }
  const clearHistory = async () => {
    setBusy(true); setError('')
    try { await api<void>('/invitations/sent/history', { method: 'DELETE' }); data.refresh() }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Не удалось очистить историю приглашений') }
    finally { setBusy(false) }
  }
  const submit = (event: FormEvent) => { event.preventDefault(); setQuery(search.trim().replace(/\s+/g, ' ')) }
  return <>
    <SectionHeader title="Спортсмены" subtitle="Состав команды и информация о спортсменах" />
    <Stack spacing={3}>
      {user && <Card><CardContent><Typography variant="h6">Мой профиль</Typography>
        <Typography>{user.name}</Typography><Typography color="text.secondary">{user.sport ?? 'Вид спорта не указан'}</Typography>
        <ProfileEditor user={user} />
      </CardContent></Card>}
      <Card><CardContent><Typography variant="h6" gutterBottom>Мои спортсмены</Typography>
        <Box component="form" onSubmit={submit}><Stack direction="row" spacing={1} sx={{ my: 2 }}>
          <TextField label="Поиск по ФИО" type="search" value={search} inputProps={{ maxLength: 100 }}
            onChange={(event) => setSearch(event.target.value)} fullWidth />
          <Button type="submit" variant="contained">Найти</Button>
        </Stack></Box>
        <RemoteDataBoundary loading={data.loading} error={data.error} retry={data.refresh}>
          <Stack divider={<Divider flexItem />}>
            {data.data?.members.map((athlete) => <Box key={athlete.public_id} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', py: 2, gap: 2 }}>
              <Box><Typography fontWeight={700}>{athlete.name}</Typography>
                <Typography color="text.secondary">{athlete.sport ?? 'Вид спорта не указан'}</Typography></Box>
              <Button variant="outlined" onClick={() => setSelected(athlete)}>Подробнее</Button>
            </Box>)}
            {data.data?.members.length === 0 && <Typography color="text.secondary" sx={{ py: 2 }}>
              {query ? 'Спортсмены не найдены. Проверьте ФИО.' : 'Спортсменов пока нет.'}
            </Typography>}
          </Stack>
        </RemoteDataBoundary>
      </CardContent></Card>
      <Card><CardContent><InviteForm onChanged={data.refresh} /></CardContent></Card>
      <Card><CardContent>
        <Stack direction="row" justifyContent="space-between" alignItems="center" flexWrap="wrap" gap={1} sx={{ mb: 1 }}>
          <Typography variant="h6">Отправленные приглашения</Typography>
          {data.data?.sent.some((item) => item.status !== 'pending') &&
            <Button variant="contained" disabled={busy} onClick={() => void clearHistory()}>Очистить историю</Button>}
        </Stack>
        {error && <Alert severity="error">{error}</Alert>}
        <RemoteDataBoundary loading={data.loading} error={data.error} retry={data.refresh}>
          {data.data?.sent.length === 0 && <Typography color="text.secondary">Приглашений нет</Typography>}
          <Stack spacing={1}>{data.data?.sent.map((item) => <Box key={item.id} sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
            <Typography>{item.athlete_name}</Typography><Chip size="small" label={item.status} />
            {item.status === 'pending' && <Button size="small" disabled={busy} onClick={() => void cancel(item.id)}>Отменить</Button>}
          </Box>)}</Stack>
        </RemoteDataBoundary>
      </CardContent></Card>
    </Stack>
    <AthleteDetails athlete={selected} onClose={() => setSelected(null)} onRemove={remove} />
  </>
}

function AthleteProfile({ user }: { user: User }) {
  const { reloadUser } = useAuth()
  const data = useResource(user.public_id, async (signal) => {
    const [trainer, incoming] = await Promise.all([
      api<User | null>('/team/my-trainer', { signal }),
      api<Invitation[]>('/invitations/incoming', { signal }),
    ])
    return { trainer, incoming }
  })
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const leave = async () => {
    if (!window.confirm('Прекратить связь с тренером? Ваша история сохранится.')) return
    setBusy(true); setError('')
    try { await api<void>('/team/my-trainer', { method: 'DELETE' }); data.refresh(); await reloadUser() }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Не удалось открепиться') }
    finally { setBusy(false) }
  }
  return <>
    <SectionHeader title="Спортсмены" subtitle="Мой профиль и связь с тренером" />
    <Stack spacing={3}>
      <Card><CardContent><Typography variant="h6" gutterBottom>Личная информация</Typography>
        <Typography fontWeight={700}>{user.name}</Typography>
        <Typography color="text.secondary">{user.sport ?? 'Вид спорта не указан'}{user.age !== null ? ` · ${user.age} лет` : ''}</Typography>
        <ProfileEditor user={user} />
        <Divider sx={{ my: 2 }} />
        <Typography variant="h6" gutterBottom>Мой тренер</Typography>
        {error && <Alert severity="error">{error}</Alert>}
        <RemoteDataBoundary loading={data.loading} error={data.error} retry={data.refresh}>
          {data.data?.trainer ? <><Typography>{data.data.trainer.name}</Typography>
            <Button size="small" disabled={busy} color="error" onClick={() => void leave()}>Открепиться от тренера</Button></>
            : <Typography color="text.secondary">Тренер ещё не подключён</Typography>}
        </RemoteDataBoundary>
      </CardContent></Card>
      <RemoteDataBoundary loading={data.loading} error={data.error} retry={data.refresh}>
        {data.data && <IncomingInvitations items={data.data.incoming} onChanged={data.refresh} />}
      </RemoteDataBoundary>
      <Card><CardContent><HealthRecords athletePublicId={user.public_id} editable={false} /></CardContent></Card>
    </Stack>
  </>
}

export function AthletesPage() {
  const { user } = useAuth()
  if (!user) return null
  return user.role === 'trainer' ? <TrainerAthletes /> : <AthleteProfile user={user} />
}
