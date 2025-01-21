import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
    plugins: [sveltekit()],
    optimizeDeps: {
        exclude: ['devalue']  // Exclude devalue from optimization
    },
    server: {
        proxy: {
            // Proxy API requests to your backend server
            '/api': {
                target: 'http://localhost:8000',
                changeOrigin: true
            }
        }
    }
});