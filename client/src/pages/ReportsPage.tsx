import { useState } from 'react'
import { Button, Card, CardContent, Grid, Stack, Typography } from '@mui/material'
import type { Summary } from '../entities/types'
import { useAuth } from '../features/auth'
import { api } from '../shared/api/client'
import { useResource } from '../shared/api/useResource'
import { RemoteDataBoundary } from '../shared/RemoteDataBoundary'
import { addDays, formatDate, isoLocalDate, weekStart } from '../shared/date'
import { SectionHeader } from '../shared/SectionHeader'

export function ReportsPage() {
  const { user } = useAuth()
  const [offset, setOffset] = useState(0)
  const start = addDays(weekStart(new Date()), offset * 7)
  const week = isoLocalDate(start)
  const resource = useResource(`${user?.public_id}:${week}`, (signal) =>
    api<Summary>(`/reports/summary?week_start=${week}`, { signal }))
  const summary = resource.data
  const stats: [string, number | string][] = user?.role === 'trainer' ? [
    ['Спортсменов', summary?.athlete_count ?? 0],
    ['Тренировок', summary?.training_count ?? 0],
    ['Посещено', summary?.attended ?? 0],
    ['Пропущено', summary?.missed ?? 0],
    ['Посещаемость', `${summary?.attendance_percent ?? 0}%`],
  ] : [
    ['Назначено тренировок', summary?.training_count ?? 0],
    ['Посещено', summary?.attended ?? 0],
    ['Пропущено', summary?.missed ?? 0],
    ['Посещаемость', `${summary?.attendance_percent ?? 0}%`],
  ]
  return <>
    <SectionHeader title="Отчёты" subtitle={user?.role === 'trainer' ? 'Показатели команды за неделю' : 'Мои показатели за неделю'} />
    <Stack direction="row" spacing={1} alignItems="center" justifyContent="space-between" sx={{ mb: 2, flexWrap: 'wrap', gap: 1 }}>
      <Button variant="outlined" onClick={() => setOffset((value) => value - 1)}>← Ранее</Button>
      <Typography fontWeight={700}>{formatDate(start, { day: 'numeric', month: 'long' })} — {formatDate(addDays(start, 6), { day: 'numeric', month: 'long', year: 'numeric' })}</Typography>
      <Button variant="outlined" onClick={() => setOffset((value) => value + 1)}>Позже →</Button>
    </Stack>
    <RemoteDataBoundary loading={resource.loading} error={resource.error} retry={resource.refresh}>
      <Grid container spacing={2}>{stats.map(([label, value]) => <Grid item xs={12} sm={6} md={3} key={label}>
        <Card><CardContent sx={{ py: 3 }}><Typography color="text.secondary" gutterBottom>{label}</Typography>
          <Typography variant="h4">{value}</Typography></CardContent></Card>
      </Grid>)}</Grid>
      {summary?.training_count === 0 && <Typography color="text.secondary" sx={{ mt: 3 }}>Тренировок на эту неделю нет.</Typography>}
      <Typography color="text.secondary" sx={{ mt: 3 }}>
        Посещаемость рассчитана по завершённым тренировкам: посещённые / (посещённые + пропущенные).
        Запланированные тренировки в процент не входят.
      </Typography>
    </RemoteDataBoundary>
  </>
}
