import { writable } from 'svelte/store';
import { browser } from '$app/environment';
import type { User } from '$lib/types/user';

export const user = writable<User | null>(null);
export const passwordResetRequired = writable<boolean>(false);
export const isAuthenticated = () => {
    if (!browser) return false;
    return localStorage.getItem('token') !== null;
};