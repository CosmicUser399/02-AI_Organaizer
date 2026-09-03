import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControlLabel,
  Checkbox,
  MenuItem,
  Box,
  Alert,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import api from '../api/client.js';

const TAG_OPTIONS = [
  'работа',
  'личное',
  'здоровье',
  'обучение',
  'финансы',
  'покупки',
  'другое',
];

export default function EditTaskDialog({ open, onClose, task, onTaskUpdated }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    due_at: '',
    tag: '',
    is_urgent: false,
    is_important: false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (task && open) {
      setFormData({
        title: task.title || '',
        description: task.description || '',
        due_at: task.due_at
          ? new Date(task.due_at).toISOString().slice(0, 16)
          : '',
        tag: task.tag || '',
        is_urgent: task.is_urgent || false,
        is_important: task.is_important || false,
      });
    }
  }, [task, open]);

  const handleChange = (field) => (event) => {
    const value =
      event.target.type === 'checkbox'
        ? event.target.checked
        : event.target.value;
    setFormData({ ...formData, [field]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.title.trim()) {
      setError('Заголовок задачи обязателен');
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const updateData = {
        title: formData.title.trim(),
        description: formData.description.trim() || null,
        tag: formData.tag || null,
        is_urgent: formData.is_urgent,
        is_important: formData.is_important,
      };

      if (formData.due_at) {
        updateData.due_at = new Date(formData.due_at).toISOString();
      } else {
        updateData.due_at = null;
      }

      const updated = await api.patch(`/tasks/${task.id}`, updateData);
      onTaskUpdated(updated);
      onClose();
    } catch (err) {
      setError(err.message || 'Не удалось обновить задачу');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setError(null);
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <EditIcon color="primary" />
          <span>Редактировать задачу</span>
        </Box>
      </DialogTitle>
      <form onSubmit={handleSubmit}>
        <DialogContent>
          {error && (
            <Alert
              severity="error"
              sx={{ mb: 2 }}
              onClose={() => setError(null)}
            >
              {error}
            </Alert>
          )}

          <TextField
            autoFocus
            fullWidth
            label="Заголовок"
            value={formData.title}
            onChange={handleChange('title')}
            required
            margin="normal"
            disabled={loading}
          />

          <TextField
            fullWidth
            label="Описание"
            value={formData.description}
            onChange={handleChange('description')}
            multiline
            rows={3}
            margin="normal"
            disabled={loading}
          />

          <TextField
            fullWidth
            label="Дата и время выполнения"
            type="datetime-local"
            value={formData.due_at}
            onChange={handleChange('due_at')}
            margin="normal"
            disabled={loading}
            InputLabelProps={{
              shrink: true,
            }}
          />

          <TextField
            fullWidth
            select
            label="Категория"
            value={formData.tag}
            onChange={handleChange('tag')}
            margin="normal"
            disabled={loading}
          >
            <MenuItem value="">
              <em>Без категории</em>
            </MenuItem>
            {TAG_OPTIONS.map((tag) => (
              <MenuItem key={tag} value={tag}>
                {tag}
              </MenuItem>
            ))}
          </TextField>

          <Box sx={{ mt: 2 }}>
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.is_urgent}
                  onChange={handleChange('is_urgent')}
                  disabled={loading}
                />
              }
              label="Срочная"
            />
            <FormControlLabel
              control={
                <Checkbox
                  checked={formData.is_important}
                  onChange={handleChange('is_important')}
                  disabled={loading}
                />
              }
              label="Важная"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} disabled={loading}>
            Отмена
          </Button>
          <Button type="submit" variant="contained" disabled={loading}>
            {loading ? 'Сохранение...' : 'Сохранить'}
          </Button>
        </DialogActions>
      </form>
    </Dialog>
  );
}
