import { Alert, Box, Button, Card, CardContent, Stack, Typography } from '@mui/material'
import { useState } from 'react'
import type { Invitation } from '../entities/types'
import { api } from '../shared/api/client'

export function IncomingInvitations({ items, onChanged }: { items: Invitation[]; onChanged: () => void }) {
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const decide = async (id: number, action: 'accept' | 'reject') => {
    setBusy(true); setError('')
    try { await api(`/invitations/${id}/${action}`, { method: 'POST' }); onChanged() }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Не удалось ответить') }
    finally { setBusy(false) }
  }
  const pending = items.filter((item) => item.status === 'pending')
  return <Card><CardContent><Typography variant="h6" gutterBottom>Входящие приглашения</Typography>
    {error && <Alert severity="error">{error}</Alert>}
    {pending.length === 0 && <Typography color="text.secondary">Приглашений нет</Typography>}
    <Stack spacing={1}>{pending.map((item) => <Box key={item.id}>
      <Typography fontWeight={600}>{item.trainer_name}</Typography>
      <Stack direction="row" spacing={1}>
        <Button disabled={busy} variant="contained" onClick={() => void decide(item.id, 'accept')}>Принять</Button>
        <Button disabled={busy} onClick={() => void decide(item.id, 'reject')}>Отклонить</Button>
      </Stack>
    </Box>)}</Stack>
  </CardContent></Card>
}
