import {
  Alert, Box, Button, Card, CardContent, Container, FormControl, FormHelperText,
  InputLabel, Link, MenuItem, Select, Stack, TextField, Typography,
} from '@mui/material'
import { useState, type FormEvent, type ReactNode } from 'react'
import { Link as RouterLink, useLocation, useNavigate } from 'react-router-dom'
import type { Role } from '../entities/types'
import { useAuth } from '../features/auth'
import { normalizeFullName, validNamePart } from '../shared/search'

function AuthShell({ title, children }: { title: string; children: ReactNode }) {
  return <Container maxWidth="sm" sx={{ py: { xs: 4, sm: 8 } }}><Card><CardContent sx={{ p: { xs: 3, sm: 5 } }}>
    <Typography variant="h5" component="h1" gutterBottom>{title}</Typography>{children}
  </CardContent></Card></Container>
}

export function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const logoutError = (location.state as { logoutError?: string } | null)?.logoutError
  const [name, setName] = useState('')
  const [password, setPassword] = useState('')
  const [attempted, setAttempted] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const validName = normalizeFullName(name).split(' ').length >= 2
  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setAttempted(true)
    setError('')
    if (!validName || !password) return
    setBusy(true)
    try { await login(name, password); navigate('/athletes', { replace: true }) }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Не удалось войти') }
    finally { setBusy(false) }
  }
  return <AuthShell title="Вход"><Box component="form" onSubmit={(event) => void submit(event)} noValidate><Stack spacing={2}>
    {logoutError && <Alert severity="warning">{logoutError}</Alert>}
    {error && <Alert severity="error">{error}</Alert>}
    <TextField label="ФИО пользователя" autoComplete="name" value={name} onChange={(event) => setName(event.target.value)}
      error={attempted && !validName} helperText={attempted && !validName ? 'Введите полное имя.' : ''} fullWidth />
    <TextField label="Пароль" type="password" autoComplete="current-password" value={password}
      onChange={(event) => setPassword(event.target.value)} error={attempted && !password}
      helperText={attempted && !password ? 'Введите пароль.' : ''} fullWidth />
    <Button type="submit" variant="contained" disabled={busy}>{busy ? 'Вход…' : 'Войти'}</Button>
    <Typography textAlign="center">Нет аккаунта? <Link component={RouterLink} to="/register">Регистрация</Link></Typography>
  </Stack></Box></AuthShell>
}

export function RegisterPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [lastName, setLastName] = useState('')
  const [firstName, setFirstName] = useState('')
  const [patronymic, setPatronymic] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [role, setRole] = useState<Role>('athlete')
  const [attempted, setAttempted] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const partError = (value: string, label: string) => attempted && !validNamePart(value)
    ? (value.trim() ? 'Используйте буквы и дефис, не более 60 символов.' : `Введите ${label}.`) : ''
  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setAttempted(true)
    setError('')
    if (![lastName, firstName, patronymic].every(validNamePart) || password.length < 8 || password.length > 128 || password !== confirm) return
    setBusy(true)
    try {
      await register({ last_name: lastName.trim(), first_name: firstName.trim(), patronymic: patronymic.trim(), password, role })
      navigate('/athletes', { replace: true })
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Не удалось зарегистрироваться') }
    finally { setBusy(false) }
  }
  return <AuthShell title="Регистрация"><Box component="form" onSubmit={(event) => void submit(event)} noValidate><Stack spacing={2}>
    {error && <Alert severity="error">{error}</Alert>}
    <TextField label="Фамилия" autoComplete="family-name" value={lastName} onChange={(event) => setLastName(event.target.value)}
      error={Boolean(partError(lastName, 'фамилию'))} helperText={partError(lastName, 'фамилию')} fullWidth />
    <TextField label="Имя" autoComplete="given-name" value={firstName} onChange={(event) => setFirstName(event.target.value)}
      error={Boolean(partError(firstName, 'имя'))} helperText={partError(firstName, 'имя')} fullWidth />
    <TextField label="Отчество" autoComplete="additional-name" value={patronymic} onChange={(event) => setPatronymic(event.target.value)}
      error={Boolean(partError(patronymic, 'отчество'))} helperText={partError(patronymic, 'отчество')} fullWidth />
    <TextField label="Пароль" type="password" autoComplete="new-password" value={password} onChange={(event) => setPassword(event.target.value)}
      error={attempted && (password.length < 8 || password.length > 128)} helperText={attempted && (password.length < 8 || password.length > 128) ? 'Пароль: от 8 до 128 символов.' : ''} fullWidth />
    <TextField label="Подтверждение пароля" type="password" autoComplete="new-password" value={confirm} onChange={(event) => setConfirm(event.target.value)}
      error={attempted && (!confirm || confirm !== password)} helperText={attempted && (!confirm || confirm !== password) ? 'Пароли не совпадают.' : ''} fullWidth />
    <FormControl fullWidth><InputLabel id="register-role">Роль</InputLabel>
      <Select labelId="register-role" value={role} label="Роль" onChange={(event) => setRole(event.target.value as Role)}>
        <MenuItem value="trainer">Тренер</MenuItem><MenuItem value="athlete">Спортсмен</MenuItem>
      </Select><FormHelperText>Роль определяется при регистрации.</FormHelperText>
    </FormControl>
    <Button type="submit" variant="contained" disabled={busy}>{busy ? 'Регистрация…' : 'Зарегистрироваться'}</Button>
    <Typography textAlign="center">Уже есть аккаунт? <Link component={RouterLink} to="/login">Вход</Link></Typography>
  </Stack></Box></AuthShell>
}
