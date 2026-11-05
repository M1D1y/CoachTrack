import { Alert, AppBar, Box, Button, Container, CssBaseline, Stack, ThemeProvider, Toolbar, Typography } from '@mui/material'
import { BrowserRouter, Link as RouterLink, NavLink, Navigate, Route, Routes, useNavigate } from 'react-router-dom'
import { AuthProvider, useAuth } from '../features/auth'
import { AthletesPage } from '../pages/AthletesPage'
import { CalendarPage } from '../pages/CalendarPage'
import { ReportsPage } from '../pages/ReportsPage'
import { LoginPage, RegisterPage } from '../pages/AuthPages'
import { RemoteDataBoundary } from '../shared/RemoteDataBoundary'
import { theme } from '../shared/theme'

const navigation = [
  ['/athletes', 'Спортсмены'],
  ['/calendar', 'Календарь'],
  ['/reports', 'Отчёты'],
]

function Layout() {
  const { user, status, error, restore, logout } = useAuth()
  const navigate = useNavigate()
  const leave = async () => {
    let logoutError = ''
    try { await logout() }
    catch { logoutError = 'Локальный выход выполнен, но сервер не подтвердил отзыв сессии.' }
    navigate('/login', { replace: true, state: { logoutError } })
  }

  return <Box sx={{ minHeight: '100vh' }}>
    <AppBar position="static" color="inherit" elevation={0} sx={{ borderBottom: '1px solid #e6ecef' }}>
      <Container maxWidth="lg"><Toolbar disableGutters sx={{ gap: 2, flexWrap: 'wrap', py: 1 }}>
        <Typography variant="h6" component={RouterLink} to="/athletes" sx={{ textDecoration: 'none', color: 'primary.main', mr: 'auto' }}>
          CoachTrack
        </Typography>
        {user && <><Typography variant="body2" color="text.secondary">{user.name}</Typography>
          <Button size="small" onClick={() => void leave()}>Выйти</Button></>}
      </Toolbar></Container>
    </AppBar>
    {user && <Box sx={{ bgcolor: 'white', borderBottom: '1px solid #e6ecef' }}><Container maxWidth="lg">
      <Stack direction="row" spacing={{ xs: 1, sm: 3 }} sx={{ overflowX: 'auto' }}>
        {navigation.map(([path, label]) => <Box key={path} component={NavLink} to={path} sx={{
          textDecoration: 'none', color: 'text.secondary', py: 1.5, px: 1,
          whiteSpace: 'nowrap', borderBottom: '3px solid transparent',
          '&.active': { color: 'primary.main', borderColor: 'primary.main', fontWeight: 700 },
        }}>{label}</Box>)}
      </Stack>
    </Container></Box>}
    <Container component="main" maxWidth="lg" sx={{ py: { xs: 3, sm: 5 } }}>
      {status === 'loading' || status === 'error' ? <RemoteDataBoundary loading={status === 'loading'} error={error} retry={() => void restore()}>
        <Alert>Проверка сессии</Alert>
      </RemoteDataBoundary> : <Routes>
        <Route path="/login" element={user ? <Navigate to="/athletes" replace /> : <LoginPage />} />
        <Route path="/register" element={user ? <Navigate to="/athletes" replace /> : <RegisterPage />} />
        <Route path="/athletes" element={user ? <AthletesPage key={user.public_id} /> : <Navigate to="/login" replace />} />
        <Route path="/calendar" element={user ? <CalendarPage key={user.public_id} /> : <Navigate to="/login" replace />} />
        <Route path="/reports" element={user ? <ReportsPage key={user.public_id} /> : <Navigate to="/login" replace />} />
        <Route path="*" element={<Navigate to={user ? '/athletes' : '/login'} replace />} />
      </Routes>}
    </Container>
  </Box>
}

export function App() {
  return <ThemeProvider theme={theme}><CssBaseline /><BrowserRouter>
    <AuthProvider><Layout /></AuthProvider>
  </BrowserRouter></ThemeProvider>
}
