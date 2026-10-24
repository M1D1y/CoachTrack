import { Box, Button, Card, CardContent, Chip, Grid, Stack, Typography } from '@mui/material'
import { useState } from 'react'
import { useDemoRole } from '../features/demoRole'
import { trainings } from '../shared/demoData'
import { addDays, formatDate, weekStart } from '../shared/date'
import { useDemoTeam } from '../features/demoTeam'
import { SectionHeader } from '../shared/SectionHeader'
import type { Attendance } from '../entities/types'
import { DemoDataBoundary, useDemoLoad } from '../shared/DemoDataBoundary'

const weekdays = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
const status: Record<Attendance, { label: string; color: 'success' | 'error' | 'default' }> = {
  attended: { label: 'Посещено', color: 'success' },
  missed: { label: 'Пропущено', color: 'error' },
  planned: { label: 'Запланировано', color: 'default' },
}

export function CalendarPage() {
  const { role, athleteId } = useDemoRole()
  const { members } = useDemoTeam()
  const { status: loadStatus, retry, showError } = useDemoLoad(`${role}:${athleteId}`)
  const [offset, setOffset] = useState(0)
  const start = addDays(weekStart(new Date()), offset * 7)
  const end = addDays(start, 6)
  const visible = role === 'trainer'
    ? trainings.filter((item) => members.some((athlete) => athlete.id === item.athleteId))
    : trainings.filter((item) => item.athleteId === athleteId)

  return <>
    <SectionHeader
      title="Календарь"
      subtitle={role === 'trainer' ? 'Недельное расписание команды' : 'Мои тренировки на неделю'}
      action={<Button size="small" onClick={showError}>Показать ошибку загрузки</Button>} />
    <DemoDataBoundary status={loadStatus} onRetry={retry}>
      <Stack direction="row" spacing={1} alignItems="center" justifyContent="space-between"
        sx={{ mb: 2, flexWrap: 'wrap', gap: 1 }}>
        <Button variant="outlined" onClick={() => setOffset((value) => value - 1)}>← Ранее</Button>
        <Typography fontWeight={700} textAlign="center">
          {formatDate(start, { day: 'numeric', month: 'long' })} — {formatDate(end, { day: 'numeric', month: 'long', year: 'numeric' })}
        </Typography>
        <Button variant="outlined" onClick={() => setOffset((value) => value + 1)}>Позже →</Button>
      </Stack>
      {offset !== 0 && <Typography color="text.secondary" sx={{ mb: 2 }}>
        Демонстрационные тренировки доступны для текущей недели.
      </Typography>}
      <Grid container spacing={2}>
        {weekdays.map((name, day) => {
          const dayTrainings = offset === 0 ? visible.filter((item) => item.day === day) : []
          return <Grid item xs={12} sm={6} md={4} key={name}>
            <Card sx={{ height: '100%' }}><CardContent>
              <Typography fontWeight={700}>{name}</Typography>
              <Typography color="text.secondary" sx={{ mb: 2 }}>
                {formatDate(addDays(start, day), { day: 'numeric', month: 'long' })}
              </Typography>
              {dayTrainings.map((item) => <Box key={item.id} sx={{ borderTop: '1px solid #e6ecef', pt: 1.5, pb: 1 }}>
                <Typography fontWeight={700}>{item.time} · {item.title}</Typography>
                {role === 'trainer' && <Typography variant="body2">
                  {members.find((athlete) => athlete.id === item.athleteId)?.name}
                </Typography>}
                <Typography variant="body2" color="text.secondary" sx={{ my: 1 }}>{item.description}</Typography>
                <Chip size="small" label={status[item.attendance].label}
                  color={status[item.attendance].color} variant="outlined" />
              </Box>)}
              {dayTrainings.length === 0 && <Typography variant="body2" color="text.secondary">Тренировок нет</Typography>}
            </CardContent></Card>
          </Grid>
        })}
      </Grid>
    </DemoDataBoundary>
  </>
}
