import { Alert, Box, Button, CircularProgress, Fade, Stack, Typography } from '@mui/material'
import type { ReactNode } from 'react'

export function RemoteDataBoundary({ loading, error, retry, children }: {
  loading: boolean; error: string; retry: () => void; children: ReactNode
}) {
  if (loading) return <Stack role="status" alignItems="center" spacing={1} sx={{ py: 5 }}>
    <CircularProgress size={32} /><Typography color="text.secondary">Загрузка данных…</Typography>
  </Stack>
  if (error) return <Alert severity="error" action={<Button onClick={retry} color="inherit">Повторить</Button>}>{error}</Alert>
  return <Fade in><Box>{children}</Box></Fade>
}
