import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Box,
  Chip,
  Typography,
  CircularProgress,
  Alert,
  Paper,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
} from '@mui/material'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import LinkIcon from '@mui/icons-material/Link'

export default function NoteEditor({ open, note, onClose, onSave, api }) {
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [tags, setTags] = useState([])
  const [tagInput, setTagInput] = useState('')
  const [linkedTaskId, setLinkedTaskId] = useState(null)
  const [suggestedTasks, setSuggestedTasks] = useState([])
  const [loadingSuggestions, setLoadingSuggestions] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (note) {
      setTitle(note.title || '')
      setContent(note.content || '')
      setTags(note.tags || [])
      setLinkedTaskId(note.linked_task_id || null)
      if (note.id) {
        loadSuggestedTasks(note.id)
      }
    } else {
      setTitle('')
      setContent('')
      setTags([])
      setLinkedTaskId(null)
      setSuggestedTasks([])
    }
    setError(null)
  }, [note, open])

  const loadSuggestedTasks = async (noteId) => {
    try {
      setLoadingSuggestions(true)
      const suggestions = await api.get(`/notes/${noteId}/suggested-tasks`)
      setSuggestedTasks(suggestions)
    } catch (err) {
      console.error('Failed to load suggestions:', err)
    } finally {
      setLoadingSuggestions(false)
    }
  }

  const handleAddTag = (e) => {
    if (e.key === 'Enter' && tagInput.trim()) {
      e.preventDefault()
      const newTag = tagInput.trim().toLowerCase()
      if (!tags.includes(newTag)) {
        setTags([...tags, newTag])
      }
      setTagInput('')
    }
  }

  const handleDeleteTag = (tagToDelete) => {
    setTags(tags.filter((tag) => tag !== tagToDelete))
  }

  const handleSave = () => {
    if (!title.trim() || !content.trim()) {
      setError('Заголовок и содержимое обязательны')
      return
    }

    onSave({
      title: title.trim(),
      content: content.trim(),
      tags: tags.length > 0 ? tags : undefined,
      linked_task_id: linkedTaskId,
    })
  }

  const handleLinkTask = (taskId) => {
    setLinkedTaskId(taskId === linkedTaskId ? null : taskId)
  }

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {note ? 'Редактировать заметку' : 'Новая заметка'}
      </DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <Box sx={{ mt: 1 }}>
          <TextField
            fullWidth
            label="Заголовок"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            margin="normal"
            required
          />

          <TextField
            fullWidth
            label="Содержимое"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            margin="normal"
            multiline
            rows={8}
            required
          />

          <Box sx={{ mt: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
              <AutoAwesomeIcon fontSize="small" color="primary" />
              <Typography variant="subtitle2">
                Теги (добавятся автоматически при сохранении)
              </Typography>
            </Box>
            <TextField
              fullWidth
              label="Добавить тег (Enter)"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyDown={handleAddTag}
              size="small"
              helperText="Теги будут сгенерированы AI, если не указаны"
            />
            <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mt: 1 }}>
              {tags.map((tag, index) => (
                <Chip
                  key={index}
                  label={tag}
                  size="small"
                  onDelete={() => handleDeleteTag(tag)}
                />
              ))}
            </Box>
          </Box>

          {note && suggestedTasks.length > 0 && (
            <Box sx={{ mt: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <LinkIcon fontSize="small" color="secondary" />
                <Typography variant="subtitle2">
                  Предложенные связи с задачами
                </Typography>
              </Box>
              {loadingSuggestions ? (
                <CircularProgress size={24} />
              ) : (
                <Paper variant="outlined" sx={{ maxHeight: 200, overflow: 'auto' }}>
                  <List dense>
                    {suggestedTasks.map((task) => (
                      <ListItem key={task.task_id} disablePadding>
                        <ListItemButton
                          selected={linkedTaskId === task.task_id}
                          onClick={() => handleLinkTask(task.task_id)}
                        >
                          <ListItemText
                            primary={task.task_title}
                            secondary={`Релевантность: ${Math.round(task.relevance * 100)}%`}
                          />
                        </ListItemButton>
                      </ListItem>
                    ))}
                  </List>
                </Paper>
              )}
            </Box>
          )}
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Отмена</Button>
        <Button onClick={handleSave} variant="contained">
          Сохранить
        </Button>
      </DialogActions>
    </Dialog>
  )
}
