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

export interface AuthResponse {
    access_token: string;
    token_type: string;
}

export interface RegisterData {
    username: string;
    password: string;
    name?: string;
} 