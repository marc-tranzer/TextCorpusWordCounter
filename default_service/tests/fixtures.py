import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient

from databases.models.base import Base
from databases.sqlite_connect import get_session
from routers.most_frequent_words_count import most_frequent_words_count_router
from routers.processing_text_tasks import tasks_router
from routers.tasks_queue import queue_router
from routers.text_corpus_locations import text_corpus_location_router


@pytest.fixture()
def api_test_client():
    # Create a test client that can be used for testing the API
    app = FastAPI()
    app.include_router(tasks_router)
    app.include_router(queue_router)
    app.include_router(text_corpus_location_router)
    app.include_router(most_frequent_words_count_router)

    return TestClient(app)


@pytest.fixture()
def clean_database():
    for table in reversed(Base.metadata.sorted_tables):
        with get_session() as session:
            session.execute(table.delete())
            session.commit()
