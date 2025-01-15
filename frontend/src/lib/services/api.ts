import type { AuthResponse, RegisterData, User } from '$lib/types/user';
import type { Sample, SearchResult } from '$lib/types/sample';
import { env } from '$env/dynamic/public';

const API_URL = import.meta.env.VITE_API_URL || env.PUBLIC_API_URL;

class ApiService {
    private getHeaders(includeAuth = true): HeadersInit {
        const headers: HeadersInit = {
            'Content-Type': 'application/json',
        };

        if (includeAuth) {
            const token = localStorage.getItem('token');
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
        }

        return headers;
    }

    async login(email: string, password: string): Promise<AuthResponse> {
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);

        const response = await fetch(`${API_URL}/token`, {
            method: 'POST',
            body: formData,
        });

        if (!response.ok) {
            throw new Error('Login failed');
        }

        return response.json();
    }

    async register(data: RegisterData): Promise<AuthResponse> {
        const response = await fetch(`${API_URL}/signup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            throw new Error('Registration failed');
        }

        return response.json();
    }

    async getCurrentUser(): Promise<User> {
        const response = await fetch(`${API_URL}/api/v1/userinfo/`, {
            headers: this.getHeaders(),
        });

        if (!response.ok) {
            throw new Error('Failed to get user info');
        }

        return response.json();
    }

    // User management functions
    async getUsers(): Promise<User[]> {
        const response = await fetch(`${API_URL}/api/v1/users/`, {
            headers: this.getHeaders(),
        });

        if (!response.ok) {
            throw new Error('Failed to get users');
        }

        return response.json();
    }

    async updateUser(userId: string, data: Partial<User>): Promise<User> {
        const response = await fetch(`${API_URL}/api/v1/users/${userId}`, {
            method: 'PATCH',
            headers: this.getHeaders(),
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            throw new Error('Failed to update user');
        }

        return response.json();
    }

    async deleteUser(userId: string): Promise<void> {
        const response = await fetch(`${API_URL}/api/v1/users/${userId}`, {
            method: 'DELETE',
            headers: this.getHeaders(),
        });

        if (!response.ok) {
            throw new Error('Failed to delete user');
        }
    }

    // Sample management
    async getSamples(): Promise<Sample[]> {
        const response = await fetch(`${API_URL}/api/v1/sample/`, {
            headers: this.getHeaders(),
        });

        if (!response.ok) {
            throw new Error('Failed to get samples');
        }

        const data = await response.json();
        return data.results;
    }

    async addSample(info: string): Promise<void> {
        const response = await fetch(`${API_URL}/api/v1/sample/`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify({ info }),
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to add sample');
        }
    }

    async deleteSample(id: string): Promise<void> {
        const response = await fetch(`${API_URL}/api/v1/sample/${id}`, {
            method: 'DELETE',
            headers: this.getHeaders(),
        });

        if (!response.ok) {
            throw new Error('Failed to delete sample');
        }
    }

    // Search functionality
    async search(query: string): Promise<SearchResult[]> {
        const response = await fetch(`${API_URL}/api/v1/search/?q=${encodeURIComponent(query)}`, {
            headers: this.getHeaders(),
        });

        if (!response.ok) {
            throw new Error('Search failed');
        }

        const data = await response.json();
        return data.results;
    }

    async updateCurrentUser(data: Partial<User>): Promise<User> {
        const response = await fetch(`${API_URL}/api/v1/userinfo/`, {
            method: 'PATCH',
            headers: this.getHeaders(),
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            throw new Error('Failed to update profile');
        }

        return response.json();
    }
}

export const api = new ApiService(); 