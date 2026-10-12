import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    port: 5173,
    host: '0.0.0.0',
    proxy: {
      '/api/v1/projects': {
        target: 'http://localhost:8009',
        changeOrigin: true,
      },
      '/api/v1/auth': {
        target: 'http://localhost:8009',
        changeOrigin: true,
      },
      '/api/v1/connections': {
        target: 'http://localhost:8010',
        changeOrigin: true,
      },
      '/api/v1/cloud': {
        target: 'http://localhost:8010',
        changeOrigin: true,
      },
      '/api/v1/source': {
        target: 'http://localhost:8010',
        changeOrigin: true,
      },
      '/api/v1/github': {
        target: 'http://localhost:8010',
        changeOrigin: true,
      },
      '/api/v1/repo': {
        target: 'http://localhost:8001',
        changeOrigin: true,
      },
      '/api/admin': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/api/v1/admin': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
