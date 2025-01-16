from fastapi import Path, HTTPException, Depends
from app.core.endpoints.endpoint import BaseEndpoint
from app.services.authentication import user_check
from app.db.relational import Projects, Tasks
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class GanttTask(BaseModel):
    id: str
    name: str
    start: datetime
    end: datetime
    progress: float
    dependencies: List[str] = []
    parent: Optional[str] = None
    collapsed: bool = False


class GanttChart(BaseModel):
    tasks: List[GanttTask]


class GanttEndpoint(BaseEndpoint):
    def __init__(self):
        super().__init__()

        self.router.get("/{project_id}", response_model=GanttChart)(self.get_gantt)

    def _task_to_gantt(self, task, include_subtasks=True) -> List[GanttTask]:
        result = []
        progress = 1.0 if task.status == 'completed' else (
            0.5 if task.status == 'in_progress' else 0.0
        )

        gantt_task = GanttTask(
            id=task.id,
            name=task.name,
            start=task.start_date,
            end=task.deadline,
            progress=progress,
            parent=task.parent_task_id,
            dependencies=[]
        )
        result.append(gantt_task)

        if include_subtasks and task.subtasks:
            for subtask in task.subtasks:
                result.extend(self._task_to_gantt(subtask, include_subtasks=True))

        return result

    async def get_gantt(
        self,
        project_id: str = Path(...),
        userinfo=Depends(user_check)
    ) -> GanttChart:
        # Check if user has access to project
        if not Projects.user_has_access(userinfo.id, project_id):
            raise HTTPException(
                status_code=403,
                detail="No access to this project"
            )

        tasks = Tasks.get_project_tasks(project_id)
        gantt_tasks = []

        for task in tasks:
            gantt_tasks.extend(self._task_to_gantt(task))

        return GanttChart(tasks=gantt_tasks)
