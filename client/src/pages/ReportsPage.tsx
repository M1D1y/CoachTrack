import { Button, Card, CardContent, Grid, Typography } from '@mui/material'
import { useDemoRole } from '../features/demoRole'
import { trainings } from '../shared/demoData'
import { useDemoTeam } from '../features/demoTeam'
import { SectionHeader } from '../shared/SectionHeader'
import { DemoDataBoundary, useDemoLoad } from '../shared/DemoDataBoundary'

export function ReportsPage() {
  const { role, athleteId } = useDemoRole()
  const { members } = useDemoTeam()
  const { status, retry, showError } = useDemoLoad(`${role}:${athleteId}`)
  const items = role === 'trainer'
    ? trainings.filter((item) => members.some((athlete) => athlete.id === item.athleteId))
    : trainings.filter((item) => item.athleteId === athleteId)
  const attended = items.filter((item) => item.attendance === 'attended').length
  const missed = items.filter((item) => item.attendance === 'missed').length
  const completed = attended + missed
  const percent = completed ? Math.round(attended / completed * 100) : 0
  const stats = role === 'trainer' ? [
    ['Спортсменов', members.length],
    ['Тренировок', items.length],
    ['Посещаемость', `${percent}%`],
    ['Пропусков', missed],
  ] : [
    ['Назначено тренировок', items.length],
    ['Посещено', attended],
    ['Пропущено', missed],
    ['Посещаемость', `${percent}%`],
  ]
  return <>
    <SectionHeader title="Отчёты"
      subtitle={role === 'trainer' ? 'Показатели команды за демонстрационную неделю' : 'Мои показатели за демонстрационную неделю'}
      action={<Button size="small" onClick={showError}>Показать ошибку загрузки</Button>} />
    <DemoDataBoundary status={status} onRetry={retry}>
      <Grid container spacing={2}>{stats.map(([label, value]) => <Grid item xs={12} sm={6} md={3} key={label}>
        <Card><CardContent sx={{ py: 3 }}>
          <Typography color="text.secondary" gutterBottom>{label}</Typography>
          <Typography variant="h4">{value}</Typography>
        </CardContent></Card>
      </Grid>)}</Grid>
      {items.length === 0 && <Typography color="text.secondary" sx={{ mt: 3 }}>
        Тренировок за демонстрационную неделю нет.
      </Typography>}
      <Typography color="text.secondary" sx={{ mt: 3 }}>
        Посещаемость рассчитана по завершённым тренировкам: посещённые / (посещённые + пропущенные).
        Запланированные тренировки в процент не входят.
      </Typography>
    </DemoDataBoundary>
  </>
}
