import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Custom plugin to add COOP header for Firebase Auth (only for HTML responses)
// COOP: same-origin-allow-popups allows popup windows for OAuth flows
const coopHeaderPlugin = {
  name: 'coop-header-plugin',
  configureServer(server) {
    return () => {
      server.middlewares.use((req, res, next) => {
        // Only add COOP header for HTML requests, not API/JSON responses
        if (!req.url.includes('/api') && !req.url.match(/\.(js|css|json|png|jpg|svg)$/)) {
          const originalSend = res.send;
          res.send = function (data) {
            res.setHeader('Cross-Origin-Opener-Policy', 'same-origin-allow-popups');
            return originalSend.call(this, data);
          };
        }
        next();
      });
    };
  },
};

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), coopHeaderPlugin],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '/api')
      }
    }
  },
  build: {
    // Code-splitting strategy: separate vendor and route chunks
    rollupOptions: {
      output: {
        manualChunks: {
          // Vendor chunks
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          'vendor-ui': ['react-hot-toast', 'react-markdown'],
          'vendor-firebase': ['firebase'],
          'vendor-chart': ['chart.js', 'react-chartjs-2'],
          // Feature chunks
          'auth': ['./src/pages/auth'],
          'dashboard': ['./src/pages/dashboard'],
          'admin': ['./src/pages/admin'],
        },
        entryFileNames: 'assets/[name]-[hash].js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash][extname]',
      },
    },
    // Target modern browsers only for smaller builds
    target: 'esnext',
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // Remove console logs in production
      },
    },
  },
})
