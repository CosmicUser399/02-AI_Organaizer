import { createTheme } from '@mui/material/styles';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: { main: '#60a5fa' },
    secondary: { main: '#22d3ee' },
    error: { main: '#f87171' },
    warning: { main: '#fbbf24' },
    background: { default: '#0a0f1e', paper: '#111827' },
    text: { primary: '#f1f5f9', secondary: '#94a3b8' },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", sans-serif',
    h4: { fontWeight: 700, letterSpacing: '-0.5px' },
    h5: { fontWeight: 700 },
    h6: { fontWeight: 600 },
    button: { textTransform: 'none', fontWeight: 600 },
  },
  shape: { borderRadius: 12 },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundImage:
            'radial-gradient(' +
            'ellipse at 20% 10%,' +
            'rgba(59,130,246,0.06) 0%,' +
            'transparent 50%),' +
            'radial-gradient(' +
            'ellipse at 80% 90%,' +
            'rgba(34,211,238,0.04) 0%,' +
            'transparent 50%)',
          backgroundAttachment: 'fixed',
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          borderRadius: 8,
        },
        containedPrimary: {
          background: 'linear-gradient(135deg,#3b82f6 0%,#06b6d4 100%)',
          boxShadow: '0 0 16px rgba(96,165,250,0.35)',
          '&:hover': {
            background: 'linear-gradient(135deg,#2563eb 0%,#0891b2 100%)',
            boxShadow: '0 0 28px rgba(96,165,250,0.55)',
          },
          '&:disabled': {
            background: 'rgba(96,165,250,0.12)',
            boxShadow: 'none',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: 'rgba(17,24,39,0.85)',
          backdropFilter: 'blur(12px)',
          border: '1px solid rgba(96,165,250,0.10)',
          boxShadow: '0 4px 24px rgba(0,0,0,0.5)',
        },
      },
    },
    MuiChip: {
      styleOverrides: { root: { fontWeight: 500 } },
    },
    MuiTab: {
      styleOverrides: {
        root: { textTransform: 'none', fontWeight: 600 },
      },
    },
    MuiTabs: {
      styleOverrides: {
        indicator: {
          background: 'linear-gradient(90deg,#3b82f6,#22d3ee)',
          height: 3,
          borderRadius: '3px 3px 0 0',
          boxShadow: '0 0 8px rgba(96,165,250,0.6)',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
              borderColor: '#60a5fa',
              boxShadow:
                '0 0 0 3px rgba(96,165,250,0.15),' +
                '0 0 12px rgba(96,165,250,0.20)',
            },
          },
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          border: '1px solid rgba(96,165,250,0.15)',
          boxShadow:
            '0 8px 48px rgba(0,0,0,0.7),' + '0 0 0 1px rgba(96,165,250,0.05)',
        },
      },
    },
    MuiDivider: {
      styleOverrides: {
        root: { borderColor: 'rgba(96,165,250,0.08)' },
      },
    },
  },
});

export default theme;
