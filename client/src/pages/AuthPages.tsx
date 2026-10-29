import {
  Alert, Box, Button, Card, CardContent, Container, FormControl, FormHelperText,
  InputLabel, Link, MenuItem, Select, Stack, TextField, Typography,
} from '@mui/material'
import { useState, type FormEvent, type ReactNode } from 'react'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import type { Role } from '../entities/types'
import { useDemoRole } from '../features/demoRole'
import { useDemoTeam } from '../features/demoTeam'
import { initialAthleteId, trainer } from '../shared/demoData'
import { normalizeFullName, validNamePart } from '../shared/search'

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
  const [name, setName] = useState('')
  const [password, setPassword] = useState('')
  const [attempted, setAttempted] = useState(false)
  const [accountError, setAccountError] = useState('')

  const nameParts = normalizeFullName(name).split(' ')
  const validName = nameParts.length === 3 && nameParts.every(validNamePart)
  const nameError = attempted && !validName ? 'Введите фамилию, имя и отчество.' : ''
  const passwordError = attempted && !password.trim() ? 'Введите пароль.' : ''

  const submit = (event: FormEvent) => {
    event.preventDefault()
    setAttempted(true)
    setAccountError('')
    if (!validName || !password.trim()) return

    const key = normalizeFullName(name)
    if (key === normalizeFullName(trainer.name)) {
      setRole('trainer')
    } else {
      const athlete = athletes.find((item) => normalizeFullName(item.name) === key)
      if (!athlete) {
        setAccountError('Такого демонстрационного пользователя нет. Выберите ФИО из списка профилей.')
        return
      }
      setAthleteId(athlete.id)
      setRole('athlete')
    }
    navigate('/athletes')
  }

  return <AuthShell title="Вход"><Box component="form" onSubmit={submit} noValidate><Stack spacing={2}>
    <TextField label="ФИО пользователя" autoComplete="name" value={name}
      onChange={(event) => { setName(event.target.value); setAccountError('') }}
      error={Boolean(nameError || accountError)} helperText={nameError || accountError} fullWidth />
    <TextField label="Пароль" type="password" autoComplete="current-password" value={password}
      onChange={(event) => setPassword(event.target.value)} error={Boolean(passwordError)} helperText={passwordError} fullWidth />
    <Typography variant="body2" color="text.secondary">
      Для демо-входа используйте, например, «Смирнов Алексей Сергеевич» или «Соколова Мария Андреевна».
      Пароль здесь не проверяется.
    </Typography>
    <Button type="submit" variant="contained">Войти в демо-режим</Button>
    <Typography textAlign="center">Нет аккаунта? <Link component={RouterLink} to="/register">Регистрация</Link></Typography>
  </Stack></Box></AuthShell>
}

export function RegisterPage() {
  const { setRole, setAthleteId } = useDemoRole()
  const navigate = useNavigate()
  const [lastName, setLastName] = useState('')
  const [firstName, setFirstName] = useState('')
  const [patronymic, setPatronymic] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [role, chooseRole] = useState<Role>('athlete')
  const [attempted, setAttempted] = useState(false)

  const partError = (value: string, label: string) => attempted && !validNamePart(value)
    ? (value.trim() ? 'Используйте буквы и дефис, не более 60 символов.' : `Введите ${label}.`)
    : ''
  const lastNameError = partError(lastName, 'фамилию')
  const firstNameError = partError(firstName, 'имя')
  const patronymicError = partError(patronymic, 'отчество')
  const passwordError = attempted && password.length < 8 ? 'Пароль должен содержать минимум 8 символов.' : ''
  const confirmError = attempted && !confirm
    ? 'Подтвердите пароль.'
    : attempted && confirm !== password ? 'Пароли не совпадают.' : ''
  const roleError = attempted && !validRole(role) ? 'Выберите допустимую роль.' : ''

  const submit = (event: FormEvent) => {
    event.preventDefault()
    setAttempted(true)
    if (![lastName, firstName, patronymic].every(validNamePart) || password.length < 8 ||
      !confirm || password !== confirm || !validRole(role)) return

    if (role === 'athlete') setAthleteId(initialAthleteId)
    setRole(role)
    navigate('/athletes')
  }

  return <AuthShell title="Регистрация"><Box component="form" onSubmit={submit} noValidate><Stack spacing={2}>
    <TextField label="Фамилия" autoComplete="family-name" value={lastName}
      onChange={(event) => setLastName(event.target.value)} error={Boolean(lastNameError)} helperText={lastNameError} fullWidth />
    <TextField label="Имя" autoComplete="given-name" value={firstName}
      onChange={(event) => setFirstName(event.target.value)} error={Boolean(firstNameError)} helperText={firstNameError} fullWidth />
    <TextField label="Отчество" autoComplete="additional-name" value={patronymic}
      onChange={(event) => setPatronymic(event.target.value)} error={Boolean(patronymicError)} helperText={patronymicError} fullWidth />
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
