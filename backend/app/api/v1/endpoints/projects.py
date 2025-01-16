from fastapi import Path, Body, HTTPException, status, Depends
from app.core.endpoints.endpoint import BaseEndpoint
from app.schemas.project import Project, ProjectCreate, ProjectUpdate, ProjectMember, ProjectMemberBase
from app.schemas.base import DefaultResponse
from app.services.authentication import admin_user_check, user_check
from app.db.relational import Projects
from typing import List
from app.schemas.users import UserRole
from app.services.email_service import EmailService
from app.db.relational import Users


class ProjectsEndpoint(BaseEndpoint):
    def __init__(self):
        super().__init__()

        self.router.get("/", response_model=List[Project])(self.get_projects)
        self.router.post("/", response_model=Project)(self.create_project)
        self.router.get("/{project_id}", response_model=Project)(self.get_project)
        self.router.put("/{project_id}", response_model=Project)(self.update_project)
        self.router.delete("/{project_id}", response_model=DefaultResponse)(self.delete_project)
        self.router.get("/{project_id}/members", response_model=List[ProjectMember])(self.get_project_members)
        self.router.post("/{project_id}/members", response_model=ProjectMember)(self.add_project_member)
        self.router.delete("/{project_id}/members/{user_id}",
                           response_model=DefaultResponse)(self.remove_project_member)

    async def get_project(self, project_id: str = Path(...), userinfo=Depends(user_check)) -> Project:
        if userinfo.role == UserRole.ADMIN:
            project = Projects.get_project(project_id)
        else:
            project = Projects.get_user_project(userinfo.id, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    async def get_projects(self, userinfo=Depends(user_check)) -> List[Project]:
        if userinfo.role == UserRole.ADMIN:
            return Projects.get_all_projects()
        return Projects.get_user_projects(userinfo.id)

    async def create_project(
        self,
        project: ProjectCreate = Body(...),
        userinfo=Depends(admin_user_check)
    ) -> Project:
        return Projects.create_project(project, creator_id=userinfo.id)

    async def update_project(
        self,
        project_id: str = Path(...),
        project: ProjectUpdate = Body(...),
        userinfo=Depends(admin_user_check)
    ) -> Project:
        updated = Projects.update_project(project_id, project)
        if not updated:
            raise HTTPException(status_code=404, detail="Project not found")
        return updated

    async def delete_project(
        self,
        project_id: str = Path(...),
        userinfo=Depends(admin_user_check)
    ) -> DefaultResponse:
        if Projects.delete_project(project_id):
            return DefaultResponse(code=200, result="Project deleted successfully")
        raise HTTPException(status_code=404, detail="Project not found")

    async def get_project_members(
        self,
        project_id: str = Path(...),
        userinfo=Depends(user_check)
    ) -> List[ProjectMember]:
        if not Projects.user_has_access(userinfo.id, project_id) and userinfo.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="No access to this project")
        return Projects.get_project_members(project_id)

    async def add_project_member(
        self,
        project_id: str = Path(...),
        member: ProjectMemberBase = Body(...),
        userinfo=Depends(user_check)
    ) -> ProjectMember:
        if not Projects.is_project_manager(userinfo.id, project_id) and userinfo.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Only project managers can add members")

        added_member = Projects.add_project_member(project_id, member)

        # Send email notification to the new member
        project = Projects.get_project(project_id)
        user = Users.get_user_by_id(member.user_id)
        project_url = f"/projects/{project_id}"

        EmailService.notify_project_assignment(
            user.username,
            project.name,
            project_url
        )

        return added_member

    async def remove_project_member(
        self,
        project_id: str = Path(...),
        user_id: str = Path(...),
        userinfo=Depends(user_check)
    ) -> DefaultResponse:
        if not Projects.is_project_manager(userinfo.id, project_id) and userinfo.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail="Only project managers can remove members")
        if Projects.remove_project_member(project_id, user_id):
            return DefaultResponse(code=200, result="Member removed successfully")
        raise HTTPException(status_code=404, detail="Member not found")
