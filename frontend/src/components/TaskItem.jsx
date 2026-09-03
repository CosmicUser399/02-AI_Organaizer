import { useState } from 'react';
import {
    ListItem,
    ListItemButton,
    ListItemIcon,
    ListItemText,
    Checkbox,
    IconButton,
    Chip,
    Box,
    Typography,
    Tooltip,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import ChecklistDialog from './ChecklistDialog';
import { formatDue, getPriorityColor } from '../utils.js';

const PRIORITY_STRIPE_COLOR = {
    error: 'error.main',
    warning: 'warning.main',
    primary: 'primary.main',
    default: 'grey.300',
};

export default function TaskItem({ task, onToggle, onDelete }) {
    const [checklistOpen, setChecklistOpen] = useState(false);

    const handleToggle = () => {
        onToggle(task.id);
    };

    const handleDelete = (e) => {
        e.stopPropagation();
        onDelete(task.id);
    };

    const handleOpenChecklist = (e) => {
        e.stopPropagation();
        setChecklistOpen(true);
    };

    const isDone = task.status === 'done';
    const isOverdue =
        Boolean(task.due_at) && !isDone && new Date(task.due_at) < new Date();

    const priorityColor = getPriorityColor(task.is_urgent, task.is_important);
    const stripeColor = PRIORITY_STRIPE_COLOR[priorityColor];
    const dueLabel = formatDue(task.due_at);

    const secondaryContent = (
        <Box component="span">
            {task.description && (
                <Typography
                    variant="body2"
                    component="span"
                    display="block"
                    color={isDone ? 'text.disabled' : 'text.secondary'}
                >
                    {task.description}
                </Typography>
            )}
            {dueLabel && (
                <Typography
                    variant="caption"
                    component="span"
                    display="block"
                    color={isOverdue ? 'error.main' : 'text.secondary'}
                    sx={{ mt: 0.25 }}
                >
                    ⏰ {dueLabel}
                </Typography>
            )}
        </Box>
    );

    return (
        <>
            <Box sx={{ display: 'flex', alignItems: 'stretch' }}>
                <Box
                    sx={{
                        width: 4,
                        bgcolor: isDone ? 'grey.200' : stripeColor,
                        borderRadius: '2px 0 0 2px',
                        flexShrink: 0,
                    }}
                />
                <Box sx={{ flex: 1 }}>
                    <ListItem
                        disablePadding
                        secondaryAction={
                            <Box>
                                <Tooltip title="Разбить на шаги">
                                    <IconButton
                                        edge="end"
                                        aria-label="decompose"
                                        onClick={handleOpenChecklist}
                                        sx={{ mr: 1 }}
                                    >
                                        <AutoAwesomeIcon />
                                    </IconButton>
                                </Tooltip>
                                <IconButton
                                    edge="end"
                                    aria-label="delete"
                                    onClick={handleDelete}
                                >
                                    <DeleteIcon />
                                </IconButton>
                            </Box>
                        }
                    >
                        <ListItemButton onClick={handleToggle} dense>
                            <ListItemIcon>
                                <Checkbox
                                    edge="start"
                                    checked={isDone}
                                    tabIndex={-1}
                                    disableRipple
                                />
                            </ListItemIcon>
                            <ListItemText
                                primary={task.title}
                                secondary={secondaryContent}
                                sx={{
                                    textDecoration: isDone
                                        ? 'line-through'
                                        : 'none',
                                    color: isDone
                                        ? 'text.disabled'
                                        : 'text.primary',
                                }}
                            />
                            <Box
                                sx={{
                                    display: 'flex',
                                    gap: 0.5,
                                    flexWrap: 'nowrap',
                                    alignItems: 'center',
                                    ml: 1,
                                }}
                            >
                                {task.tag && (
                                    <Chip
                                        label={task.tag}
                                        size="small"
                                        color={
                                            task.tag === 'work'
                                                ? 'primary'
                                                : task.tag === 'personal'
                                                  ? 'secondary'
                                                  : 'default'
                                        }
                                    />
                                )}
                                {priorityColor !== 'default' && (
                                    <Chip
                                        label={
                                            task.is_urgent && task.is_important
                                                ? 'важно+срочно'
                                                : task.is_urgent
                                                  ? 'срочно'
                                                  : 'важно'
                                        }
                                        size="small"
                                        color={priorityColor}
                                    />
                                )}
                                {isOverdue && (
                                    <Chip
                                        label="Просрочено"
                                        size="small"
                                        color="error"
                                        variant="outlined"
                                    />
                                )}
                            </Box>
                        </ListItemButton>
                    </ListItem>
                </Box>
            </Box>
            <ChecklistDialog
                open={checklistOpen}
                onClose={() => setChecklistOpen(false)}
                task={task}
            />
        </>
    );
}
