import axios from 'axios';
import type { AuthResponse, LoginCredentials, RegisterData, User } from '../types/user';

const API_URL = process.env.REACT_APP_API_URL || 'http://192.168.1.111:8000';

const api = axios.create({
    baseURL: API_URL,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export const authApi = {
    login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
        const formData = new FormData();
        formData.append('username', credentials.username);
        formData.append('password', credentials.password);
        const { data } = await api.post<AuthResponse>('/token', formData);
        return data;
    },

    register: async (userData: RegisterData): Promise<AuthResponse> => {
        const { data } = await api.post<AuthResponse>('/signup', userData);
        return data;
    },

    getCurrentUser: async (): Promise<User> => {
        const { data } = await api.get<User>('/api/v1/userinfo/');
        return data;
    },
};

export const userApi = {
    getUsers: async (): Promise<User[]> => {
        const { data } = await api.get<User[]>('/api/v1/users/');
        return data;
    },

    getUser: async (id: string): Promise<User> => {
        const { data } = await api.get<User>(`/api/v1/users/${id}`);
        return data;
    },

    updateUser: async (id: string, userData: Partial<User>): Promise<User> => {
        const { data } = await api.patch<User>(`/api/v1/users/${id}`, userData);
        return data;
    },

    deleteUser: async (id: string): Promise<void> => {
        await api.delete(`/api/v1/users/${id}`);
    },
}; 