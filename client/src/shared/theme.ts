import { createTheme } from '@mui/material/styles'

export const theme = createTheme({
  palette: { mode: 'light', primary: { main: '#315c75' }, background: { default: '#f6f8fa', paper: '#ffffff' }, text: { primary: '#20313c', secondary: '#60717c' } },
  shape: { borderRadius: 12 },
  typography: { fontFamily: 'Inter, system-ui, Arial, sans-serif', h4: { fontWeight: 700 }, h5: { fontWeight: 700 }, h6: { fontWeight: 700 } },
  components: { MuiCard: { styleOverrides: { root: { boxShadow: '0 1px 5px rgba(28,51,65,.07)', border: '1px solid #e6ecef' } } }, MuiButton: { defaultProps: { disableElevation: true }, styleOverrides: { root: { textTransform: 'none', fontWeight: 600 } } } },
})
