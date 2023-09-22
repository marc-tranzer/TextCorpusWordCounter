import uvicorn
from databases import models
from databases.models.base import Base
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from routers.processing_text_tasks import tasks_router
from routers.tasks_queue import queue_router
from routers.text_corpus_locations import text_corpus_location_router
from routers.most_frequent_words_count import most_frequent_words_count_router

HOST: str = "0.0.0.0"
SERVER_PORT: int = 5001

APP = FastAPI()
APP.include_router(tasks_router)
APP.include_router(queue_router)
APP.include_router(text_corpus_location_router)
APP.include_router(most_frequent_words_count_router)

openapi_schema = get_openapi(
    title="Word Counter Exercise",
    version="0.1.0",
    description="Display More Frequent Words from a text corpus",
    routes=APP.routes,
)

APP.openapi_schema = openapi_schema


class API:
    """This class is supposed to contain the web server.
    API.run should start the server.
    """

    def run(self) -> None:
        uvicorn.run("api:APP", host=HOST, port=SERVER_PORT)
