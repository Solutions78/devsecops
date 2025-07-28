import { createTheme } from '@mui/material/styles'

export const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#0078d4', // Azure blue
      light: '#40a2e3',
      dark: '#004578',
    },
    secondary: {
      main: '#00bcf2', // Azure light blue
      light: '#4fd0ff',
      dark: '#008bb8',
    },
    background: {
      default: '#0d1117', // GitHub dark background
      paper: '#161b22',
    },
    text: {
      primary: '#f0f6fc',
      secondary: '#7d8590',
    },
    success: {
      main: '#238636',
      light: '#2ea043',
      dark: '#1a7f37',
    },
    warning: {
      main: '#d29922',
      light: '#f2cc60',
      dark: '#9a6700',
    },
    error: {
      main: '#f85149',
      light: '#ff7b72',
      dark: '#da3633',
    },
    info: {
      main: '#58a6ff',
      light: '#79c0ff',
      dark: '#388bfd',
    },
  },
  typography: {
    fontFamily: 'Inter, system-ui, Avenir, Helvetica, Arial, sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
      letterSpacing: '-0.01562em',
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
      letterSpacing: '-0.00833em',
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
      letterSpacing: '0em',
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
      letterSpacing: '0.00735em',
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600,
      letterSpacing: '0em',
    },
    h6: {
      fontSize: '1.125rem',
      fontWeight: 600,
      letterSpacing: '0.0075em',
    },
    body1: {
      fontSize: '1rem',
      fontWeight: 400,
      lineHeight: 1.5,
    },
    body2: {
      fontSize: '0.875rem',
      fontWeight: 400,
      lineHeight: 1.43,
    },
    button: {
      textTransform: 'none',
      fontWeight: 500,
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          textTransform: 'none',
          fontWeight: 500,
          boxShadow: 'none',
          '&:hover': {
            boxShadow: 'none',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          border: '1px solid #30363d',
          backgroundImage: 'none',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          border: '1px solid #30363d',
          backgroundImage: 'none',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          backgroundColor: '#0d1117',
          borderBottom: '1px solid #30363d',
        },
      },
    },
  },
})