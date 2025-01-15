import adapter from '@sveltejs/adapter-node';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		adapter: adapter({
			// Optional: Specify the output directory (defaults to 'build')
			out: 'build',
			// Optional: Enable precompression of assets
			precompress: true,
			// Optional: Configure the port (defaults to 3000)
			envPrefix: 'APP_'
		})
	},
	preprocess: vitePreprocess()
};

export default config;
