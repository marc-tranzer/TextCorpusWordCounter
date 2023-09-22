import time

from databases import models
from databases.sqlite_connect import get_session
from resources.queues import RESULT_QUEUE
from resources.tasks import ProcessingTextTaskStatusEnum
from resources.tasks import SingleProcessingTextTask


class ResultProcessor:
    def __init__(self) -> None:
        pass

    def _process_result(self, task: SingleProcessingTextTask) -> None:
        print(f"processing task {task.uuid}")
        if task.status != ProcessingTextTaskStatusEnum.PROCESSED.name:
            raise ValueError("ResultQueue should only include processed task")

        with get_session() as session:
            # Query the database for the word
            words_in_db: list[models.WordOccurrenceDBModel] = (
                session.query(models.WordOccurrenceDBModel)
                .filter(models.WordOccurrenceDBModel.word.in_(task.word_occurrences_result.keys()))
                .all()
            )

            # The word exists: Update the occurrence
            for word_in_db in words_in_db:
                word_in_db.occurrence += task.word_occurrences_result[word_in_db.word]
                del task.word_occurrences_result[word_in_db.word]
            # Create new db records for new words
            for remaining_word in task.word_occurrences_result.keys():
                # Word doesn't exist, create a new entry
                new_occurrence = models.WordOccurrenceDBModel(
                    word=remaining_word, occurrence=task.word_occurrences_result[remaining_word]
                )
                session.add(new_occurrence)
            session.commit()

    def run(self) -> None:
        while True:
            # Process all the results
            if not RESULT_QUEUE.empty():
                self._process_result(RESULT_QUEUE.get())
                continue
            else:
                time.sleep(1)
