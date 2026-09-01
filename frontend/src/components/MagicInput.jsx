import { useState, useEffect } from 'react'
import {
  TextField,
  Button,
  Paper,
  Box,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Typography,
  Collapse,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import HistoryIcon from '@mui/icons-material/History'

const HISTORY_KEY = 'magic_input_history'
const MAX_HISTORY_ITEMS = 10

export default function MagicInput({ onSubmit, disabled }) {
  const [input, setInput] = useState('')
  const [history, setHistory] = useState([])
  const [showHistory, setShowHistory] = useState(false)

  useEffect(() => {
    const savedHistory = localStorage.getItem(HISTORY_KEY)
    if (savedHistory) {
      try {
        setHistory(JSON.parse(savedHistory))
      } catch {
        // ignore invalid history
      }
    }
  }, [])

  const saveToHistory = (text) => {
    if (!text.trim()) return

    const newHistory = [text, ...history.filter((item) => item !== text)].slice(
      0,
      MAX_HISTORY_ITEMS
    )

    setHistory(newHistory)
    localStorage.setItem(HISTORY_KEY, JSON.stringify(newHistory))
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!input.trim()) return

    saveToHistory(input)
    onSubmit(input)
    setInput('')
    setShowHistory(false)
  }

  const handleHistoryClick = (text) => {
    setInput(text)
    setShowHistory(false)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowUp' && history.length > 0 && !input) {
      e.preventDefault()
      setInput(history[0])
    }
  }

  return (
    <Paper sx={{ p: 2 }}>
      <Box
        component="form"
        onSubmit={handleSubmit}
        sx={{ display: 'flex', gap: 1 }}
      >
        <TextField
          fullWidth
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => setShowHistory(history.length > 0)}
          placeholder="Опишите задачу на естественном языке..."
          variant="outlined"
          disabled={disabled}
          size="medium"
        />
        <Button
          type="submit"
          variant="contained"
          disabled={!input.trim() || disabled}
          startIcon={<AddIcon />}
        >
          Добавить
        </Button>
      </Box>

      <Collapse in={showHistory}>
        <Box sx={{ mt: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <HistoryIcon fontSize="small" sx={{ mr: 1 }} />
            <Typography variant="caption" color="text.secondary">
              История ввода
            </Typography>
          </Box>
          <List dense sx={{ bgcolor: 'action.hover', borderRadius: 1 }}>
            {history.map((item, index) => (
              <ListItem key={index} disablePadding>
                <ListItemButton onClick={() => handleHistoryClick(item)}>
                  <ListItemText
                    primary={item}
                    primaryTypographyProps={{
                      noWrap: true,
                      variant: 'body2',
                    }}
                  />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Box>
      </Collapse>
    </Paper>
  )
}
