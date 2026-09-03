import { useState, useEffect, useCallback } from 'react';
import {
    Box,
    Paper,
    Typography,
    Chip,
    Button,
    CircularProgress,
    List,
    ListItem,
    ListItemText,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
} from '@mui/material';
import EventRepeatIcon from '@mui/icons-material/EventRepeat';
import ErrorAlert from './ErrorAlert';
import EmptyState from './EmptyState';
import api from '../api/client.js';

const QUADRANTS = [
    {
        key: 'do_first',
        title: 'Срочно и важно',
        hint: 'Сделать в первую очередь',
        color: 'error',
    },
    {
        key: 'schedule',
        title: 'Важно, не срочно',
        hint: 'Запланировать',
        color: 'primary',
    },
    {
        key: 'delegate',
        title: 'Срочно, не важно',
        hint: 'Можно делегировать',
        color: 'warning',
    },
    {
        key: 'later',
        title: 'Не срочно и не важно',
        hint: 'Позже или отказаться',
        color: 'default',
    },
];

function formatDue(value) {
    if (!value) return 'без срока';
    return new Date(value).toLocaleString('ru-RU', {
        day: 'numeric',
        month: 'short',
        hour: '2-digit',
        minute: '2-digit',
    });
}

function TaskRows({ tasks, onReschedule, reschedulingId }) {
    if (!tasks || tasks.length === 0) {
        return (
            <Typography variant="body2" color="text.secondary">
                Нет задач
            </Typography>
        );
    }

    return (
        <List dense disablePadding>
            {tasks.map((task) => (
                <ListItem
                    key={task.id}
                    disableGutters
                    secondaryAction={
                        task.is_overdue ? (
                            <Button
                                size="small"
                                startIcon={
                                    reschedulingId === task.id ? (
                                        <CircularProgress size={14} />
                                    ) : (
                                        <EventRepeatIcon fontSize="small" />
                                    )
                                }
                                onClick={() => onReschedule(task)}
                                disabled={Boolean(reschedulingId)}
                            >
                                Перенести
                            </Button>
                        ) : null
                    }
                    sx={{ pr: task.is_overdue ? 14 : 0 }}
                >
                    <Box sx={{ minWidth: 0, width: '100%' }}>
                        <ListItemText
                            primary={task.title}
                            secondary={formatDue(task.due_at)}
                        />
                        {task.is_overdue && (
                            <Chip
                                label="Просрочено"
                                size="small"
                                color="error"
                                sx={{ mt: 0.5 }}
                            />
                        )}
                    </Box>
                </ListItem>
            ))}
        </List>
    );
}

