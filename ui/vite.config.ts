import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173, // Optional: only used for local dev
  },
  build: {
    outDir: 'dist',
    sourcemap: true, // Optional: helpful for debugging deployed builds
  },
  resolve: {
    extensions: ['.js', '.ts', '.jsx', '.tsx'], // Ensures module resolution for TypeScript
  },
});
