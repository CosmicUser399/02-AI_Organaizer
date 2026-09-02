import Alert from '@mui/material/Alert';
import Button from '@mui/material/Button';

export default function ErrorAlert({ message, onClose, onRetry }) {
  if (!message) {
    return null;
  }

  return (
    <Alert
      severity="error"
      sx={{ mb: 2 }}
      onClose={onClose}
      action={
        onRetry ? (
          <Button color="inherit" size="small" onClick={onRetry}>
            Повторить
          </Button>
        ) : null
      }
    >
      {message}
    </Alert>
  );
}
