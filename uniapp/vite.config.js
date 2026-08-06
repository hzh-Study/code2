import { defineConfig } from 'vite'
import uni from '@dcloudio/vite-plugin-uni'

const proxyTarget = process.env.VITE_PROXY_TARGET || 'http://localhost:8000'

export default defineConfig({
  plugins: [uni()],
  server: {
    host: '0.0.0.0',
    port: 5174,
    proxy: {
      '/api': { target: proxyTarget, changeOrigin: true },
      '/static': { target: proxyTarget, changeOrigin: true },
      '/images': { target: proxyTarget, changeOrigin: true }
    }
  }
})
