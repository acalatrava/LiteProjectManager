from fastapi import Path, Body, HTTPException, status, Depends, Query
from app.core.endpoints.endpoint import BaseEndpoint
from app.schemas.task import Task, TaskCreate, TaskUpdate
from app.schemas.base import DefaultResponse
from app.services.authentication import user_check
from app.db.relational import Tasks, Projects, Users
from typing import List
from app.services.email_service import EmailService
from app.core.config import SERVER_URL


class TasksEndpoint(BaseEndpoint):
    def __init__(self):
        super().__init__()

        self.router.get("/", response_model=List[Task])(self.get_tasks)
        self.router.post("/", response_model=Task)(self.create_task)
        self.router.put("/{task_id}", response_model=Task)(self.update_task)
        self.router.get("/{task_id}", response_model=Task)(self.get_task)
        self.router.delete("/{task_id}", response_model=DefaultResponse)(self.delete_task)

    async def get_task(self, task_id: str = Path(...), userinfo=Depends(user_check)) -> Task:
        task = Tasks.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Check if user is admin or member of the project
        if not (userinfo.is_admin or Projects.is_project_member(userinfo.id, task.project_id)):
            raise HTTPException(
                status_code=403,
                detail="You don't have access to this task"
            )

        return task

    async def get_tasks(self, project_id: str = Query(...), userinfo=Depends(user_check)) -> List[Task]:
        if userinfo.is_admin:
            tasks = Tasks.get_all_tasks(project_id)
        else:
            tasks = Tasks.get_user_tasks(userinfo.id, project_id)

        # Sort tasks by deadline, None values go last
        return sorted(tasks, key=lambda x: (x.deadline is None, x.deadline or ""))

    async def create_task(
        self,
        task: TaskCreate = Body(...),
        userinfo=Depends(user_check)
    ) -> Task:
        # Check if user has project manager role
        if not Projects.is_project_manager(userinfo.id, task.project_id):
            raise HTTPException(
                status_code=403,
                detail="Only project managers can create tasks"
            )

        Projects.update_project_status(task.project_id, "in_progress")

        created_task = Tasks.create_task(task, created_by=userinfo.id)

        # Send email if task is assigned to someone
        if created_task.assigned_to_id:
            assigned_user = Users.get_user_by_id(created_task.assigned_to_id)
            project = Projects.get_project(created_task.project_id)
            task_url = f"{SERVER_URL}/projects/{created_task.project_id}/tasks/{created_task.id}"
            EmailService.notify_task_assignment(
                assigned_user.username,
                created_task.name,
                project.name,
                task_url
            )

        return created_task

    async def update_task(
        self,
        task_id: str = Path(...),
        task: TaskUpdate = Body(...),
        userinfo=Depends(user_check)
    ) -> Task:
        if userinfo.is_admin:
            current_task = Tasks.get_task(task_id)
        else:
            current_task = Tasks.get_user_task(userinfo.id, task_id)
        if not current_task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Check permissions
        if not (userinfo.is_admin or
                Projects.is_project_manager(userinfo.id, current_task.project_id) or
                current_task.assigned_to_id == userinfo.id):
            raise HTTPException(status_code=403, detail="Not enough permissions")

        updated = Tasks.update_task(task_id, task)
        if not updated:
            raise HTTPException(status_code=404, detail="Task not found")

        # Handle task assignment notification
        if task.assigned_to_id and task.assigned_to_id != current_task.assigned_to_id:
            assigned_user = Users.get_user_by_id(task.assigned_to_id)
            project = Projects.get_project(current_task.project_id)
            task_url = f"{SERVER_URL}/projects/{current_task.project_id}/tasks/{task_id}"
            EmailService.notify_task_assignment(
                assigned_user.username,
                updated.name,
                project.name,
                task_url
            )

        # Handle task completion notification
        if task.status == "completed" and current_task.status != "completed":
            project = Projects.get_project(current_task.project_id)
            project_members = Projects.get_project_members(current_task.project_id)
            member_ids = [member.user_id for member in project_members]
            member_users = [Users.get_user_by_id(member_id) for member_id in member_ids]
            member_emails = [user.username for user in member_users]

            # Notify about task completion
            EmailService.notify_task_completed(
                member_emails,
                updated.name,
                project.name,
                userinfo.name or userinfo.username
            )

            # Check if all tasks are completed
            project_tasks = Tasks.get_project_tasks(current_task.project_id)
            if all(t.status == "completed" for t in project_tasks):
                Projects.update_project_status(current_task.project_id, "completed")
                # Notify about project completion
                EmailService.notify_project_completed(member_emails, project.name)

        return updated

    async def delete_task(
        self,
        task_id: str = Path(...),
        userinfo=Depends(user_check)
    ) -> DefaultResponse:
        task = Tasks.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Check if user has project manager role
        if not (userinfo.is_admin or
                Projects.is_project_manager(userinfo.id, task.project_id)):
            raise HTTPException(
                status_code=403,
                detail="Only admins and project managers can delete tasks"
            )

        if Tasks.delete_task(task_id):
            return DefaultResponse(code=200, result="Task deleted successfully")
        raise HTTPException(status_code=404, detail="Task not found")
