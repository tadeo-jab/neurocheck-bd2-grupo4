import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/auth': 'http://localhost:8000',
      '/curriculum': 'http://localhost:8000',
      '/study': 'http://localhost:8000',
      '/mates': 'http://localhost:8000',
    },
  },
})
