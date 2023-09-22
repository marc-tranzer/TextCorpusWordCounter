# Define a simple User class as an example
from uuid import uuid4

from databases.models.base import Base
from resources.tasks import ProcessingTextTaskStatusEnum
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String


class ProcessingTextTaskDBModel(Base):
    __tablename__ = "processing_text_task"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String, unique=True, nullable=False)
    text_absolute_location = Column(String, nullable=False)
    status = Column(String, nullable=False, default=ProcessingTextTaskStatusEnum.NOT_STARTED.name)
    retry_count = Column(Integer, nullable=False, default=0)

    # FIXME
    word_occurrences_result = Column(String, nullable=False, default="{}")
