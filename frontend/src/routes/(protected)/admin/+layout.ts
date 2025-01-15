import { browser } from '$app/environment';
import { goto } from '$app/navigation';
import { user } from '$lib/stores/auth';
import { get } from 'svelte/store';

export const load = async () => {
    if (browser) {
        const currentUser = get(user);
        if (currentUser?.role !== 'admin') {
            goto('/dashboard');
        }
    }
}; 