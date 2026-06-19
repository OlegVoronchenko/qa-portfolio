import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  base: '/qa-portfolio/',
  plugins: [react()],
  build: {
    outDir: 'dist',
  },
})
