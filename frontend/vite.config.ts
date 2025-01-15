import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		proxy: {
			'/api': {
				target: 'http://192.168.1.111:8000',
				changeOrigin: true
			},
			'/token': {
				target: 'http://192.168.1.111:8000',
				changeOrigin: true
			},
			'/signup': {
				target: 'http://192.168.1.111:8000',
				changeOrigin: true
			}
		}
	}
});
