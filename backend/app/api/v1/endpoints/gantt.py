from fastapi import Path, HTTPException, Depends
from app.core.endpoints.endpoint import BaseEndpoint
from app.services.authentication import user_check
from app.db.relational import Projects, Tasks
from typing import List
from datetime import datetime
from pydantic import BaseModel


class GanttTask(BaseModel):
    id: str
    name: str
    start: datetime
    end: datetime
    progress: float
    dependencies: List[str] = []


class GanttChart(BaseModel):
    tasks: List[GanttTask]


class GanttEndpoint(BaseEndpoint):
    def __init__(self):
        super().__init__()

        self.router.get("/{project_id}", response_model=GanttChart)(self.get_gantt)

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
            progress = 1.0 if task.status == 'completed' else (
                0.5 if task.status == 'in_progress' else 0.0
            )

            gantt_tasks.append(GanttTask(
                id=task.id,
                name=task.name,
                start=task.start_date,
                end=task.deadline,
                progress=progress,
                dependencies=[]  # TODO: Implement task dependencies if needed
            ))

        return GanttChart(tasks=gantt_tasks)
