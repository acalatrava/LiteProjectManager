import { browser } from '$app/environment';
import { goto } from '$app/navigation';
import { isAuthenticated } from '$lib/stores/auth';
import { get } from 'svelte/store';

export const load = async () => {
    if (browser) {
        if (!isAuthenticated()) {
            goto('/login');
        }
    }
}; 