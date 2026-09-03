import { useState, useEffect, useCallback } from 'react';
import { ThemeProvider } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Container from '@mui/material/Container';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Alert from '@mui/material/Alert';
import CircularProgress from '@mui/material/CircularProgress';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Chip from '@mui/material/Chip';
import theme from './theme';
import api from './api/client';
import MagicInput from './components/MagicInput';
import TaskList from './components/TaskList';
import NotesPanel from './components/NotesPanel';
import Planner from './components/Planner';
import DigestCard from './components/DigestCard';
import ErrorAlert from './components/ErrorAlert';
import EmptyState from './components/EmptyState';
import ConfirmDialog from './components/ConfirmDialog';

function App() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [warning, setWarning] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [currentTab, setCurrentTab] = useState(0);
  const [clearConfirmOpen, setClearConfirmOpen] = useState(false);

  const loadTasks = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.get('/tasks/');
      setTasks(data);
    } catch (err) {
      setError(err.message || 'Не удалось загрузить задачи');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTasks();
  }, [loadTasks]);

  const handleAddTask = async (input) => {
    try {
      setSubmitting(true);
      setError(null);
      setWarning(null);
      try {
        const newTask = await api.post('/tasks/parse', {
          raw_input: input,
        });
        setTasks((prev) => [newTask, ...prev]);
        return;
      } catch (parseErr) {
        const canFallback =
          !parseErr.status || parseErr.status >= 500 || parseErr.status === 0;
        if (!canFallback) {
          throw parseErr;
        }
        const newTask = await api.post('/tasks/', {
          title: input.trim().slice(0, 255),
          raw_input: input,
        });
        setTasks((prev) => [newTask, ...prev]);
        setWarning('AI не смог разобрать запрос, задача создана как есть.');
      }
    } catch (err) {
      setError(err.message || 'Не удалось добавить задачу');
      throw err;
    } finally {
      setSubmitting(false);
    }
  };

  const handleToggleTask = async (taskId) => {
    const task = tasks.find((t) => t.id === taskId);
    if (!task) return;

    const newStatus = task.status === 'done' ? 'pending' : 'done';

    try {
      setError(null);
      const updated = await api.patch(`/tasks/${taskId}`, {
        status: newStatus,
      });
      setTasks((prev) => prev.map((t) => (t.id === taskId ? updated : t)));
    } catch (err) {
      setError(err.message || 'Не удалось обновить задачу');
    }
  };

  const handleDeleteTask = async (taskId) => {
    try {
      setError(null);
      await api.delete(`/tasks/${taskId}`);
      setTasks((prev) => prev.filter((t) => t.id !== taskId));
    } catch (err) {
      setError(err.message || 'Не удалось удалить задачу');
    }
  };

  const handleUpdateTask = (updatedTask) => {
    setTasks((prev) =>
      prev.map((t) => (t.id === updatedTask.id ? updatedTask : t))
    );
  };

  const handleClearAll = async () => {
    try {
      setError(null);
      await api.delete('/tasks/');
      setTasks([]);
    } catch (err) {
      setError(err.message || 'Не удалось очистить список');
    } finally {
      setClearConfirmOpen(false);
    }
  };

  const openCount = tasks.filter((t) => t.status !== 'done').length;
  const showLoadError = Boolean(error) && !loading && tasks.length === 0;

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="lg">
        <Box sx={{ my: 4 }}>
          <Box
            sx={{
              background:
                'linear-gradient(135deg,' +
                'rgba(59,130,246,0.08) 0%,' +
                'rgba(6,182,212,0.04) 100%)',
              border: '1px solid rgba(96,165,250,0.12)',
              borderRadius: 3,
              px: 3,
              py: 2.5,
              mb: 3,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <Box>
              <Typography variant="h4" component="h1">
                ✦ AI-Органайзер
              </Typography>
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ mt: 0.5 }}
              >
                Умный планировщик задач с AI
              </Typography>
            </Box>
            <Chip
              label={`${openCount} открытых`}
              size="small"
              sx={{
                background: 'rgba(96,165,250,0.12)',
                border: '1px solid rgba(96,165,250,0.30)',
                color: 'primary.main',
                fontWeight: 600,
              }}
            />
          </Box>

          {error && !showLoadError && (
            <ErrorAlert message={error} onClose={() => setError(null)} />
          )}

          {warning && (
            <Alert
              severity="warning"
              sx={{ mb: 2 }}
              onClose={() => setWarning(null)}
            >
              {warning}
            </Alert>
          )}

          <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
            <Tabs
              value={currentTab}
              onChange={(e, newValue) => setCurrentTab(newValue)}
            >
              <Tab label="Задачи" />
              <Tab label="Планировщик" />
              <Tab label="Заметки" />
            </Tabs>
          </Box>

          <Box sx={{ display: currentTab === 0 ? 'block' : 'none' }}>
            <Box sx={{ mb: 3 }}>
              <MagicInput onSubmit={handleAddTask} disabled={submitting} />
            </Box>

            {loading ? (
              <Box
                sx={{
                  display: 'flex',
                  justifyContent: 'center',
                  py: 4,
                }}
              >
                <CircularProgress />
              </Box>
            ) : showLoadError ? (
              <EmptyState
                message={error}
                actionLabel="Повторить"
                onAction={loadTasks}
              />
            ) : (
              <TaskList
                tasks={tasks}
                onToggle={handleToggleTask}
                onDelete={handleDeleteTask}
                onUpdate={handleUpdateTask}
                onClearAll={() => setClearConfirmOpen(true)}
              />
            )}

            <DigestCard />
          </Box>

          <Box sx={{ display: currentTab === 1 ? 'block' : 'none' }}>
            <Planner />
          </Box>

          <Box sx={{ display: currentTab === 2 ? 'block' : 'none' }}>
            <NotesPanel />
          </Box>
        </Box>
      </Container>

      <ConfirmDialog
        open={clearConfirmOpen}
        title="Удалить все задачи?"
        message="Это действие нельзя отменить."
        onConfirm={handleClearAll}
        onCancel={() => setClearConfirmOpen(false)}
      />
    </ThemeProvider>
  );
}

export default App;
