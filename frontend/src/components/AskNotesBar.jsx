import { useState } from 'react';
import {
  Paper,
  Box,
  TextField,
  Button,
  Typography,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  Chip,
  Alert,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import ErrorAlert from './ErrorAlert';
import api from '../api/client.js';

export default function AskNotesBar() {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [asked, setAsked] = useState(false);

  const handleAsk = async (event) => {
    event.preventDefault();
    const trimmed = question.trim();
    if (!trimmed) {
      setError('Введите вопрос по заметкам');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const result = await api.post('/notes/ask', {
        question: trimmed,
        top_k: 5,
      });
      setAnswer(result.answer || '');
      setMatches(result.matches || []);
      setAsked(true);
    } catch (err) {
      setError(err.message || 'Не удалось выполнить поиск');
      setAsked(false);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper sx={{ p: 2, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Спроси свои заметки
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Поиск по смыслу: вопрос не обязан совпадать со словами заметки
      </Typography>

      {error && <ErrorAlert message={error} onClose={() => setError(null)} />}

      <Box
        component="form"
        onSubmit={handleAsk}
        sx={{ display: 'flex', gap: 1, mb: 2 }}
      >
        <TextField
          fullWidth
          size="small"
          label="Что вы искали в заметках?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={loading}
        />
        <Button
          type="submit"
          variant="contained"
          startIcon={
            loading ? (
              <CircularProgress size={16} color="inherit" />
            ) : (
              <SearchIcon />
            )
          }
          disabled={loading}
          sx={{ whiteSpace: 'nowrap' }}
        >
          Спросить
        </Button>
      </Box>

      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 2 }}>
          <CircularProgress size={28} />
        </Box>
      )}

      {!loading && asked && (
        <>
          {answer && (
            <Alert severity="info" sx={{ mb: 2 }}>
              {answer}
            </Alert>
          )}

          {matches.length === 0 ? (
            <Typography variant="body2" color="text.secondary">
              Подходящие фрагменты не найдены.
            </Typography>
          ) : (
            <List dense disablePadding>
              {matches.map((match, index) => (
                <ListItem
                  key={`${match.note_id}-${index}`}
                  alignItems="flex-start"
                  sx={{ px: 0 }}
                >
                  <Box sx={{ width: '100%' }}>
                    <Box
                      sx={{
                        display: 'flex',
                        gap: 1,
                        alignItems: 'center',
                        mb: 0.5,
                      }}
                    >
                      <Typography variant="subtitle2">
                        {match.note_title}
                      </Typography>
                      <Chip
                        size="small"
                        label={`${Math.round(match.score * 100)}%`}
                        variant="outlined"
                      />
                    </Box>
                    <ListItemText secondary={match.chunk_text} />
                  </Box>
                </ListItem>
              ))}
            </List>
          )}
        </>
      )}
    </Paper>
  );
}
