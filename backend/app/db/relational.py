from datetime import datetime, timedelta
import hashlib
import re
import uuid
from typing import List, Optional
from playhouse.shortcuts import model_to_dict

from app.models.user import User
from app.schemas.users import UserRole, UserInDB
from .database import DB, get_db
from app.models.auth_token import AuthToken
from app.core.config import AUTH_TOKEN_LIFETIME
from app.models.project import Project as ProjectModel, ProjectMember as ProjectMemberModel
from app.models.task import Task as TaskModel
from app.schemas.project import (
    ProjectCreate,
    ProjectUpdate,
    Project as ProjectSchema,
    ProjectMember as ProjectMemberSchema,
    ProjectMemberBase
)
from app.schemas.task import TaskCreate, TaskUpdate, Task as TaskSchema
from app.models.comment import Comment as CommentModel
from app.schemas.comment import CommentCreate, Comment as CommentSchema


class UsersTable:
    def __init__(self):
        with get_db():
            DB.create_tables([User, AuthToken])

    def insert_new_user(
        self, username: str, password: str, role: str = UserRole.USER.value, name: str = ''
    ) -> Optional[UserInDB]:
        # Set username to lowercase
        username = username.lower()

        # Check username is a valid email using regex
        if not re.match(r"[^@]+@[^@]+\.[^@]+", username):
            return None

        # Check if the username already exists
        if self.get_user_by_username(username):
            return None

        try:
            # Generate a random salt
            salt = str(uuid.uuid4())

            # Encrypt the password using sha256 and the salt
            password = hashlib.sha256((salt + password).encode()).hexdigest()

            # Generate an id from the username
            id = str(uuid.uuid5(namespace=uuid.NAMESPACE_OID, name=username.lower()))

            # Generate a token based on id and random string
            token = hashlib.sha256((id + str(uuid.uuid4())).encode()).hexdigest()

            # Check if this is the first user
            is_first_user = self.get_num_users() == 0

            # Create new user with admin role if it's the first user
            user = User.create(
                id=id,
                token=token,
                username=username.lower(),
                password=password,
                salt=salt,
                role=UserRole.ADMIN.value if is_first_user else UserRole.USER.value,
                name=name,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

            return UserInDB(**user.to_dict())
        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    def get_user_by_id(self, id: str) -> Optional[UserInDB]:
        try:
            user = User.get(User.id == id)
            return UserInDB(**user.to_dict())
        except User.DoesNotExist:
            return None

    def get_user_by_token(self, token: str) -> Optional[UserInDB]:
        try:
            # Get valid token
            auth_token = (AuthToken
                          .select()
                          .where(
                              (AuthToken.token == token) &
                              (AuthToken.is_active == True) &
                              (AuthToken.expires_at > datetime.now())
                          )
                          .first())

            if not auth_token:
                return None

            user = User.get(User.id == auth_token.user_id)
            return UserInDB(**user.to_dict())
        except Exception as e:
            print(f"Error getting user by token: {e}")
            return None

    def is_admin(self, token: str) -> bool:
        # Get user by token
        try:
            user = self.get_user_by_token(token)
            return user.role == UserRole.ADMIN.value
        except:
            return False

    def user_id_is_admin(self, user_id: str) -> bool:
        user = User.get(User.id == user_id)
        return user.role == UserRole.ADMIN.value

    def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        try:
            user = User.get(User.username == username.lower())
            return UserInDB(**user.to_dict())
        except:
            return None

    def get_user_by_username_and_password(self, username: str, password: str) -> Optional[tuple[UserInDB, str]]:
        # Set username to lowercase
        username = username.lower()

        # Check username format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", username):
            return None

        try:
            # Get user and verify password
            user = User.get(User.username == username.lower())
            hashed_password = hashlib.sha256((user.salt + password).encode()).hexdigest()

            if user.password != hashed_password:
                return None

            # Create new auth token
            token = self.create_auth_token(user.id)
            if not token:
                return None

            return UserInDB(**user.to_dict()), token

        except Exception as e:
            return None

    def get_users(self, skip: int = 0, limit: int = 50) -> List[UserInDB]:
        return [
            UserInDB.model_validate(user)
            for user in User.select().limit(limit).offset(skip)
        ]

    def get_num_users(self) -> Optional[int]:
        return User.select().count()

    def update_user_role_by_id(self, id: str, role: str) -> Optional[UserInDB]:
        try:
            query = User.update(role=role).where(User.id == id)
            query.execute()

            user = User.get(User.id == id)
            return UserInDB(**model_to_dict(user))
        except:
            return None

    def update_user_by_id(self, id: str, updated: dict) -> Optional[UserInDB]:
        try:
            # If changing password, generate new salt and hash
            if 'password' in updated:
                salt = str(uuid.uuid4())
                updated['password'] = hashlib.sha256((salt + updated['password']).encode()).hexdigest()
                updated['salt'] = salt

            # Update user
            query = User.update(**updated).where(User.id == id)
            query.execute()

            user = User.get(User.id == id)
            return UserInDB.model_validate(user)
        except Exception as e:
            print(f"Error updating user: {e}")
            return None

    def delete_user_by_id(self, id: str) -> bool:
        try:
            # Delete associated auth tokens first
            AuthToken.delete().where(AuthToken.user_id == id).execute()

            # Then delete the user
            query = User.delete().where(User.id == id)
            query.execute()

            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False

    def update_user_role(self, user_id: str, new_role: UserRole) -> Optional[UserInDB]:
        try:
            user = User.get(User.id == user_id)
            user.role = new_role
            user.updated_at = datetime.now()
            user.save()
            return UserInDB(**user.to_dict())
        except User.DoesNotExist:
            return None

    def get_active_users(self, skip: int = 0, limit: int = 50) -> List[UserInDB]:
        return [
            UserInDB.model_validate(user)
            for user in User.select()
            .where(User.is_active == True)
            .limit(limit)
            .offset(skip)
        ]

    def get_all_users(self, skip: int = 0, limit: int = 50) -> List[UserInDB]:
        return [
            UserInDB.model_validate(user)
            for user in User.select().limit(limit).offset(skip)
        ]

    def verify_password(self, username: str, password: str) -> bool:
        try:
            user = User.get(User.username == username.lower())
            # Encrypt the password using sha256 and the user's salt
            hashed_password = hashlib.sha256((user.salt + password).encode()).hexdigest()
            return user.password == hashed_password
        except User.DoesNotExist:
            return False

    def create_auth_token(self, user_id: str) -> Optional[str]:
        try:
            # Generate new token
            token = hashlib.sha256((str(uuid.uuid4()) + str(datetime.now())).encode()).hexdigest()

            # Calculate expiration
            expires_at = datetime.now() + timedelta(seconds=int(AUTH_TOKEN_LIFETIME))

            # Create token record
            AuthToken.create(
                id=str(uuid.uuid4()),
                user_id=user_id,
                token=token,
                expires_at=expires_at
            )

            return token
        except Exception as e:
            print(f"Error creating auth token: {e}")
            return None

    def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get a user by their email address"""
        try:
            user = User.get(User.username == email)
            return UserInDB.model_validate(user)
        except User.DoesNotExist:
            return None


class ProjectsTable:
    def __init__(self):
        with get_db():
            DB.create_tables([ProjectModel, ProjectMemberModel])

    def create_project(self, project: ProjectCreate, creator_id: str) -> ProjectSchema:
        project_id = str(uuid.uuid4())
        project_db = ProjectModel.create(
            id=project_id,
            name=project.name,
            description=project.description,
            start_date=project.start_date,
            deadline=project.deadline,
            status='pending',
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        # Add creator as project manager
        ProjectMemberModel.create(
            id=str(uuid.uuid4()),
            project_id=project_id,
            user_id=creator_id,
            role='project_manager',
            created_at=datetime.now()
        )

        return ProjectSchema.model_validate({
            "id": project_db.id,
            "name": project_db.name,
            "description": project_db.description,
            "start_date": project_db.start_date,
            "deadline": project_db.deadline,
            "status": project_db.status,
            "created_at": project_db.created_at,
            "updated_at": project_db.updated_at,
            "is_active": project_db.is_active
        })

    def update_project(self, project_id: str, project_update: ProjectUpdate) -> Optional[ProjectSchema]:
        try:
            project = ProjectModel.get(ProjectModel.id == project_id)
            project.name = project_update.name
            project.description = project_update.description
            project.start_date = project_update.start_date
            project.deadline = project_update.deadline
            if project_update.status:
                project.status = project_update.status
            project.updated_at = datetime.now()
            project.save()
            return ProjectSchema.model_validate({
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "start_date": project.start_date,
                "deadline": project.deadline,
                "status": project.status,
                "created_at": project.created_at,
                "updated_at": project.updated_at,
                "is_active": project.is_active
            })
        except ProjectModel.DoesNotExist:
            return None

    def update_project_status(self, project_id: str, status: str):
        try:
            project = ProjectModel.get(ProjectModel.id == project_id)
            project.status = status
            project.updated_at = datetime.now()
            project.save()
            return True
        except ProjectModel.DoesNotExist:
            return False

    def delete_project(self, project_id: str) -> bool:
        try:
            # Delete associated tasks first
            TaskModel.delete().where(TaskModel.project_id == project_id).execute()
            # Delete project members
            ProjectMemberModel.delete().where(ProjectMemberModel.project_id == project_id).execute()
            # Delete project
            ProjectModel.delete().where(ProjectModel.id == project_id).execute()
            return True
        except:
            return False

    def get_all_projects(self) -> List[ProjectSchema]:
        projects = ProjectModel.select()
        result = []

        for p in projects:
            # Get tasks for this project
            tasks = [
                TaskSchema.model_validate(task.to_dict())
                for task in TaskModel.select().where(TaskModel.project_id == p.id)
            ]

            # Create project schema with tasks
            project = ProjectSchema.model_validate({
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "start_date": p.start_date,
                "deadline": p.deadline,
                "status": p.status,
                "created_at": p.created_at,
                "updated_at": p.updated_at,
                "is_active": p.is_active,
                "tasks": tasks  # Include tasks in project data
            })
            result.append(project)

        return result

    def get_user_projects(self, user_id: str) -> List[ProjectSchema]:
        project_members = ProjectMemberModel.select().where(ProjectMemberModel.user_id == user_id)
        result = []

        for pm in project_members:
            # Get tasks for this project
            tasks = [
                TaskSchema.model_validate(task.to_dict())
                for task in TaskModel.select().where(TaskModel.project_id == pm.project.id)
            ]

            # Create project schema with tasks
            project = ProjectSchema.model_validate({
                "id": pm.project.id,
                "name": pm.project.name,
                "description": pm.project.description,
                "start_date": pm.project.start_date,
                "deadline": pm.project.deadline,
                "status": pm.project.status,
                "created_at": pm.project.created_at,
                "updated_at": pm.project.updated_at,
                "is_active": pm.project.is_active,
                "tasks": tasks  # Include tasks in project data
            })
            result.append(project)

        return result

    def get_project(self, project_id: str) -> Optional[ProjectSchema]:
        try:
            project = ProjectModel.get(ProjectModel.id == project_id)
            return ProjectSchema.model_validate(project.to_dict())
        except ProjectModel.DoesNotExist:
            return None

    def get_user_project(self, user_id: str, project_id: str) -> Optional[ProjectSchema]:
        try:
            project = ProjectModel.get(ProjectModel.id == project_id)
            return ProjectSchema.model_validate(project.to_dict())
        except ProjectModel.DoesNotExist:
            return None

    def is_project_manager(self, user_id: str, project_id: str) -> bool:
        try:
            member = ProjectMemberModel.get(
                (ProjectMemberModel.user_id == user_id) &
                (ProjectMemberModel.project_id == project_id)
            )
            return member.role == 'project_manager'
        except ProjectMemberModel.DoesNotExist:
            return False

    def user_has_access(self, user_id: str, project_id: str) -> bool:
        # Check if user is admin
        if Users.user_id_is_admin(user_id):
            return True

        return ProjectMemberModel.select().where(
            (ProjectMemberModel.user_id == user_id) &
            (ProjectMemberModel.project_id == project_id)
        ).exists()

    def get_project_members(self, project_id: str) -> List[ProjectMemberSchema]:
        return [
            ProjectMemberSchema.model_validate({
                "id": pm.id,
                "project_id": pm.project_id,
                "user_id": pm.user_id,
                "role": pm.role,
                "created_at": pm.created_at
            })
            for pm in ProjectMemberModel.select().where(ProjectMemberModel.project_id == project_id)
        ]

    def add_project_member(self, project_id: str, member: ProjectMemberBase) -> ProjectMemberSchema:
        member_db = ProjectMemberModel.create(
            id=str(uuid.uuid4()),
            project_id=project_id,
            user_id=member.user_id,
            role=member.role,
            created_at=datetime.now()
        )
        return ProjectMemberSchema.model_validate({
            "id": member_db.id,
            "project_id": member_db.project_id,
            "user_id": member_db.user_id,
            "role": member_db.role,
            "created_at": member_db.created_at
        })

    def remove_project_member(self, project_id: str, user_id: str) -> bool:
        try:
            ProjectMemberModel.delete().where(
                (ProjectMemberModel.project_id == project_id) &
                (ProjectMemberModel.user_id == user_id)
            ).execute()
            return True
        except:
            return False

    def is_project_member(self, user_id: str, project_id: str) -> bool:
        return ProjectMemberModel.select().where(
            (ProjectMemberModel.user_id == user_id) &
            (ProjectMemberModel.project_id == project_id)
        ).exists()


class TasksTable:
    def __init__(self):
        with get_db():
            DB.create_tables([TaskModel])

    def create_task(self, task: TaskCreate, created_by: str) -> TaskSchema:
        task_id = str(uuid.uuid4())
        task_db = TaskModel.create(
            id=task_id,
            parent_task_id=task.parent_task_id,
            project_id=task.project_id,
            name=task.name,
            description=task.description,
            start_date=task.start_date,
            deadline=task.deadline,
            created_by_id=created_by,
            assigned_to_id=task.assigned_to_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        return TaskSchema.model_validate({
            "id": task_db.id,
            "name": task_db.name,
            "description": task_db.description,
            "project_id": task_db.project_id,
            "start_date": task_db.start_date,
            "deadline": task_db.deadline,
            "assigned_to_id": task_db.assigned_to_id,
            "created_by_id": task_db.created_by_id,
            "status": task_db.status,
            "created_at": task_db.created_at,
            "updated_at": task_db.updated_at,
            "parent_task_id": task_db.parent_task_id.id if task_db.parent_task_id else None,
            "subtasks": []
        })

    def update_task(self, task_id: str, task_update: TaskUpdate) -> Optional[TaskSchema]:
        try:
            task = TaskModel.get(TaskModel.id == task_id)
            update_data = task_update.model_dump(exclude_unset=True)

            # Check if trying to set status to completed
            if update_data.get('status') == 'completed':
                # Check if all subtasks are completed
                incomplete_subtasks = task.get_subtasks().where(
                    TaskModel.status != 'completed'
                ).count()
                if incomplete_subtasks > 0:
                    raise ValueError("Cannot complete task: there are incomplete subtasks")

            for field, value in update_data.items():
                setattr(task, field, value)

            task.updated_at = datetime.now()
            task.save()
            return TaskSchema.model_validate({
                "id": task.id,
                "name": task.name,
                "description": task.description,
                "project_id": task.project_id,
                "start_date": task.start_date,
                "deadline": task.deadline,
                "assigned_to_id": task.assigned_to_id,
                "created_by_id": task.created_by_id,
                "status": task.status,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "parent_task_id": task.parent_task_id.id if task.parent_task_id else None,
                "subtasks": [
                    {
                        **st.to_dict(),
                        "parent_task_id": st.parent_task_id.id if st.parent_task_id else None
                    } for st in task.get_subtasks()
                ]
            })
        except TaskModel.DoesNotExist:
            return None

    def delete_task(self, task_id: str) -> bool:
        try:
            TaskModel.delete().where(TaskModel.id == task_id).execute()
            return True
        except:
            return False

    def get_task(self, task_id: str) -> Optional[TaskSchema]:
        try:
            task = TaskModel.get(TaskModel.id == task_id)
            task_dict = {
                "id": task.id,
                "name": task.name,
                "description": task.description,
                "project_id": task.project_id,
                "start_date": task.start_date,
                "deadline": task.deadline,
                "assigned_to_id": task.assigned_to_id,
                "created_by_id": task.created_by_id,
                "status": task.status,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "parent_task_id": task.parent_task_id.id if task.parent_task_id else None
            }
            subtasks = [
                TaskSchema.model_validate({
                    **st.to_dict(),
                    "parent_task_id": st.parent_task_id.id if st.parent_task_id else None
                })
                for st in task.get_subtasks()
            ]
            task_dict["subtasks"] = subtasks
            return TaskSchema.model_validate(task_dict)
        except TaskModel.DoesNotExist:
            return None

    def get_user_task(self, user_id: str, task_id: str) -> Optional[TaskSchema]:
        try:
            task = TaskModel.get(
                (TaskModel.id == task_id) &
                (TaskModel.assigned_to_id == user_id)
            )
            return TaskSchema.model_validate({
                "id": task.id,
                "name": task.name,
                "description": task.description,
                "project_id": task.project_id,
                "start_date": task.start_date,
                "deadline": task.deadline,
                "assigned_to_id": task.assigned_to_id,
                "created_by_id": task.created_by_id,
                "status": task.status,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "parent_task_id": task.parent_task_id.id if task.parent_task_id else None
            })
        except TaskModel.DoesNotExist:
            return None

    def get_all_tasks(self, project_id: str) -> List[TaskSchema]:
        return [
            TaskSchema.model_validate({
                "id": t.id,
                "parent_task_id": t.parent_task_id.id if t.parent_task_id else None,
                "name": t.name,
                "description": t.description,
                "project_id": t.project_id,
                "start_date": t.start_date,
                "deadline": t.deadline,
                "assigned_to_id": t.assigned_to_id,
                "created_by_id": t.created_by_id,
                "status": t.status,
                "created_at": t.created_at,
                "updated_at": t.updated_at,
                "subtasks": [
                    {
                        **st.to_dict(),
                        "parent_task_id": st.parent_task_id.id if st.parent_task_id else None
                    } for st in t.get_subtasks()
                ]
            })
            for t in TaskModel.select().where(TaskModel.project_id == project_id)
        ]

    def get_user_tasks(self, user_id: str, project_id: str) -> List[TaskSchema]:
        return [
            TaskSchema.model_validate({
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "project_id": t.project_id,
                "start_date": t.start_date,
                "deadline": t.deadline,
                "assigned_to_id": t.assigned_to_id,
                "created_by_id": t.created_by_id,
                "status": t.status,
                "created_at": t.created_at,
                "updated_at": t.updated_at,
                "parent_task_id": t.parent_task_id.id if t.parent_task_id else None,
                "subtasks": []
            })
            for t in TaskModel.select().where(
                (TaskModel.assigned_to_id == user_id) |
                (TaskModel.created_by_id == user_id) |
                (TaskModel.project_id == project_id)
            )
        ]

    def get_project_tasks(self, project_id: str) -> List[TaskSchema]:
        return [
            TaskSchema.model_validate({
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "project_id": t.project_id,
                "start_date": t.start_date,
                "deadline": t.deadline,
                "assigned_to_id": t.assigned_to_id,
                "created_by_id": t.created_by_id,
                "status": t.status,
                "created_at": t.created_at,
                "updated_at": t.updated_at,
                "parent_task_id": t.parent_task_id.id if t.parent_task_id else None,
                "subtasks": [
                    {
                        **st.to_dict(),
                        "parent_task_id": st.parent_task_id.id if st.parent_task_id else None
                    } for st in t.get_subtasks()
                ]
            })
            for t in TaskModel.select().where(
                (TaskModel.project_id == project_id) &
                (TaskModel.parent_task_id.is_null())  # Only get top-level tasks
            )
        ]


class CommentsTable:
    def __init__(self):
        with get_db():
            DB.create_tables([CommentModel])

    def create_comment(self, comment: CommentCreate, user_id: str) -> CommentSchema:
        comment_id = str(uuid.uuid4())
        comment_db = CommentModel.create(
            id=comment_id,
            task_id=comment.task_id,
            user_id=user_id,
            content=comment.content,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        return CommentSchema.model_validate(comment_db.to_dict())

    def get_task_comments(self, task_id: str) -> List[CommentSchema]:
        return [
            CommentSchema.model_validate(comment.to_dict())
            for comment in CommentModel.select().where(CommentModel.task_id == task_id)
        ]

    def delete_comment(self, comment_id: str) -> bool:
        try:
            CommentModel.delete().where(CommentModel.id == comment_id).execute()
            return True
        except:
            return False


Users = UsersTable()
Projects = ProjectsTable()
Tasks = TasksTable()
Comments = CommentsTable()
