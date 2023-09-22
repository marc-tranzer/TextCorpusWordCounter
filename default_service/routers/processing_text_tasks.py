import json
from uuid import UUID

import pydantic
from databases import models
from databases.sqlite_connect import get_session
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from pydantic import validator
from resources.queues import RESULT_QUEUE
from resources.queues import TASK_QUEUE
from resources.tasks import ProcessingTextTaskStatusEnum
from resources.tasks import SingleProcessingTextTask

tasks_router = APIRouter(prefix="/processing_text_tasks", tags=["Processing Text Tasks"])


class PutTextProcessingResultParams(pydantic.BaseModel):
    status: ProcessingTextTaskStatusEnum
    word_occurrences_result: dict[str, int] | None = None

    @validator("word_occurrences_result", pre=True)
    def validate_word_occurrences_result(cls, value):  # type: ignore
        if isinstance(value, str):
            return json.loads(value)
        else:
            return value


@tasks_router.put(
    "/{uuid}/results", status_code=200, response_model=SingleProcessingTextTask, responses={404: {}, 204: {}}
)
async def put_result_in_task(
    uuid: UUID,
    word_occurrences_result_params: PutTextProcessingResultParams,
) -> SingleProcessingTextTask:
    """Put results to the task"""
    with get_session() as session:
        task = (
            session.query(models.ProcessingTextTaskDBModel)
            .filter(models.ProcessingTextTaskDBModel.uuid == str(uuid))
            .one_or_none()
        )
        if not task:
            raise HTTPException(status_code=404)

        if word_occurrences_result_params.status == ProcessingTextTaskStatusEnum.PROCESSED:
            task.status = word_occurrences_result_params.status.name
            task.word_occurrences_result = json.dumps(word_occurrences_result_params.word_occurrences_result)
            session.commit()

            # Add the job to the list of jobs to processed
            RESULT_QUEUE.put(SingleProcessingTextTask.from_orm(task))
            return SingleProcessingTextTask.from_orm(task)
        elif task.retry_count == 3:
            # Store the task as failed and don't retry it
            task.status = ProcessingTextTaskStatusEnum.FAILED.name
            session.commit()

            raise HTTPException(status_code=204)
        else:
            task.retry_count += 1
            task.status = ProcessingTextTaskStatusEnum.IN_PROGRESS.name
            session.commit()
            TASK_QUEUE.put(task)
            return SingleProcessingTextTask.from_orm(task)
