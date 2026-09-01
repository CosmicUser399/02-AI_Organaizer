import { ThemeProvider } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import Container from '@mui/material/Container'
import Typography from '@mui/material/Typography'
import Box from '@mui/material/Box'
import theme from './theme'

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="lg">
        <Box sx={{ my: 4 }}>
          <Typography variant="h3" component="h1" gutterBottom>
            AI-Органайзер
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Умный планировщик задач с AI
          </Typography>
        </Box>
      </Container>
    </ThemeProvider>
  )
}

export default App
