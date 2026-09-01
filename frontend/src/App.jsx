import { useState, useEffect } from 'react'
import { ThemeProvider } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import Container from '@mui/material/Container'
import Typography from '@mui/material/Typography'
import Box from '@mui/material/Box'
import Alert from '@mui/material/Alert'
import CircularProgress from '@mui/material/CircularProgress'
import theme from './theme'
import api from './api/client'
import MagicInput from './components/MagicInput'
import TaskList from './components/TaskList'

function App() {
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    loadTasks()
  }, [])

  const loadTasks = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await api.get('/tasks/')
      setTasks(data)
    } catch (err) {
      setError(err.message || 'Не удалось загрузить задачи')
    } finally {
      setLoading(false)
    }
  }

  const handleAddTask = async (input) => {
    try {
      setSubmitting(true)
      setError(null)
      const newTask = await api.post('/tasks/', {
        title: input,
        raw_input: input,
      })
      setTasks([newTask, ...tasks])
    } catch (err) {
      setError(err.message || 'Не удалось добавить задачу')
    } finally {
      setSubmitting(false)
    }
  }

  const handleToggleTask = async (taskId) => {
    const task = tasks.find((t) => t.id === taskId)
    if (!task) return

    const newStatus = task.status === 'done' ? 'pending' : 'done'

    try {
      setError(null)
      const updated = await api.patch(`/tasks/${taskId}`, {
        status: newStatus,
      })
      setTasks(tasks.map((t) => (t.id === taskId ? updated : t)))
    } catch (err) {
      setError(err.message || 'Не удалось обновить задачу')
    }
  }

  const handleDeleteTask = async (taskId) => {
    try {
      setError(null)
      await api.delete(`/tasks/${taskId}`)
      setTasks(tasks.filter((t) => t.id !== taskId))
    } catch (err) {
      setError(err.message || 'Не удалось удалить задачу')
    }
  }

  const handleClearAll = async () => {
    if (!window.confirm('Удалить все задачи?')) return

    try {
      setError(null)
      await api.delete('/tasks/')
      setTasks([])
    } catch (err) {
      setError(err.message || 'Не удалось очистить список')
    }
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="lg">
        <Box sx={{ my: 4 }}>
          <Typography variant="h3" component="h1" gutterBottom>
            AI-Органайзер
          </Typography>
          <Typography
            variant="body1"
            color="text.secondary"
            gutterBottom
            sx={{ mb: 3 }}
          >
            Умный планировщик задач с AI
          </Typography>

          {error && (
            <Alert
              severity="error"
              sx={{ mb: 2 }}
              onClose={() => setError(null)}
            >
              {error}
            </Alert>
          )}

          <Box sx={{ mb: 3 }}>
            <MagicInput onSubmit={handleAddTask} disabled={submitting} />
          </Box>

          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            <TaskList
              tasks={tasks}
              onToggle={handleToggleTask}
              onDelete={handleDeleteTask}
              onClearAll={handleClearAll}
            />
          )}
        </Box>
      </Container>
    </ThemeProvider>
  )
}

export default App
