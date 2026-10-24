import { useEffect, useState } from 'react'
import { Box, Button, Chip, Dialog, DialogActions, DialogContent, DialogTitle, Divider, Stack, Typography } from '@mui/material'
import type { Athlete } from './types'

export function AthleteDetails({ athlete, onClose, onRemove }: { athlete: Athlete | null; onClose: () => void; onRemove: (id: number) => void }) {
  const [confirm, setConfirm] = useState(false)
  useEffect(() => {
    if (!athlete) setConfirm(false)
  }, [athlete])
  return <>
    <Dialog open={Boolean(athlete) && !confirm} onClose={onClose} fullWidth maxWidth="sm" aria-labelledby="athlete-dialog-title">
      {athlete && <><DialogTitle id="athlete-dialog-title">{athlete.name}</DialogTitle><DialogContent>
        <Stack spacing={2}>
          <Typography color="text.secondary">ID {athlete.id}</Typography>
          <Stack direction="row" spacing={1}><Chip label={athlete.sport} size="small" /><Chip label={`${athlete.age} лет`} size="small" variant="outlined" /></Stack>
          <Divider />
          <Box><Typography variant="h6" gutterBottom>Травмы</Typography>{athlete.injuries.length ? athlete.injuries.map((item) => <Box key={item.title} mb={1}><Typography fontWeight={600}>{item.title} · {item.date}</Typography><Typography color="text.secondary">{item.note}</Typography></Box>) : <Typography color="text.secondary">Записей нет</Typography>}</Box>
          <Divider />
          <Box><Typography variant="h6" gutterBottom>Питание</Typography>{athlete.nutrition.length ? athlete.nutrition.map((item) => <Box key={item.title}><Typography fontWeight={600}>{item.title} · {item.date}</Typography><Typography color="text.secondary">{item.note}</Typography></Box>) : <Typography color="text.secondary">Записей нет</Typography>}</Box>
        </Stack>
      </DialogContent><DialogActions><Button color="error" onClick={() => setConfirm(true)}>Удалить из команды</Button></DialogActions></>}
    </Dialog>
    <Dialog open={Boolean(athlete) && confirm} onClose={() => setConfirm(false)}>
      <DialogTitle>Удалить {athlete?.name} из команды? Аккаунт и история спортсмена сохранятся</DialogTitle>
      <DialogActions><Button onClick={() => setConfirm(false)}>Отмена</Button><Button color="error" variant="contained" onClick={() => { if (athlete) onRemove(athlete.id); setConfirm(false) }}>Удалить из команды</Button></DialogActions>
    </Dialog>
  </>
}
