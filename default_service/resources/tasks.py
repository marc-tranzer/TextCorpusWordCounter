import json
from enum import Enum
from uuid import UUID

import pydantic
from pydantic import validator


class ProcessingTextTaskStatusEnum(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    PROCESSED = "PROCESSED"
    # This will trigger a retry
    FAILED = "FAILED"


class SingleProcessingTextTask(pydantic.BaseModel):
    class Config:
        orm_mode = True

    uuid: UUID
    # TODO(mt): Move this to a reference to a Document DB
    text_absolute_location: str
    status: ProcessingTextTaskStatusEnum = ProcessingTextTaskStatusEnum.NOT_STARTED
    retry_count: int = 0
    word_occurrences_result: dict[str, int] | None = None

    @validator("word_occurrences_result", pre=True)
    def validate_word_occurrences_result(cls, value):  # type: ignore
        if isinstance(value, str):
            return json.loads(value)
        else:
            return value