export default function Planner() {
    const [schedule, setSchedule] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [reschedulingId, setReschedulingId] = useState(null);
    const [proposal, setProposal] = useState(null);
    const [applying, setApplying] = useState(false);

    const loadSchedule = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await api.get('/schedule/today');
            setSchedule(data);
        } catch (err) {
            setError(err.message || 'Не удалось загрузить расписание');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        loadSchedule();
    }, [loadSchedule]);

    const handleReschedule = async (task) => {
        try {
            setReschedulingId(task.id);
            setError(null);
            const result = await api.post(`/tasks/${task.id}/reschedule`, {});
            setProposal(result);
        } catch (err) {
            setError(err.message || 'Не удалось предложить новое время');
        } finally {
            setReschedulingId(null);
        }
    };

    const handleConfirmReschedule = async () => {
        if (!proposal) return;
        try {
            setApplying(true);
            setError(null);
            await api.patch(`/tasks/${proposal.task_id}`, {
                due_at: proposal.suggested_due_at,
            });
            setProposal(null);
            await loadSchedule();
        } catch (err) {
            setError(err.message || 'Не удалось сохранить новое время');
        } finally {
            setApplying(false);
        }
    };

    if (loading && !schedule) {
        return (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                <CircularProgress />
            </Box>
        );
    }

    if (error && !schedule) {
        return (
            <EmptyState
                message={error}
                actionLabel="Повторить"
                onAction={loadSchedule}
            />
        );
    }

    return (
        <Box>
            <Typography variant="h5" component="h2" gutterBottom>
                Планировщик на сегодня
            </Typography>
            <Typography
                variant="body2"
                color="text.secondary"
                sx={{ mb: 2 }}
            >
                Фокус-задачи и матрица Эйзенхауэра
                {schedule?.date ? ` · ${schedule.date}` : ''}
            </Typography>

            <ErrorAlert
                message={error}
                onClose={() => setError(null)}
                onRetry={loadSchedule}
            />

            {schedule?.overdue?.length > 0 && (
                <Paper sx={{ p: 2, mb: 2 }}>
                    <Typography variant="subtitle1" gutterBottom>
                        Просроченные задачи
                    </Typography>
                    <TaskRows
                        tasks={schedule.overdue}
                        onReschedule={handleReschedule}
                        reschedulingId={reschedulingId}
                    />
                </Paper>
            )}

            <Paper sx={{ p: 2, mb: 3 }}>
                <Typography variant="subtitle1" gutterBottom>
                    Фокус дня
                </Typography>
                {schedule?.focus_tasks?.length ? (
                    <TaskRows
                        tasks={schedule.focus_tasks}
                        onReschedule={handleReschedule}
                        reschedulingId={reschedulingId}
                    />
                ) : (
                    <Typography variant="body2" color="text.secondary">
                        Нет открытых задач на сегодня.
                    </Typography>
                )}
            </Paper>

            <Box
                sx={{
                    display: 'grid',
                    gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
                    gap: 2,
                }}
            >
                {QUADRANTS.map((quadrant) => (
                    <Paper key={quadrant.key} sx={{ p: 2, minHeight: 160 }}>
                        <Chip
                            label={quadrant.title}
                            color={
                                quadrant.color === 'default'
                                    ? 'default'
                                    : quadrant.color
                            }
                            size="small"
                            sx={{ mb: 1 }}
                        />
                        <Typography
                            variant="caption"
                            color="text.secondary"
                            display="block"
                            sx={{ mb: 1 }}
                        >
                            {quadrant.hint}
                        </Typography>
                        <TaskRows
                            tasks={schedule?.quadrants?.[quadrant.key] || []}
                            onReschedule={handleReschedule}
                            reschedulingId={reschedulingId}
                        />
                    </Paper>
                ))}
            </Box>

            <Dialog
                open={Boolean(proposal)}
                onClose={() => !applying && setProposal(null)}
            >
                <DialogTitle>Предложенное время</DialogTitle>
                <DialogContent>
                    {proposal && (
                        <Box sx={{ pt: 1 }}>
                            <Typography variant="body1" gutterBottom>
                                Новое окно: {formatDue(proposal.suggested_due_at)}
                            </Typography>
                            {proposal.current_due_at && (
                                <Typography
                                    variant="body2"
                                    color="text.secondary"
                                    gutterBottom
                                >
                                    Было: {formatDue(proposal.current_due_at)}
                                </Typography>
                            )}
                            <Typography variant="body2" sx={{ mt: 1 }}>
                                {proposal.reason}
                            </Typography>
                            {proposal.day_load_summary && (
                                <Typography
                                    variant="body2"
                                    color="text.secondary"
                                    sx={{ mt: 1 }}
                                >
                                    Загрузка: {proposal.day_load_summary}
                                </Typography>
                            )}
                        </Box>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button
                        onClick={() => setProposal(null)}
                        disabled={applying}
                    >
                        Отмена
                    </Button>
                    <Button
                        variant="contained"
                        onClick={handleConfirmReschedule}
                        disabled={applying}
                    >
                        {applying ? 'Сохранение…' : 'Подтвердить'}
                    </Button>
                </DialogActions>
            </Dialog>
        </Box>
    );
}
