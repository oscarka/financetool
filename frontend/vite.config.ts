import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd())
  const allowedHosts = env.VITE_ALLOWED_HOSTS
    ? env.VITE_ALLOWED_HOSTS.split(',').map(h => h.trim())
    : []

  return {
    plugins: [react()],
    server: {
      proxy: {
        '/api': {
          target: 'https://backend-production-2750.up.railway.app',
          changeOrigin: true,
          secure: true,
        }
      }
    },
    preview: {
      host: true,
      port: 8080,
      allowedHosts
    }
  }
})
