import type { AuthResponse, RegisterData, User } from '$lib/types/user';
import type { Sample, SearchResult } from '$lib/types/sample';
import { env } from '$env/dynamic/public';
import type { Project, ProjectCreate, ProjectMember, Task, TaskCreate, GanttTask, Comment, CommentCreate } from '$lib/types/project';

const API_URL = import.meta.env.VITE_API_URL || env.PUBLIC_API_URL;

interface UserCreate {
    email: string;
    full_name: string;
    role?: string;
}

interface TaskCreate {
    name: string;
    description: string;
    project_id: string;
    start_date: string;
    deadline: string;
    assigned_to_id?: string | null;
    parent_task_id?: string | null;
}

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

    private async handleResponse(response: Response) {
        if (!response.ok) {
            const contentType = response.headers.get('content-type');
            let errorDetail;

            if (contentType?.includes('application/json')) {
                const errorData = await response.json();
                errorDetail = errorData.detail || JSON.stringify(errorData);
            } else {
                errorDetail = await response.text();
            }

            const error = new Error(errorDetail);
            error.response = response;
            throw error;
        }
        return response;
    }

    async login(email: string, password: string): Promise<AuthResponse> {
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);

        const response = await fetch(`${API_URL}/token`, {
            method: 'POST',
            body: formData,
        });

        await this.handleResponse(response);
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

        await this.handleResponse(response);
        return response.json();
    }

    async getCurrentUser(): Promise<User> {
        const response = await fetch(`${API_URL}/api/v1/userinfo/`, {
            headers: this.getHeaders(),
        });

        await this.handleResponse(response);
        return response.json();
    }

    // User management functions
    async getUsers(): Promise<User[]> {
        const response = await fetch(`${API_URL}/api/v1/users/`, {
            headers: this.getHeaders(),
        });

        await this.handleResponse(response);
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

    async getProjects(): Promise<Project[]> {
        const response = await fetch(`${API_URL}/api/v1/projects/`, {
            headers: this.getHeaders(),
        });

        await this.handleResponse(response);
        return response.json();
    }

    async createProject(project: ProjectCreate): Promise<Project> {
        const response = await fetch(`${API_URL}/api/v1/projects/`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(project),
        });

        await this.handleResponse(response);
        return response.json();
    }

    async updateProject(projectId: string, project: Partial<Project>): Promise<Project> {
        const response = await fetch(`${API_URL}/api/v1/projects/${projectId}`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify(project),
        });

        if (!response.ok) {
            throw new Error('Failed to update project');
        }

        return response.json();
    }

    async deleteProject(projectId: string): Promise<void> {
        const response = await fetch(`${API_URL}/api/v1/projects/${projectId}`, {
            method: 'DELETE',
            headers: this.getHeaders(),
        });

        if (!response.ok) {
            throw new Error('Failed to delete project');
        }
    }

    async getProjectMembers(projectId: string): Promise<ProjectMember[]> {
        const response = await fetch(`${API_URL}/api/v1/projects/${projectId}/members`, {
            headers: this.getHeaders(),
        });

        await this.handleResponse(response);
        return response.json();
    }

    async addProjectMember(projectId: string, userId: string, role: string): Promise<ProjectMember> {
        const response = await fetch(`${API_URL}/api/v1/projects/${projectId}/members`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify({ user_id: userId, role, project_id: projectId }),
        });

        await this.handleResponse(response);
        return response.json();
    }

    async removeProjectMember(projectId: string, userId: string): Promise<void> {
        const response = await fetch(`${API_URL}/api/v1/projects/${projectId}/members/${userId}`, {
            method: 'DELETE',
            headers: this.getHeaders(),
        });

        await this.handleResponse(response);
    }

    async getTasks(projectId?: string): Promise<Task[]> {
        const url = projectId
            ? `${API_URL}/api/v1/tasks/?project_id=${projectId}`
            : `${API_URL}/api/v1/tasks/`;

        const response = await fetch(url, {
            headers: this.getHeaders(),
        });

        await this.handleResponse(response);
        return response.json();
    }

    async createTask(task: TaskCreate): Promise<Task> {
        const response = await fetch(`${API_URL}/api/v1/tasks/`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(task),
        });

        await this.handleResponse(response);
        return response.json();
    }

    async updateTask(taskId: string, task: Partial<Task>): Promise<Task> {
        const response = await fetch(`${API_URL}/api/v1/tasks/${taskId}`, {
            method: 'PUT',
            headers: this.getHeaders(),
            body: JSON.stringify(task),
        });

        await this.handleResponse(response);
        return response.json();
    }

    async deleteTask(taskId: string): Promise<void> {
        const response = await fetch(`${API_URL}/api/v1/tasks/${taskId}`, {
            method: 'DELETE',
            headers: this.getHeaders(),
        });

        await this.handleResponse(response);
    }

    async getGanttChart(projectId: string): Promise<{ tasks: GanttTask[] }> {
        const response = await fetch(`${API_URL}/api/v1/gantt/${projectId}`, {
            headers: this.getHeaders(),
        });

        await this.handleResponse(response);
        return response.json();
    }

    async getProject(projectId: string): Promise<Project> {
        const response = await fetch(`${API_URL}/api/v1/projects/${projectId}`, {
            headers: this.getHeaders(),
        });

        await this.handleResponse(response);
        return response.json();
    }

    async getTaskComments(taskId: string): Promise<Comment[]> {
        const response = await fetch(`${API_URL}/api/v1/comments/${taskId}`, {
            headers: this.getHeaders(),
        });

        await this.handleResponse(response);
        return response.json();
    }

    async createComment(comment: CommentCreate): Promise<Comment> {
        const response = await fetch(`${API_URL}/api/v1/comments/`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(comment),
        });

        await this.handleResponse(response);
        return response.json();
    }

    async deleteComment(commentId: string): Promise<void> {
        const response = await fetch(`${API_URL}/api/v1/comments/${commentId}`, {
            method: 'DELETE',
            headers: this.getHeaders(),
        });

        await this.handleResponse(response);
    }

    async getTask(taskId: string): Promise<Task> {
        const response = await fetch(`${API_URL}/api/v1/tasks/${taskId}`, {
            headers: this.getHeaders(),
        });

        await this.handleResponse(response);
        return response.json();
    }

    async createUser(userData: UserCreate): Promise<User> {
        const response = await fetch(`${API_URL}/api/v1/users/`, {
            method: 'POST',
            headers: this.getHeaders(),
            body: JSON.stringify(userData),
        });

        await this.handleResponse(response);
        return response.json();
    }

    async createSubtask(parentTaskId: string, task: Omit<TaskCreate, 'parent_task_id'>): Promise<Task> {
        return this.createTask({
            ...task,
            parent_task_id: parentTaskId
        });
    }
}

export const api = new ApiService(); 