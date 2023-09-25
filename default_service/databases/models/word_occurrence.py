# Define a simple User class as an example
from databases.models.base import Base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String


class WordOccurrenceDBModel(Base):
    __tablename__ = "word_occurrence"

    word = Column(String, unique=True, primary_key=True)
    occurrence = Column(Integer, nullable=False)

    # TODO(mt): Add reference to the text where this word is present
    pass
