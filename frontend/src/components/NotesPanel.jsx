import { useState, useEffect } from 'react'
import {
  Paper,
  Box,
  Typography,
  Button,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Chip,
  IconButton,
  Alert,
  CircularProgress,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import DeleteIcon from '@mui/icons-material/Delete'
import NoteEditor from './NoteEditor'

export default function NotesPanel({ api }) {
  const [notes, setNotes] = useState([])
  const [selectedNote, setSelectedNote] = useState(null)
  const [editorOpen, setEditorOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadNotes()
  }, [])

  const loadNotes = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await api.get('/notes/')
      setNotes(data)
    } catch (err) {
      setError(err.message || 'Не удалось загрузить заметки')
    } finally {
      setLoading(false)
    }
  }

  const handleCreateNote = () => {
    setSelectedNote(null)
    setEditorOpen(true)
  }

  const handleEditNote = (note) => {
    setSelectedNote(note)
    setEditorOpen(true)
  }

  const handleDeleteNote = async (noteId, e) => {
    e.stopPropagation()
    if (!window.confirm('Удалить заметку?')) return

    try {
      setError(null)
      await api.delete(`/notes/${noteId}`)
      setNotes(notes.filter((n) => n.id !== noteId))
    } catch (err) {
      setError(err.message || 'Не удалось удалить заметку')
    }
  }

  const handleSaveNote = async (noteData) => {
    try {
      setError(null)
      if (selectedNote) {
        const updated = await api.patch(`/notes/${selectedNote.id}`, noteData)
        setNotes(notes.map((n) => (n.id === selectedNote.id ? updated : n)))
      } else {
        const created = await api.post('/notes/', noteData)
        setNotes([created, ...notes])
      }
      setEditorOpen(false)
      setSelectedNote(null)
    } catch (err) {
      setError(err.message || 'Не удалось сохранить заметку')
    }
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Typography variant="h5" component="h2">
          Заметки
        </Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleCreateNote}
        >
          Новая заметка
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      ) : notes.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            Нет заметок. Создайте первую заметку.
          </Typography>
        </Paper>
      ) : (
        <Paper>
          <List sx={{ py: 0 }}>
            {notes.map((note) => (
              <ListItem
                key={note.id}
                disablePadding
                secondaryAction={
                  <IconButton
                    edge="end"
                    aria-label="delete"
                    onClick={(e) => handleDeleteNote(note.id, e)}
                  >
                    <DeleteIcon />
                  </IconButton>
                }
              >
                <ListItemButton onClick={() => handleEditNote(note)}>
                  <Box sx={{ flexGrow: 1 }}>
                    <ListItemText primary={note.title} />
                    {note.tags && note.tags.length > 0 && (
                      <Box
                        sx={{
                          display: 'flex',
                          gap: 0.5,
                          flexWrap: 'wrap',
                          mt: 0.5,
                        }}
                      >
                        {note.tags.map((tag, index) => (
                          <Chip
                            key={index}
                            label={tag}
                            size="small"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    )}
                  </Box>
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Paper>
      )}

      <NoteEditor
        open={editorOpen}
        note={selectedNote}
        onClose={() => {
          setEditorOpen(false)
          setSelectedNote(null)
        }}
        onSave={handleSaveNote}
        api={api}
      />
    </Box>
  )
}
