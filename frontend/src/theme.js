import { createTheme } from '@mui/material/styles';

const theme = createTheme({
    palette: {
        primary: { main: '#4f46e5' },
        secondary: { main: '#10b981' },
        error: { main: '#ef4444' },
        warning: { main: '#f59e0b' },
        background: { default: '#f1f5f9', paper: '#ffffff' },
        text: { primary: '#0f172a', secondary: '#64748b' },
    },
    typography: {
        fontFamily: '"Inter", "Roboto", sans-serif',
        h4: { fontWeight: 700, letterSpacing: '-0.5px' },
        h6: { fontWeight: 600 },
        button: { textTransform: 'none', fontWeight: 600 },
    },
    shape: { borderRadius: 12 },
    components: {
        MuiButton: {
            styleOverrides: {
                root: {
                    textTransform: 'none',
                    fontWeight: 600,
                    borderRadius: 8,
                },
            },
        },
        MuiPaper: {
            styleOverrides: {
                root: { boxShadow: '0 1px 3px rgba(0,0,0,0.08)' },
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
    },
});

export default theme;
