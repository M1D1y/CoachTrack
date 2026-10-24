import { Box, Typography } from '@mui/material'
import type { ReactNode } from 'react'

export function SectionHeader({ title, subtitle, action }: { title: string; subtitle: string; action?: ReactNode }) {
  return <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: { xs: 'flex-start', sm: 'center' }, gap: 2, flexWrap: 'wrap', mb: 3 }}>
    <Box><Typography variant="h4" component="h1" sx={{ fontSize: { xs: 28, sm: 34 } }}>{title}</Typography><Typography color="text.secondary">{subtitle}</Typography></Box>
    {action}
  </Box>
}
