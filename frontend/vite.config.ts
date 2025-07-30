import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react({
      // Standard React plugin configuration for optimal HMR
      include: "**/*.{jsx,tsx}",
    }),
  ],
  optimizeDeps: {
    // Include these dependencies in pre-bundling for better HMR performance
    include: ['react', 'react-dom', '@mui/material', '@tanstack/react-query'],
  },
  esbuild: {
    // Ensure proper JSX handling
    jsx: 'automatic',
  },
  server: {
    port: 3005,
    // Improve HMR performance
    hmr: {
      overlay: true,
      port: 3006, // Use different port for HMR to avoid conflicts
    },
    proxy: {
      '/api': {
        target: `http://${process.env.BACKEND_HOST || 'localhost'}:${process.env.BACKEND_PORT || '8001'}`,
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, ''),
        ws: true, // Enable WebSocket proxying
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('proxy error', err);
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log('Sending Request to the Target:', req.method, req.url);
          });
          proxy.on('proxyRes', (proxyRes, req, _res) => {
            console.log('Received Response from the Target:', proxyRes.statusCode, req.url);
          });
        },
      },
    },
  },
  // Build optimizations that also help with HMR
  build: {
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          // Separate vendor chunks for better caching and HMR
          vendor: ['react', 'react-dom'],
          mui: ['@mui/material', '@mui/icons-material'],
          queries: ['@tanstack/react-query'],
        },
      },
    },
  },
})
