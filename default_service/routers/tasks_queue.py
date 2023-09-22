from uuid import uuid4

import pydantic
from databases import models
from databases.sqlite_connect import get_session
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from resources.queues import TASK_QUEUE
from routers.processing_text_tasks import ProcessingTextTaskStatusEnum
from routers.processing_text_tasks import SingleProcessingTextTask

queue_router = APIRouter(prefix="/tasks_queue", tags=["Compute Tasks Queue"])


class SingleProcessingTextTaskCreate(pydantic.BaseModel):
    text_absolute_location: str
    status: ProcessingTextTaskStatusEnum = ProcessingTextTaskStatusEnum.NOT_STARTED
    retry_count: int = 0


@queue_router.post(
    "",
    status_code=201,
    response_model=SingleProcessingTextTask,
)
async def create_task_in_queue(new_task: SingleProcessingTextTaskCreate) -> SingleProcessingTextTask:
    """Add a new task to the pool"""

    with get_session() as session:
        # Create the task in DB
        task = models.ProcessingTextTaskDBModel(
            uuid=str(uuid4()),
            text_absolute_location=new_task.text_absolute_location,
            retry_count=new_task.retry_count,
            status=new_task.status,
        )
        session.add(task)
        session.commit()

        # Add it to the local queue
        TASK_QUEUE.put(SingleProcessingTextTask.from_orm(task))

    return SingleProcessingTextTask.from_orm(task)


@queue_router.get("", status_code=200, response_model=SingleProcessingTextTask, responses={404: {}})
async def get_task_from_queue() -> SingleProcessingTextTask:
    """Dequeue a task of the pool"""
    if TASK_QUEUE.empty():
        raise HTTPException(status_code=404, detail="Queue Is Empty")

    task_in_queue: SingleProcessingTextTask = TASK_QUEUE.get()

    with get_session() as session:
        task = (
            session.query(models.ProcessingTextTaskDBModel)
            .filter(models.ProcessingTextTaskDBModel.uuid == str(task_in_queue.uuid))
            .one_or_none()
        )

        if not task:
            raise HTTPException(status_code=404)

        # Update the task status to IN_PROGRESS
        task.status = ProcessingTextTaskStatusEnum.IN_PROGRESS.name
        session.commit()

        return SingleProcessingTextTask.from_orm(task)
