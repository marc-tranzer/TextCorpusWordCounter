import pydantic
from databases import models
from databases.sqlite_connect import get_session
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from routers.processing_text_tasks import ProcessingTextTaskStatusEnum

most_frequent_words_count_router = APIRouter(prefix="/most_frequent_words_count", tags=[""])


class MostFrequentWordsCountResponse(pydantic.BaseModel):
    display: list[tuple[str, int]]


@most_frequent_words_count_router.get(
    "",
    status_code=200,
    response_model=MostFrequentWordsCountResponse,
)
async def display_result(skip_if_process_incomplete: bool = False, limit: int = 10) -> MostFrequentWordsCountResponse:

    """Display the result of the file processing on a screen
    params:
    - limit: number of max words to return
    - skip_if_process_incomplete: Only return a result when
    """

    with get_session() as db_session:
        # Then check if all the task have been processed

        if skip_if_process_incomplete:
            result = (
                db_session.query(models.ProcessingTextTaskDBModel)
                .filter(
                    models.ProcessingTextTaskDBModel.status.in_(
                        [
                            ProcessingTextTaskStatusEnum.IN_PROGRESS.name,
                            ProcessingTextTaskStatusEnum.NOT_STARTED.name,
                        ]
                    )
                )
                .first()
            )
            if result is not None:
                # TODO(mt): Add Progress Percentage
                raise HTTPException(detail="STILL PROCESSING", status_code=202)

        most_frequent_words_with_occurrence = [
            (res[0], res[1])
            for res in (
                db_session.query(models.WordOccurrenceDBModel.word, models.WordOccurrenceDBModel.occurrence)
                .order_by(models.WordOccurrenceDBModel.occurrence.desc())
                .limit(limit)
                .all()
            )
        ]
        return MostFrequentWordsCountResponse(display=most_frequent_words_with_occurrence)
