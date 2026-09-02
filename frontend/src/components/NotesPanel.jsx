import { useState, useEffect, useCallback } from 'react';
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
  CircularProgress,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import NoteEditor from './NoteEditor';
import AskNotesBar from './AskNotesBar';
import ErrorAlert from './ErrorAlert';
import EmptyState from './EmptyState';

export default function NotesPanel({ api }) {
  const [notes, setNotes] = useState([]);
  const [selectedNote, setSelectedNote] = useState(null);
  const [editorOpen, setEditorOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const loadNotes = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.get('/notes/');
      setNotes(data);
    } catch (err) {
      setError(err.message || 'Не удалось загрузить заметки');
    } finally {
      setLoading(false);
    }
  }, [api]);

  useEffect(() => {
    loadNotes();
  }, [loadNotes]);

  const handleCreateNote = () => {
    setSelectedNote(null);
    setEditorOpen(true);
  };

  const handleEditNote = (note) => {
    setSelectedNote(note);
    setEditorOpen(true);
  };

  const handleDeleteNote = async (noteId, e) => {
    e.stopPropagation();
    if (!window.confirm('Удалить заметку?')) return;

    try {
      setError(null);
      await api.delete(`/notes/${noteId}`);
      setNotes((prev) => prev.filter((n) => n.id !== noteId));
    } catch (err) {
      setError(err.message || 'Не удалось удалить заметку');
    }
  };

  const handleSaveNote = async (noteData) => {
    setError(null);
    if (selectedNote) {
      const updated = await api.patch(`/notes/${selectedNote.id}`, noteData);
      setNotes((prev) =>
        prev.map((n) => (n.id === selectedNote.id ? updated : n))
      );
    } else {
      const created = await api.post('/notes/', noteData);
      setNotes((prev) => [created, ...prev]);
    }
    setEditorOpen(false);
    setSelectedNote(null);
  };

  return (
    <Box>
      <AskNotesBar api={api} />

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

      {error && notes.length > 0 && (
        <ErrorAlert
          message={error}
          onClose={() => setError(null)}
          onRetry={loadNotes}
        />
      )}

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
          <CircularProgress />
        </Box>
      ) : error && notes.length === 0 ? (
        <EmptyState
          message={error}
          actionLabel="Повторить"
          onAction={loadNotes}
        />
      ) : notes.length === 0 ? (
        <EmptyState message="Нет заметок. Создайте первую заметку." />
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
          setEditorOpen(false);
          setSelectedNote(null);
        }}
        onSave={handleSaveNote}
        api={api}
      />
    </Box>
  );
}
