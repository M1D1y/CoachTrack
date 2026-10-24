import { Alert, Box, Button, CircularProgress, Fade, Stack, Typography } from '@mui/material'
import { useEffect, useState, type ReactNode } from 'react'

export type DemoLoadStatus = 'loading' | 'error' | 'ready'

function loadDemoData(shouldFail: boolean): Promise<void> {
  return new Promise((resolve, reject) => {
    window.setTimeout(() => {
      if (shouldFail) reject(new Error('Demo loading error'))
      else resolve()
    }, 450)
  })
}

export function useDemoLoad(scope: string) {
  const [status, setStatus] = useState<DemoLoadStatus>('loading')
  const [request, setRequest] = useState({ number: 0, fail: false })

  useEffect(() => {
    let active = true
    setStatus('loading')
    loadDemoData(request.fail).then(
      () => { if (active) setStatus('ready') },
      () => { if (active) setStatus('error') },
    )
    return () => { active = false }
  }, [scope, request])

  const retry = () => setRequest((value) => ({ number: value.number + 1, fail: false }))
  const showError = () => setRequest((value) => ({ number: value.number + 1, fail: true }))
  return { status, retry, showError }
}

export function DemoDataBoundary({ status, onRetry, children }: {
  status: DemoLoadStatus
  onRetry: () => void
  children: ReactNode
}) {
  if (status === 'loading') {
    return <Stack alignItems="center" spacing={1.5} sx={{ py: 5 }} role="status">
      <CircularProgress size={32} />
      <Typography color="text.secondary">Загрузка демонстрационных данных…</Typography>
    </Stack>
  }
  if (status === 'error') {
    return <Alert severity="error" action={<Button color="inherit" onClick={onRetry}>Повторить</Button>}>
      Не удалось загрузить данные.
    </Alert>
  }
  return <Fade in timeout={300}><Box>{children}</Box></Fade>
}
