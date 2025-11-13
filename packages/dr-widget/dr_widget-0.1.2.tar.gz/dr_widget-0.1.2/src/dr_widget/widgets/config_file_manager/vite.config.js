import path from 'node:path';
import { defineConfig } from 'vite';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import react from '@vitejs/plugin-react-swc';

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    svelte({ compilerOptions: { runes: true } }),
    react(),
  ],
  define: {
    'process.env.NODE_ENV': '"production"',
  },
  resolve: {
    alias: {
      $lib: path.resolve('./src/lib')
    }
  },
  build: {
    lib: {
      entry: 'src/index.js',
      formats: ['es'],
      fileName: 'index'
    },
    outDir: 'static',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        inlineDynamicImports: true,
        entryFileNames: 'index.js',
        assetFileNames: '[name][extname]'
      }
    }
  }
});
