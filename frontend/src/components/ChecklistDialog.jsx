import { useState, useEffect, useCallback } from 'react';
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
  TextField,
  IconButton,
} from '@mui/material';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import LightbulbOutlinedIcon from '@mui/icons-material/LightbulbOutlined';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import EditIcon from '@mui/icons-material/Edit';
import CheckIcon from '@mui/icons-material/Check';
import CloseIcon from '@mui/icons-material/Close';
import api from '../api/client.js';

export default function ChecklistDialog({ open, onClose, task }) {
  const [checklist, setChecklist] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [decomposed, setDecomposed] = useState(false);
  const [newItemText, setNewItemText] = useState('');
  const [addingItem, setAddingItem] = useState(false);
  const [editingItemId, setEditingItemId] = useState(null);
  const [editingText, setEditingText] = useState('');

  const loadExistingChecklist = useCallback(async () => {
    if (!task?.id) return;

    try {
      setLoading(true);
      const items = await api.get(`/tasks/${task.id}/checklist`);
      if (items && items.length > 0) {
        setChecklist(items);
        setDecomposed(true);
      }
    } catch {
      setError('Не удалось загрузить чек-лист');
      setDecomposed(false);
    } finally {
      setLoading(false);
    }
  }, [task?.id]);

  useEffect(() => {
    if (open && task?.id) {
      loadExistingChecklist();
    }
  }, [open, task?.id, loadExistingChecklist]);

  const handleDecompose = async () => {
    try {
      setLoading(true);
      setError(null);
      const result = await api.post(`/tasks/${task.id}/decompose`, {});
      setChecklist(result.checklist_items || []);
      setSuggestions(result.suggestions || []);
      setDecomposed(true);
    } catch (err) {
      setError(err.message || 'Не удалось разбить задачу');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleItem = async (itemId) => {
    const item = checklist.find((i) => i.id === itemId);
    if (!item) return;

    try {
      const updated = await api.patch(`/tasks/${task.id}/checklist/${itemId}`, {
        is_done: !item.is_done,
      });
      setChecklist(checklist.map((i) => (i.id === itemId ? updated : i)));
    } catch (err) {
      setError(err.message || 'Не удалось обновить пункт');
    }
  };

  const handleAddItem = async () => {
    const trimmed = newItemText.trim();
    if (!trimmed) return;

    try {
      setAddingItem(true);
      setError(null);
      const maxPosition = Math.max(0, ...checklist.map((i) => i.position));
      const created = await api.post(`/tasks/${task.id}/checklist`, {
        text: trimmed,
        position: maxPosition + 1,
      });
      setChecklist([...checklist, created]);
      setNewItemText('');
    } catch (err) {
      setError(err.message || 'Не удалось добавить пункт');
    } finally {
      setAddingItem(false);
    }
  };

  const handleDeleteItem = async (itemId) => {
    try {
      await api.delete(`/tasks/${task.id}/checklist/${itemId}`);
      setChecklist(checklist.filter((i) => i.id !== itemId));
    } catch (err) {
      setError(err.message || 'Не удалось удалить пункт');
    }
  };

  const handleStartEdit = (item) => {
    setEditingItemId(item.id);
    setEditingText(item.text);
  };

  const handleCancelEdit = () => {
    setEditingItemId(null);
    setEditingText('');
  };

  const handleSaveEdit = async (itemId) => {
    const trimmed = editingText.trim();
    if (!trimmed) {
      handleCancelEdit();
      return;
    }

    try {
      const updated = await api.patch(`/tasks/${task.id}/checklist/${itemId}`, {
        text: trimmed,
      });
      setChecklist(checklist.map((i) => (i.id === itemId ? updated : i)));
      setEditingItemId(null);
      setEditingText('');
    } catch (err) {
      setError(err.message || 'Не удалось обновить пункт');
    }
  };

  const handleClose = () => {
    setChecklist([]);
    setSuggestions([]);
    setDecomposed(false);
    setNewItemText('');
    setEditingItemId(null);
    setEditingText('');
    setError(null);
    onClose();
  };

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
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                mt: 2,
                mb: 1,
              }}
            >
              <Typography variant="subtitle1">
                Шаги выполнения ({checklist.filter((i) => i.is_done).length}/
                {checklist.length})
              </Typography>
            </Box>
            {checklist.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                Пока нет шагов. Добавьте шаг вручную или разбейте задачу заново.
              </Typography>
            ) : (
              <List>
                {checklist.map((item) => (
                  <ListItem
                    key={item.id}
                    disablePadding
                    secondaryAction={
                      editingItemId === item.id ? (
                        <Box>
                          <IconButton
                            edge="end"
                            aria-label="save"
                            onClick={() => handleSaveEdit(item.id)}
                            size="small"
                            color="primary"
                            sx={{ mr: 1 }}
                          >
                            <CheckIcon fontSize="small" />
                          </IconButton>
                          <IconButton
                            edge="end"
                            aria-label="cancel"
                            onClick={handleCancelEdit}
                            size="small"
                          >
                            <CloseIcon fontSize="small" />
                          </IconButton>
                        </Box>
                      ) : (
                        <Box>
                          <IconButton
                            edge="end"
                            aria-label="edit"
                            onClick={() => handleStartEdit(item)}
                            size="small"
                            sx={{ mr: 1 }}
                          >
                            <EditIcon fontSize="small" />
                          </IconButton>
                          <IconButton
                            edge="end"
                            aria-label="delete"
                            onClick={() => handleDeleteItem(item.id)}
                            size="small"
                          >
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </Box>
                      )
                    }
                  >
                    <ListItemIcon>
                      <Checkbox
                        edge="start"
                        checked={item.is_done}
                        onChange={() => handleToggleItem(item.id)}
                        tabIndex={-1}
                        disableRipple
                        disabled={editingItemId === item.id}
                      />
                    </ListItemIcon>
                    {editingItemId === item.id ? (
                      <TextField
                        fullWidth
                        size="small"
                        value={editingText}
                        onChange={(e) => setEditingText(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            handleSaveEdit(item.id);
                          } else if (e.key === 'Escape') {
                            handleCancelEdit();
                          }
                        }}
                        autoFocus
                        sx={{ mr: 2 }}
                      />
                    ) : (
                      <ListItemText
                        primary={item.text}
                        sx={{
                          textDecoration: item.is_done
                            ? 'line-through'
                            : 'none',
                          color: item.is_done
                            ? 'text.disabled'
                            : 'text.primary',
                        }}
                      />
                    )}
                  </ListItem>
                ))}
              </List>
            )}

            <Box sx={{ display: 'flex', gap: 1, mt: 2 }}>
              <TextField
                fullWidth
                size="small"
                placeholder="Добавить новый шаг..."
                value={newItemText}
                onChange={(e) => setNewItemText(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleAddItem();
                  }
                }}
                disabled={addingItem}
              />
              <Button
                variant="outlined"
                startIcon={
                  addingItem ? <CircularProgress size={16} /> : <AddIcon />
                }
                onClick={handleAddItem}
                disabled={!newItemText.trim() || addingItem}
              >
                Добавить
              </Button>
            </Box>

            {suggestions.length > 0 && (
              <Box sx={{ mt: 3 }}>
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                    mb: 2,
                  }}
                >
                  <LightbulbOutlinedIcon color="warning" fontSize="small" />
                  <Typography variant="subtitle2" color="text.secondary">
                    Подсказки:
                  </Typography>
                </Box>
                <Box
                  sx={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: 1,
                  }}
                >
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
        <Button onClick={handleClose}>Отмена</Button>
        <Button onClick={handleClose} variant="contained">
          Сохранить
        </Button>
      </DialogActions>
    </Dialog>
  );
}
