from contextlib import contextmanager

# Create an in-memory SQLite database
from databases.models.base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

db_file_path = "my_database.db"
engine = create_engine(
    f"sqlite:///{db_file_path}?check_same_thread=False",
)

# Create the table in the database
Base.metadata.create_all(engine)

Session = scoped_session(sessionmaker(bind=engine))


# Create a session to interact with the database
@contextmanager
def get_session():  # type: ignore
    session = Session()
    session.expire_on_commit = False
    try:
        yield session

    finally:
        session.close()
