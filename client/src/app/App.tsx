import {
  AppBar, Box, Button, Container, CssBaseline, FormControl, MenuItem,
  Select, Stack, ThemeProvider, Toolbar, Typography,
} from '@mui/material'
import { BrowserRouter, Link as RouterLink, NavLink, Navigate, Route, Routes } from 'react-router-dom'
import type { Role } from '../entities/types'
import { DemoRoleProvider, useDemoRole } from '../features/demoRole'
import { DemoTeamProvider, useDemoTeam } from '../features/demoTeam'
import { AthletesPage } from '../pages/AthletesPage'
import { CalendarPage } from '../pages/CalendarPage'
import { ReportsPage } from '../pages/ReportsPage'
import { LoginPage, RegisterPage } from '../pages/AuthPages'
import { trainer } from '../shared/demoData'
import { theme } from '../shared/theme'

const navigation = [
  ['/athletes', 'Спортсмены'],
  ['/calendar', 'Календарь'],
  ['/reports', 'Отчёты'],
]

function Layout() {
  const { role, setRole, athleteId, setAthleteId } = useDemoRole()
  const { athletes } = useDemoTeam()

  return <Box sx={{ minHeight: '100vh' }}>
    <AppBar position="static" color="inherit" elevation={0} sx={{ borderBottom: '1px solid #e6ecef' }}>
      <Container maxWidth="lg">
        <Toolbar disableGutters sx={{ gap: 2, flexWrap: 'wrap', py: 1 }}>
          <Typography variant="h6" component={RouterLink} to="/athletes"
            sx={{ textDecoration: 'none', color: 'primary.main', mr: 'auto' }}>
            CoachTrack
          </Typography>
          <FormControl size="small">
            <Select aria-label="Демонстрационная роль" value={role}
              onChange={(event) => setRole(event.target.value as Role)} sx={{ minWidth: 130 }}>
              <MenuItem value="trainer">Тренер</MenuItem>
              <MenuItem value="athlete">Спортсмен</MenuItem>
            </Select>
          </FormControl>
          {role === 'trainer' && <Typography variant="body2" color="text.secondary">
            {trainer.name}
          </Typography>}
          {role === 'athlete' && <FormControl size="small">
            <Select aria-label="Демонстрационный спортсмен" value={athleteId}
              onChange={(event) => setAthleteId(Number(event.target.value))} sx={{ minWidth: 170 }}>
              {athletes.map((athlete) => <MenuItem key={athlete.id} value={athlete.id}>
                {athlete.name} · ID {athlete.id}
              </MenuItem>)}
            </Select>
          </FormControl>}
          <Button component={RouterLink} to="/login" size="small">Вход</Button>
        </Toolbar>
      </Container>
    </AppBar>
    <Box sx={{ bgcolor: 'white', borderBottom: '1px solid #e6ecef' }}>
      <Container maxWidth="lg">
        <Stack direction="row" spacing={{ xs: 1, sm: 3 }} sx={{ overflowX: 'auto' }}>
          {navigation.map(([path, label]) => <Box key={path} component={NavLink} to={path} sx={{
            textDecoration: 'none', color: 'text.secondary', py: 1.5, px: 1,
            whiteSpace: 'nowrap', borderBottom: '3px solid transparent',
            '&.active': { color: 'primary.main', borderColor: 'primary.main', fontWeight: 700 },
          }}>{label}</Box>)}
        </Stack>
      </Container>
    </Box>
    <Container component="main" maxWidth="lg" sx={{ py: { xs: 3, sm: 5 } }}>
      <Routes>
        <Route path="/" element={<Navigate to="/athletes" replace />} />
        <Route path="/athletes" element={<AthletesPage />} />
        <Route path="/calendar" element={<CalendarPage />} />
        <Route path="/reports" element={<ReportsPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="*" element={<Navigate to="/athletes" replace />} />
      </Routes>
    </Container>
  </Box>
}

export function App() {
  return <ThemeProvider theme={theme}>
    <CssBaseline />
    <BrowserRouter>
      <DemoRoleProvider>
        <DemoTeamProvider>
          <Layout />
        </DemoTeamProvider>
      </DemoRoleProvider>
    </BrowserRouter>
  </ThemeProvider>
}
