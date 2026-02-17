from fastapi import Path, Body, HTTPException, Depends
from app.core.endpoints.endpoint import BaseEndpoint
from app.schemas.comment import Comment, CommentCreate
from app.schemas.base import DefaultResponse
from app.services.authentication import user_check
from app.db.relational import Comments, Projects, Tasks
from app.schemas.users import UserRole
from typing import List


class CommentsEndpoint(BaseEndpoint):
    def __init__(self):
        super().__init__()

        self.router.get("/{task_id}", response_model=List[Comment])(self.get_task_comments)
        self.router.post("/", response_model=Comment)(self.create_comment)
        self.router.delete("/{comment_id}", response_model=DefaultResponse)(self.delete_comment)

    async def get_task_comments(
        self,
        task_id: str = Path(...),
        userinfo=Depends(user_check)
    ) -> List[Comment]:
        # Verify user has access to the task's project
        task = Tasks.get_task(task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        if not (userinfo.is_admin or Projects.user_has_access(userinfo.id, task.project_id)):
            raise HTTPException(status_code=403, detail="No access to this task")

        return Comments.get_task_comments(task_id)

    async def create_comment(
        self,
        comment: CommentCreate = Body(...),
        userinfo=Depends(user_check)
    ) -> Comment:
        # Verify user has access to the task's project
        task = Tasks.get_task(comment.task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        if not (userinfo.is_admin or Projects.user_has_access(userinfo.id, task.project_id)):
            raise HTTPException(status_code=403, detail="No access to this task")

        return Comments.create_comment(comment, userinfo.id)

    async def delete_comment(
        self,
        comment_id: str = Path(...),
        userinfo=Depends(user_check)
    ) -> DefaultResponse:
        # Fetch the comment to verify ownership
        comment = Comments.get_comment(comment_id)
        if not comment:
            raise HTTPException(status_code=404, detail="Comment not found")

        # Only comment owner or admin can delete
        if comment.user_id != userinfo.id and not userinfo.is_admin:
            raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

        if Comments.delete_comment(comment_id):
            return DefaultResponse(code=200, result="Comment deleted successfully")
        raise HTTPException(status_code=500, detail="Error deleting comment")
