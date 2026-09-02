import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: '0.0.0.0',
    hmr: {
      clientPort: 5173,
      host: 'localhost',
    },
    watch: {
      usePolling: true,
    },
    proxy: {
      '/api': {
        target: 'http://backend:18080',
        changeOrigin: true,
        timeout: 120000,
        rewrite: (path) => path,
      },
    },
  },
})
