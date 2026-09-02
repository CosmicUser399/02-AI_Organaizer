import { useState } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  List,
  ListItem,
  Checkbox,
  ListItemIcon,
  ListItemText,
  CircularProgress,
  Alert,
  Box,
  Typography,
  Chip,
} from '@mui/material'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import LightbulbOutlinedIcon from '@mui/icons-material/LightbulbOutlined'

export default function ChecklistDialog({ open, onClose, task, api }) {
  const [checklist, setChecklist] = useState([])
  const [suggestions, setSuggestions] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [decomposed, setDecomposed] = useState(false)

  const handleDecompose = async () => {
    try {
      setLoading(true)
      setError(null)
      const result = await api.post(`/tasks/${task.id}/decompose`, {})
      setChecklist(result.checklist_items || [])
      setSuggestions(result.suggestions || [])
      setDecomposed(true)
    } catch (err) {
      setError(err.message || 'Не удалось разбить задачу')
    } finally {
      setLoading(false)
    }
  }

  const handleToggleItem = async (itemId) => {
    const item = checklist.find((i) => i.id === itemId)
    if (!item) return

    try {
      const updated = await api.patch(
        `/tasks/${task.id}/checklist/${itemId}`,
        { is_done: !item.is_done }
      )
      setChecklist(checklist.map((i) => (i.id === itemId ? updated : i)))
    } catch (err) {
      setError(err.message || 'Не удалось обновить пункт')
    }
  }

  const handleClose = () => {
    setChecklist([])
    setSuggestions([])
    setDecomposed(false)
    setError(null)
    onClose()
  }

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="md" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <AutoAwesomeIcon color="primary" />
          <span>Декомпозиция задачи</span>
        </Box>
      </DialogTitle>
      <DialogContent>
        <Typography variant="h6" gutterBottom>
          {task?.title}
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        {!decomposed && !loading && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              Нажмите кнопку, чтобы разбить задачу на шаги с помощью AI
            </Typography>
            <Button
              variant="contained"
              onClick={handleDecompose}
              startIcon={<AutoAwesomeIcon />}
              sx={{ mt: 2 }}
            >
              Разбить на шаги
            </Button>
          </Box>
        )}

        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        )}

        {decomposed && !loading && (
          <>
            <Typography variant="subtitle1" gutterBottom sx={{ mt: 2 }}>
              Шаги выполнения:
            </Typography>
            <List>
              {checklist.map((item) => (
                <ListItem key={item.id} disablePadding>
                  <ListItemIcon>
                    <Checkbox
                      edge="start"
                      checked={item.is_done}
                      onChange={() => handleToggleItem(item.id)}
                      tabIndex={-1}
                      disableRipple
                    />
                  </ListItemIcon>
                  <ListItemText
                    primary={item.text}
                    sx={{
                      textDecoration: item.is_done ? 'line-through' : 'none',
                      color: item.is_done ? 'text.disabled' : 'text.primary',
                    }}
                  />
                </ListItem>
              ))}
            </List>

            {suggestions.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                  <LightbulbOutlinedIcon color="warning" fontSize="small" />
                  <Typography variant="subtitle2" color="text.secondary">
                    Подсказки:
                  </Typography>
                </Box>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {suggestions.map((suggestion, index) => (
                    <Chip
                      key={index}
                      label={suggestion}
                      size="small"
                      variant="outlined"
                      color="warning"
                    />
                  ))}
                </Box>
              </Box>
            )}
          </>
        )}
      </DialogContent>
      <DialogActions>
        <Button onClick={handleClose}>Закрыть</Button>
      </DialogActions>
    </Dialog>
  )
}
