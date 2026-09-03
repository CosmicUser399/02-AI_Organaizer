import { useState, useEffect, useCallback } from 'react';
import {
  Paper,
  Box,
  Typography,
  CircularProgress,
  Button,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import RefreshIcon from '@mui/icons-material/Refresh';
import ErrorAlert from './ErrorAlert';
import api from '../api/client.js';

export default function DigestCard() {
  const [digest, setDigest] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadDigest = useCallback(async (refresh = false) => {
    try {
      setLoading(true);
      setError(null);
      const query = refresh
        ? '/insights/digest?refresh=true'
        : '/insights/digest';
      const data = await api.get(query);
      setDigest(data);
    } catch (err) {
      setError(err.message || 'Не удалось загрузить дайджест');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDigest(false);
  }, [loadDigest]);

  const stats = digest?.stats;
  const percent = stats?.completion_percent ?? 0;

  return (
    <Paper sx={{ p: 2, mt: 3 }}>
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 1,
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <AutoAwesomeIcon color="primary" fontSize="small" />
          <Typography variant="h6">Вечерний дайджест</Typography>
        </Box>
        <Button
          size="small"
          startIcon={loading ? <CircularProgress size={14} /> : <RefreshIcon />}
          onClick={() => loadDigest(true)}
          disabled={loading}
        >
          Обновить
        </Button>
      </Box>

      {error && (
        <ErrorAlert
          message={error}
          onClose={() => setError(null)}
          onRetry={() => loadDigest(true)}
        />
      )}

      {loading && !digest ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
          <CircularProgress />
        </Box>
      ) : digest ? (
        <>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            {digest.date}
            {digest.cached ? ' · из кэша' : ''}
          </Typography>

          <Box sx={{ mb: 2 }}>
            <Box
              sx={{
                display: 'flex',
                justifyContent: 'space-between',
                mb: 0.5,
              }}
            >
              <Typography variant="body2">Выполнено за день</Typography>
              <Typography variant="body2">{percent}%</Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={Math.min(percent, 100)}
              sx={{
                height: 8,
                borderRadius: 4,
                backgroundColor: 'rgba(96,165,250,0.10)',
                '& .MuiLinearProgress-bar': {
                  background: 'linear-gradient(' + '90deg,#3b82f6,#22d3ee)',
                  boxShadow: '0 0 8px rgba(96,165,250,0.4)',
                  borderRadius: 4,
                },
              }}
            />
          </Box>

          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 2 }}>
            <Chip
              size="small"
              label={`Закрыто: ${stats?.completed_count ?? 0}`}
            />
            <Chip
              size="small"
              color="primary"
              label={
                stats?.most_productive_period
                  ? `Пик: ${stats.most_productive_period}`
                  : 'Пик: нет данных'
              }
            />
          </Box>

          <Typography variant="body1" sx={{ mb: 2, whiteSpace: 'pre-wrap' }}>
            {digest.text}
          </Typography>

          {stats?.in_progress_tasks?.length > 0 && (
            <>
              <Typography variant="subtitle2" sx={{ mt: 1 }}>
                Задачи в процессе
              </Typography>
              <List dense disablePadding>
                {stats.in_progress_tasks.map((item, index) => (
                  <ListItem key={index} disableGutters>
                    <ListItemText
                      primary={item.title}
                      secondary={`Выполнено: ${item.progress} (${item.percent}%)`}
                    />
                  </ListItem>
                ))}
              </List>
            </>
          )}

          {stats?.tomorrow_hard_tasks?.length > 0 && (
            <>
              <Typography variant="subtitle2" sx={{ mt: 1 }}>
                Сложные задачи на завтра
              </Typography>
              <List dense disablePadding>
                {stats.tomorrow_hard_tasks.map((title) => (
                  <ListItem key={title} disableGutters>
                    <ListItemText primary={title} />
                  </ListItem>
                ))}
              </List>
            </>
          )}
        </>
      ) : (
        <Typography variant="body2" color="text.secondary">
          Дайджест пока недоступен.
        </Typography>
      )}
    </Paper>
  );
}
