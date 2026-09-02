import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';

export default function EmptyState({ message, actionLabel, onAction }) {
  return (
    <Paper sx={{ p: 3, textAlign: 'center' }}>
      <Typography variant="body1" color="text.secondary">
        {message}
      </Typography>
      {onAction && actionLabel ? (
        <Button onClick={onAction} sx={{ mt: 2 }} variant="outlined">
          {actionLabel}
        </Button>
      ) : null}
    </Paper>
  );
}
