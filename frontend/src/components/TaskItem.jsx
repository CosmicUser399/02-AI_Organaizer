import {
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Checkbox,
  IconButton,
  Chip,
} from '@mui/material'
import DeleteIcon from '@mui/icons-material/Delete'

export default function TaskItem({ task, onToggle, onDelete }) {
  const handleToggle = () => {
    onToggle(task.id)
  }

  const handleDelete = (e) => {
    e.stopPropagation()
    onDelete(task.id)
  }

  const isDone = task.status === 'done'

  return (
    <ListItem
      disablePadding
      secondaryAction={
        <IconButton edge="end" aria-label="delete" onClick={handleDelete}>
          <DeleteIcon />
        </IconButton>
      }
    >
      <ListItemButton onClick={handleToggle} dense>
        <ListItemIcon>
          <Checkbox edge="start" checked={isDone} tabIndex={-1} disableRipple />
        </ListItemIcon>
        <ListItemText
          primary={task.title}
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
      </ListItemButton>
    </ListItem>
  )
}
