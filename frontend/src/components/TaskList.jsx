import { List, Paper, Typography, Button, Box } from '@mui/material'
import TaskItem from './TaskItem'

export default function TaskList({ tasks, onToggle, onDelete, onClearAll }) {
  if (tasks.length === 0) {
    return (
      <Paper sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="body1" color="text.secondary">
          Нет задач. Добавьте новую задачу выше.
        </Typography>
      </Paper>
    )
  }

  return (
    <Paper>
      <List sx={{ py: 0 }}>
        {tasks.map((task) => (
          <TaskItem
            key={task.id}
            task={task}
            onToggle={onToggle}
            onDelete={onDelete}
          />
        ))}
      </List>
      <Box sx={{ p: 2, display: 'flex', justifyContent: 'flex-end' }}>
        <Button
          variant="outlined"
          color="error"
          onClick={onClearAll}
          size="small"
        >
          Очистить список
        </Button>
      </Box>
    </Paper>
  )
}
