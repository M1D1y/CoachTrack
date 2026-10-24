import { Alert, Box, Button, Card, CardContent, Fade, Stack, Typography } from '@mui/material'
import { useState } from 'react'
import { trainer } from '../shared/demoData'
import { useDemoRole } from './demoRole'
import { useDemoTeam } from './demoTeam'

export function IncomingInvitations() {
  const { athleteId } = useDemoRole()
  const { invitations, respond } = useDemoTeam()
  const [message, setMessage] = useState('')
  const [error, setError] = useState(false)
  const incoming = invitations.filter((item) => item.athleteId === athleteId && item.status === 'pending')

  const decide = (id: number, accepted: boolean) => {
    const result = respond(id, athleteId, accepted)
    setMessage(result.message)
    setError(!result.ok)
  }

  return <Card><CardContent>
    <Typography variant="h6" gutterBottom>Входящие приглашения</Typography>
    {incoming.length ? incoming.map((item) => <Box key={item.id} sx={{ py: 1 }}>
      <Typography fontWeight={600}>{trainer.name}</Typography>
      <Stack direction="row" spacing={1}>
        <Button size="small" variant="contained" onClick={() => decide(item.id, true)}>Принять</Button>
        <Button size="small" onClick={() => decide(item.id, false)}>Отклонить</Button>
      </Stack>
    </Box>) : <Typography color="text.secondary">Новых приглашений нет</Typography>}
    {message && <Fade in><Alert severity={error ? 'error' : 'success'} sx={{ mt: 2 }}>{message}</Alert></Fade>}
  </CardContent></Card>
}
