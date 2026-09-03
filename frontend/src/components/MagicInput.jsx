import { useState, useEffect, useRef } from 'react';
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
  CircularProgress,
  IconButton,
  Tooltip,
} from '@mui/material';
import HistoryIcon from '@mui/icons-material/History';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import DeleteSweepIcon from '@mui/icons-material/DeleteSweep';

const HISTORY_KEY = 'magic_input_history';
const MAX_HISTORY_ITEMS = 10;

export default function MagicInput({ onSubmit, disabled }) {
  const [input, setInput] = useState('');
  const [history, setHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    const savedHistory = localStorage.getItem(HISTORY_KEY);
    if (savedHistory) {
      try {
        setHistory(JSON.parse(savedHistory));
      } catch {
        // ignore invalid history
      }
    }
  }, []);

  useEffect(() => {
    if (!showHistory) return;

    const handleMouseDown = (e) => {
      if (containerRef.current && !containerRef.current.contains(e.target)) {
        setShowHistory(false);
      }
    };
    document.addEventListener('mousedown', handleMouseDown);
    return () => document.removeEventListener('mousedown', handleMouseDown);
  }, [showHistory]);

  const saveToHistory = (text) => {
    if (!text.trim()) return;

    const newHistory = [text, ...history.filter((item) => item !== text)].slice(
      0,
      MAX_HISTORY_ITEMS
    );

    setHistory(newHistory);
    localStorage.setItem(HISTORY_KEY, JSON.stringify(newHistory));
  };

  const handleClearHistory = () => {
    setHistory([]);
    localStorage.removeItem(HISTORY_KEY);
    setShowHistory(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const text = input;
    try {
      await onSubmit(text);
      saveToHistory(text);
      setInput('');
      setShowHistory(false);
    } catch {
      // Parent shows the error; keep the input so the user can retry.
    }
  };

  const handleHistoryClick = (text) => {
    setInput(text);
    setShowHistory(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      setShowHistory(false);
      return;
    }
    if (e.key === 'ArrowUp' && history.length > 0 && !input) {
      e.preventDefault();
      setInput(history[0]);
    }
  };

  return (
    <Paper sx={{ p: 2 }} ref={containerRef}>
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
          placeholder='Например: "Позвонить клиенту завтра в 14:00, важно"'
          variant="outlined"
          disabled={disabled}
          size="medium"
          helperText={disabled ? 'Обработка с помощью AI...' : ''}
        />
        <Button
          type="submit"
          variant="contained"
          disabled={!input.trim() || disabled}
          startIcon={
            disabled ? (
              <CircularProgress size={20} color="inherit" />
            ) : (
              <AutoAwesomeIcon />
            )
          }
        >
          {disabled ? 'AI обрабатывает...' : 'Добавить'}
        </Button>
      </Box>

      <Collapse in={showHistory}>
        <Box sx={{ mt: 2 }}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              mb: 1,
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <HistoryIcon fontSize="small" sx={{ mr: 1 }} />
              <Typography variant="caption" color="text.secondary">
                История ввода
              </Typography>
            </Box>
            <Tooltip title="Очистить историю">
              <IconButton
                size="small"
                onClick={handleClearHistory}
                color="default"
              >
                <DeleteSweepIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Box>
          <List
            dense
            sx={{
              background: 'rgba(96,165,250,0.05)',
              border: '1px solid rgba(96,165,250,0.10)',
              borderRadius: 1,
            }}
          >
            {history.map((item, index) => (
              <ListItem key={index} disablePadding>
                <ListItemButton
                  onClick={() => handleHistoryClick(item)}
                  sx={{
                    borderRadius: 1,
                    '&:hover': {
                      background: 'rgba(96,165,250,0.08)',
                    },
                  }}
                >
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
  );
}
