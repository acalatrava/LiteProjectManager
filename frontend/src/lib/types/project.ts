export interface Project {
    id: string;
    name: string;
    description: string;
    status: string;
    start_date: string;
    deadline: string;
    tasks?: Task[];
    members?: ProjectMember[];
}

export interface ProjectCreate {
    name: string;
    description: string;
    start_date: string;
    deadline: string;
}

export interface ProjectMember {
    id: string;
    user_id: string;
    project_id: string;
    role: string;
    name?: string;
    email?: string;
}

export interface Task {
    id: string;
    name: string;
    description: string;
    project_id: string;
    parent_task_id?: string;
    start_date: string;
    deadline: string;
    assigned_to_id?: string;
    created_by_id: string;
    status: 'pending' | 'in_progress' | 'completed';
    created_at: string;
    updated_at: string;
    subtasks?: Task[];
}

export interface TaskCreate {
    name: string;
    description: string;
    project_id: string;
    start_date: string;
    deadline: string;
    assigned_to_id?: string | null;
}

export interface GanttTask {
    id: string;
    name: string;
    start: string;
    end: string;
    progress: number;
    dependencies?: string[];
}

export interface Comment {
    id: string;
    task_id: string;
    user_id: string;
    content: string;
    created_at: string;
    updated_at: string;
}

export interface CommentCreate {
    task_id: string;
    content: string;
} 