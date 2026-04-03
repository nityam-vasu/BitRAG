import { defineConfig } from 'vite'
import path from 'path'
import react from '@vitejs/plugin-react'

// Get port from environment or use default
const frontendPort = process.env.FRONTEND_PORT || '5173'
const apiProxyTarget = process.env.API_PROXY_TARGET || 'http://localhost:5000'

export default defineConfig({
  plugins: [
    // React plugin for Make - Tailwind is handled via PostCSS
    react(),
  ],
  resolve: {
    alias: {
      // Alias @ to the src directory
      '@': path.resolve(__dirname, './src'),
    },
  },
  
  // File types to support raw imports. Never add .css, .tsx, or .ts files to this.
  assetsInclude: ['**/*.svg', '**/*.csv'],
  
  // Server configuration
  server: {
    port: parseInt(frontendPort),
    strictPort: false,
    host: '0.0.0.0',
    proxy: {
      '/api': {
        target: apiProxyTarget,
        changeOrigin: true,
        secure: false,
      },
    },
  },
  
  // Build configuration
  build: {
    outDir: 'dist',
    emptyOutDir: true,
  },
})
