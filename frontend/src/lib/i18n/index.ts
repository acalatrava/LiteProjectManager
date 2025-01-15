import { browser } from '$app/environment';
import { init, register, waitLocale } from 'svelte-i18n';

const defaultLocale = 'en';

register('en', () => import('./locales/en.json'));
register('es', () => import('./locales/es.json'));

init({
    fallbackLocale: defaultLocale,
    initialLocale: browser ? window.navigator.language.split('-')[0] : defaultLocale,
});

// Wait for locale data to be loaded
if (browser) {
    waitLocale();
} 