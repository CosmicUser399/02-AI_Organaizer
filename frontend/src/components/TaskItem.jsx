import { useState } from 'react'
import {
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Checkbox,
  IconButton,
  Chip,
  Box,
  Tooltip,
} from '@mui/material'
import DeleteIcon from '@mui/icons-material/Delete'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import ChecklistDialog from './ChecklistDialog'

export default function TaskItem({ task, onToggle, onDelete, api }) {
  const [checklistOpen, setChecklistOpen] = useState(false)

  const handleToggle = () => {
    onToggle(task.id)
  }

  const handleDelete = (e) => {
    e.stopPropagation()
    onDelete(task.id)
  }

  const handleOpenChecklist = (e) => {
    e.stopPropagation()
    setChecklistOpen(true)
  }

  const isDone = task.status === 'done'
  const isOverdue =
    Boolean(task.due_at) && !isDone && new Date(task.due_at) < new Date()

  return (
    <>
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
            <IconButton edge="end" aria-label="delete" onClick={handleDelete}>
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
            secondary={task.description}
            sx={{
              textDecoration: isDone ? 'line-through' : 'none',
              color: isDone ? 'text.disabled' : 'text.primary',
            }}
          />
          {task.tag && (
            <Chip
              label={task.tag}
              size="small"
              sx={{ ml: 1 }}
              color={
                task.tag === 'work'
                  ? 'primary'
                  : task.tag === 'personal'
                    ? 'secondary'
                    : 'default'
              }
            />
          )}
          {isOverdue && (
            <Chip
              label="Просрочено"
              size="small"
              color="error"
              sx={{ ml: 1 }}
            />
          )}
        </ListItemButton>
      </ListItem>
      <ChecklistDialog
        open={checklistOpen}
        onClose={() => setChecklistOpen(false)}
        task={task}
        api={api}
      />
    </>
  )
}
