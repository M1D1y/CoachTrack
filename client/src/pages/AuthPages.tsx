import {
  Alert, Box, Button, Card, CardContent, Container, FormControl, FormHelperText,
  InputLabel, Link, MenuItem, Select, Stack, TextField, Typography,
} from '@mui/material'
import { useState, type FormEvent, type ReactNode } from 'react'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import type { Role } from '../entities/types'
import { useDemoRole } from '../features/demoRole'
import { useDemoTeam } from '../features/demoTeam'

function AuthShell({ title, children }: { title: string; children: ReactNode }) {
  return <Container maxWidth="sm" sx={{ py: { xs: 4, sm: 8 } }}>
    <Card><CardContent sx={{ p: { xs: 3, sm: 5 } }}>
      <Typography variant="h5" component="h1" gutterBottom>{title}</Typography>
      <Alert severity="info" sx={{ mb: 3 }}>
        Демонстрационный режим: учётные записи не создаются, пароль не проверяется и нигде не сохраняется.
      </Alert>
      {children}
    </CardContent></Card>
  </Container>
}

function validRole(role: string): role is Role {
  return role === 'trainer' || role === 'athlete'
}

export function LoginPage() {
  const { setRole, setAthleteId } = useDemoRole()
  const { athletes } = useDemoTeam()
  const navigate = useNavigate()
  const [id, setId] = useState('')
  const [password, setPassword] = useState('')
  const [role, chooseRole] = useState<Role>('trainer')
  const [attempted, setAttempted] = useState(false)

  const validId = /^\d+$/.test(id.trim()) && Number.isSafeInteger(Number(id.trim())) && Number(id.trim()) > 0
  const idError = attempted && !validId ? 'Введите положительный целый ID.' : ''
  const passwordError = attempted && !password.trim() ? 'Введите пароль.' : ''
  const roleError = attempted && !validRole(role) ? 'Выберите допустимую роль.' : ''

  const submit = (event: FormEvent) => {
    event.preventDefault()
    setAttempted(true)
    if (!validId || !password.trim() || !validRole(role)) return

    if (role === 'athlete' && athletes.some((athlete) => athlete.id === Number(id))) {
      setAthleteId(Number(id))
    }
    setRole(role)
    navigate('/athletes')
  }

  return <AuthShell title="Вход"><Box component="form" onSubmit={submit} noValidate><Stack spacing={2}>
    <TextField label="ID пользователя" inputMode="numeric" value={id} onChange={(event) => setId(event.target.value)}
      error={Boolean(idError)} helperText={idError} fullWidth />
    <TextField label="Пароль" type="password" autoComplete="current-password" value={password}
      onChange={(event) => setPassword(event.target.value)} error={Boolean(passwordError)} helperText={passwordError} fullWidth />
    <FormControl fullWidth error={Boolean(roleError)}>
      <InputLabel id="login-role">Демонстрационная роль</InputLabel>
      <Select labelId="login-role" value={role} label="Демонстрационная роль"
        onChange={(event) => { if (validRole(event.target.value)) chooseRole(event.target.value) }}>
        <MenuItem value="trainer">Тренер</MenuItem>
        <MenuItem value="athlete">Спортсмен</MenuItem>
      </Select>
      {roleError && <FormHelperText>{roleError}</FormHelperText>}
    </FormControl>
    <Button type="submit" variant="contained">Войти в демо-режим</Button>
    <Typography textAlign="center">Нет аккаунта? <Link component={RouterLink} to="/register">Регистрация</Link></Typography>
  </Stack></Box></AuthShell>
}

export function RegisterPage() {
  const { setRole } = useDemoRole()
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [role, chooseRole] = useState<Role>('athlete')
  const [attempted, setAttempted] = useState(false)

  const nameError = attempted && !name.trim() ? 'Введите имя.' : ''
  const passwordError = attempted && password.length < 8 ? 'Пароль должен содержать минимум 8 символов.' : ''
  const confirmError = attempted && !confirm
    ? 'Подтвердите пароль.'
    : attempted && confirm !== password ? 'Пароли не совпадают.' : ''
  const roleError = attempted && !validRole(role) ? 'Выберите допустимую роль.' : ''

  const submit = (event: FormEvent) => {
    event.preventDefault()
    setAttempted(true)
    if (!name.trim() || password.length < 8 || !confirm || password !== confirm || !validRole(role)) return

    setRole(role)
    navigate('/athletes')
  }

  return <AuthShell title="Регистрация"><Box component="form" onSubmit={submit} noValidate><Stack spacing={2}>
    <TextField label="Имя" autoComplete="name" value={name} onChange={(event) => setName(event.target.value)}
      error={Boolean(nameError)} helperText={nameError} fullWidth />
    <TextField label="Пароль" type="password" autoComplete="new-password" value={password}
      onChange={(event) => setPassword(event.target.value)} error={Boolean(passwordError)} helperText={passwordError} fullWidth />
    <TextField label="Подтверждение пароля" type="password" autoComplete="new-password" value={confirm}
      onChange={(event) => setConfirm(event.target.value)} error={Boolean(confirmError)} helperText={confirmError} fullWidth />
    <FormControl fullWidth error={Boolean(roleError)}>
      <InputLabel id="register-role">Роль</InputLabel>
      <Select labelId="register-role" value={role} label="Роль"
        onChange={(event) => { if (validRole(event.target.value)) chooseRole(event.target.value) }}>
        <MenuItem value="trainer">Тренер</MenuItem>
        <MenuItem value="athlete">Спортсмен</MenuItem>
      </Select>
      {roleError && <FormHelperText>{roleError}</FormHelperText>}
    </FormControl>
    <Button type="submit" variant="contained">Продолжить в демо-режиме</Button>
    <Typography textAlign="center">Уже есть аккаунт? <Link component={RouterLink} to="/login">Вход</Link></Typography>
  </Stack></Box></AuthShell>
}
