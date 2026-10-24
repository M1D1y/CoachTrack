import { Box, Button, Card, CardContent, Chip, Divider, Stack, TextField, Typography } from '@mui/material'
import { useState } from 'react'
import { AthleteDetails } from '../entities/AthleteDetails'
import type { Athlete } from '../entities/types'
import { IncomingInvitations } from '../features/IncomingInvitations'
import { InviteForm } from '../features/InviteForm'
import { useDemoRole } from '../features/demoRole'
import { useDemoTeam } from '../features/demoTeam'
import { DemoDataBoundary, useDemoLoad } from '../shared/DemoDataBoundary'
import { SectionHeader } from '../shared/SectionHeader'
import { trainer } from '../shared/demoData'
import { matchesAthlete } from '../shared/search'

export function AthletesPage() {
  const { role, athleteId } = useDemoRole()
  const { athletes, members, remove } = useDemoTeam()
  const { status, retry, showError } = useDemoLoad(`${role}:${athleteId}`)
  const [selected, setSelected] = useState<Athlete | null>(null)
  const [search, setSearch] = useState('')
  const [submittedSearch, setSubmittedSearch] = useState('')
  const matchingAthletes = members.filter((athlete) => matchesAthlete(athlete, submittedSearch))
  const me = athletes.find((athlete) => athlete.id === athleteId)

  return <>
    <SectionHeader
      title="Спортсмены"
      subtitle={role === 'trainer' ? 'Состав команды и информация о спортсменах' : 'Мой профиль и связь с тренером'}
      action={<Button size="small" onClick={showError}>Показать ошибку загрузки</Button>}
    />
    <DemoDataBoundary status={status} onRetry={retry}>
      {role === 'trainer' ? <Stack spacing={3}>
        <Card><CardContent>
          <Typography variant="h6" gutterBottom>
            Мои спортсмены <Chip label={members.length} size="small" sx={{ ml: 1 }} />
          </Typography>
          <Stack direction="row" spacing={1} sx={{ my: 2 }}>
            <TextField
              label="Поиск по ID или ФИО"
              type="search"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              onKeyDown={(event) => { if (event.key === 'Enter') setSubmittedSearch(search) }}
              fullWidth
            />
            <Button variant="contained" onClick={() => setSubmittedSearch(search)}>Найти</Button>
          </Stack>
          <Stack divider={<Divider flexItem />}>
            {matchingAthletes.map((athlete) => <Box key={athlete.id} sx={{
              display: 'flex', alignItems: { xs: 'flex-start', sm: 'center' },
              justifyContent: 'space-between', gap: 2, py: 2,
              flexDirection: { xs: 'column', sm: 'row' },
            }}>
              <Box>
                <Typography fontWeight={700}>{athlete.name}</Typography>
                <Typography color="text.secondary">ID {athlete.id} · {athlete.sport}</Typography>
              </Box>
              <Button variant="outlined" onClick={() => setSelected(athlete)}>Подробнее</Button>
            </Box>)}
            {matchingAthletes.length === 0 && <Typography color="text.secondary" sx={{ py: 2 }}>
              {members.length === 0 && !submittedSearch.trim()
                ? 'В команде пока нет спортсменов.'
                : 'Спортсмены не найдены. Проверьте ID или имя.'}
            </Typography>}
          </Stack>
        </CardContent></Card>
        <Card><CardContent><InviteForm /></CardContent></Card>
      </Stack> : me ? <Stack spacing={3}>
        <Card><CardContent>
          <Typography variant="h6" gutterBottom>Личная информация</Typography>
          <Typography fontWeight={700}>{me.name} · ID {me.id}</Typography>
          <Typography color="text.secondary">{me.sport} · {me.age} лет</Typography>
          <Divider sx={{ my: 2 }} />
          <Typography variant="h6" gutterBottom>Мой тренер</Typography>
          {me.trainerId === trainer.id ? <>
            <Typography>{trainer.name}</Typography>
            <Typography color="text.secondary">{trainer.sport}</Typography>
          </> : <Typography color="text.secondary">Тренер ещё не подключён</Typography>}
        </CardContent></Card>
        <IncomingInvitations key={athleteId} />
        <Card><CardContent>
          <Typography variant="h6" gutterBottom>Травмы</Typography>
          {me.injuries.length ? me.injuries.map((item) => <Box key={`${item.title}-${item.date}`} mb={1}>
            <Typography fontWeight={600}>{item.title} · {item.date}</Typography>
            <Typography color="text.secondary">{item.note}</Typography>
          </Box>) : <Typography color="text.secondary">Записей нет</Typography>}
          <Divider sx={{ my: 2 }} />
          <Typography variant="h6" gutterBottom>Питание</Typography>
          {me.nutrition.length ? me.nutrition.map((item) => <Box key={`${item.title}-${item.date}`}>
            <Typography fontWeight={600}>{item.title} · {item.date}</Typography>
            <Typography color="text.secondary">{item.note}</Typography>
          </Box>) : <Typography color="text.secondary">Записей нет</Typography>}
        </CardContent></Card>
      </Stack> : <Typography color="text.secondary">Спортсмен не найден.</Typography>}
    </DemoDataBoundary>
    <AthleteDetails
      athlete={role === 'trainer' ? selected : null}
      onClose={() => setSelected(null)}
      onRemove={(id) => { remove(id); setSelected(null) }}
    />
  </>
}
