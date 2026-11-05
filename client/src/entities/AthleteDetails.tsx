import { useState } from 'react'
import { Alert, Button, Chip, Dialog, DialogActions, DialogContent, DialogTitle, Stack } from '@mui/material'
import type { User } from './types'
import { HealthRecords } from '../features/HealthRecords'

export function AthleteDetails({ athlete, onClose, onRemove }: {
  athlete: User | null; onClose: () => void; onRemove: (publicId: string) => Promise<void>
}) {
  const [confirm, setConfirm] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const remove = async () => {
    if (!athlete) return
    setBusy(true); setError('')
    try { await onRemove(athlete.public_id); setConfirm(false) }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Не удалось удалить спортсмена') }
    finally { setBusy(false) }
  }
  return <><Dialog open={Boolean(athlete) && !confirm} onClose={onClose} fullWidth maxWidth="md">
    {athlete && <><DialogTitle>{athlete.name}</DialogTitle><DialogContent>
      <Stack spacing={2}>
        <Stack direction="row" spacing={1}>{athlete.sport && <Chip label={athlete.sport} size="small" />}
          {athlete.age !== null && <Chip label={`${athlete.age} лет`} size="small" variant="outlined" />}</Stack>
        <HealthRecords athletePublicId={athlete.public_id} editable />
      </Stack>
    </DialogContent><DialogActions><Button onClick={onClose}>Закрыть</Button>
      <Button color="error" onClick={() => setConfirm(true)}>Удалить из команды</Button></DialogActions></>}
  </Dialog>
    <Dialog open={Boolean(athlete) && confirm} onClose={() => setConfirm(false)}>
      <DialogTitle>Удалить {athlete?.name} из команды? Аккаунт и история спортсмена сохранятся.</DialogTitle>
      <DialogContent>{error && <Alert severity="error">{error}</Alert>}</DialogContent>
      <DialogActions><Button onClick={() => setConfirm(false)}>Отмена</Button>
        <Button disabled={busy} color="error" variant="contained" onClick={() => void remove()}>Удалить из команды</Button></DialogActions>
    </Dialog>
  </>
}
