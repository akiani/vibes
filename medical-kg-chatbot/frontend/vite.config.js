import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// The dev server proxies API traffic to FastAPI on :8000, so the frontend can
// use same-origin paths like fetch('/api/chat') and never think about CORS.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:8000',
      '/graphql': 'http://localhost:8000',
    },
  },
})
