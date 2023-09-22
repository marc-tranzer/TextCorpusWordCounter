import pathlib
from uuid import uuid4

import pydantic
from databases import models
from databases.sqlite_connect import get_session
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from routers.tasks_queue import TASK_QUEUE

text_corpus_location_router = APIRouter(prefix="/text_corpus_locations", tags=["Text Corpus Locations"])


class SingleCorpusLocationCreate(pydantic.BaseModel):
    folder_location: str


class SingleCorpusLocationCreateResponse(pydantic.BaseModel):
    number_of_tasks_created: int


@text_corpus_location_router.post(
    "", status_code=201, response_model=SingleCorpusLocationCreateResponse, responses={404: {}}
)
async def add_new_text_corpus_location(
    folder_location_create: SingleCorpusLocationCreate,
) -> SingleCorpusLocationCreateResponse:
    """Add a new folder/corpus location to be processed"""
    try:
        files = [
            p
            for p in pathlib.Path(folder_location_create.folder_location).iterdir()
            if p.is_file() and p.name.endswith(".txt")
        ]
    except Exception:
        raise HTTPException(status_code=404)

    with get_session() as session:
        for f in files:
            new_task = models.ProcessingTextTaskDBModel(
                uuid=str(uuid4()),
                text_absolute_location=str(f.absolute()),
            )
            session.add(new_task)
            TASK_QUEUE.put(new_task)
        session.commit()

    return SingleCorpusLocationCreateResponse(number_of_tasks_created=len(files))
