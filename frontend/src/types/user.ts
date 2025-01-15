export enum UserRole {
    USER = "user",
    ADMIN = "admin"
}

export interface User {
    id: string;
    username: string;
    name: string | null;
    role: UserRole;
    created_at: string;
    is_active: boolean;
}

export interface LoginCredentials {
    username: string;
    password: string;
}

export interface RegisterData {
    username: string;
    password: string;
    name?: string;
}

export interface AuthResponse {
    access_token: string;
    token_type: string;
} 