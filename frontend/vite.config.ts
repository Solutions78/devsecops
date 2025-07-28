import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/health': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
      },
      '/task': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
      },
      '/agents': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
      },
      '/tasks': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
      },
      '/metrics': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
      },
      '/updates': {
        target: 'ws://localhost:8001',
        ws: true,
      },
    },
  },
})