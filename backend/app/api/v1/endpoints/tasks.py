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
        def sort_key(x):
            if x.deadline is None:
                return (True, None)
            # Convert to naive datetime if aware
            deadline = x.deadline.replace(tzinfo=None) if x.deadline.tzinfo else x.deadline
            return (False, deadline)

        return sorted(tasks, key=sort_key)

    async def create_task(
        self,
        task: TaskCreate,
        userinfo=Depends(user_check)
    ) -> Task:
        if not Projects.user_has_access(userinfo.id, task.project_id):
            raise HTTPException(
                status_code=403,
                detail="No access to this project"
            )

        try:
            created_task = Tasks.create_task(task, created_by=userinfo.id)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        # Check project status and update if needed
        project = Projects.get_project(task.project_id)
        if project.status == "completed":
            Projects.update_project_status(task.project_id, "in_progress")
            # Notify project members about project being reopened
            project_members = Projects.get_project_members(task.project_id)
            member_ids = [member.user_id for member in project_members]
            member_users = [Users.get_user_by_id(member_id) for member_id in member_ids]
            member_emails = [user.username for user in member_users]
            EmailService.notify_project_reopened(member_emails, project.name)

        # Send email notification if task is assigned
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
        current_task = Tasks.get_task(task_id)
        if not current_task:
            raise HTTPException(status_code=404, detail="Task not found")

        if not (userinfo.is_admin or
                Projects.is_project_manager(userinfo.id, current_task.project_id) or
                current_task.assigned_to_id == userinfo.id):
            raise HTTPException(status_code=403, detail="Not enough permissions")

        try:
            updated = Tasks.update_task(task_id, task)
            if not updated:
                raise HTTPException(status_code=404, detail="Task not found")

            # Check if we need to update project status
            if task.status:
                project_tasks = Tasks.get_project_tasks(current_task.project_id)
                all_completed = True
                has_in_progress = False

                for t in project_tasks:
                    if t.status != "completed":
                        all_completed = False
                    if t.status == "in_progress":
                        has_in_progress = True

                project = Projects.get_project(current_task.project_id)
                new_status = None

                if all_completed and project.status != "completed":
                    new_status = "completed"
                    # Get project members for notification
                    project_members = Projects.get_project_members(current_task.project_id)
                    member_ids = [member.user_id for member in project_members]
                    member_users = [Users.get_user_by_id(member_id) for member_id in member_ids]
                    member_emails = [user.username for user in member_users]
                    # Notify about project completion
                    EmailService.notify_project_completed(member_emails, project.name)
                elif has_in_progress:
                    new_status = "in_progress"

                if new_status:
                    Projects.update_project_status(current_task.project_id, new_status)

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

        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

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
