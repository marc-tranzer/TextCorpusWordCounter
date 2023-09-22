from uuid import uuid4
from databases import models
from databases.sqlite_connect import get_session


class TestMostFrequentWordsCount:
    def test(self, api_test_client, clean_database):
        # Given a user with 2 tasks, one completed and one not started
        with get_session() as test_session:
            # TODO(mt): Use factory to create DB records
            task_completed = models.ProcessingTextTaskDBModel(
                uuid=str(uuid4()),
                text_absolute_location="test_location",
                retry_count=0,
                status="PROCESSED",
            )
            test_session.add(task_completed)

            task_in_progress = models.ProcessingTextTaskDBModel(
                uuid=str(uuid4()),
                text_absolute_location="test_location2",
                retry_count=0,
                status="NOT_STARTED",
            )
            test_session.add(task_in_progress)
            test_session.commit()

            # And the global word count with 3 words
            for word, count in [("the", 10), ("at", 3), ("constitution", 1)]:
                occurrence_per_word = models.WordOccurrenceDBModel(word=word, occurrence=count)
                test_session.add(occurrence_per_word)
                test_session.commit()

            # When we request the top2 words
            results = api_test_client.get("/most_frequent_words_count?limit=2")

            # Then it succeeds and the right result
            assert results.status_code == 200
            assert len(results.json()["display"]) == 2
            assert set([res[0] for res in results.json()["display"]]) == {"the", "at"}

    def test_wait_for_all_task_to_finish__one_incomplete_task(self, api_test_client, clean_database):
        # Given a user with 2 task, one completed and one not started
        with get_session() as test_session:
            # TODO(mt): Use factory to create DB records
            task_completed = models.ProcessingTextTaskDBModel(
                uuid=str(uuid4()),
                text_absolute_location="test_location",
                retry_count=0,
                status="PROCESSED",
            )
            test_session.add(task_completed)

            task_in_progress = models.ProcessingTextTaskDBModel(
                uuid=str(uuid4()),
                text_absolute_location="test_location2",
                retry_count=0,
                status="NOT_STARTED",
            )
            test_session.add(task_in_progress)
            test_session.commit()

            # And the global word count with 3 words
            for word, count in [("the", 10), ("at", 3), ("constitution", 1)]:
                occurrence_per_word = models.WordOccurrenceDBModel(word=word, occurrence=count)
                test_session.add(occurrence_per_word)
                test_session.commit()

            # When we request the top2 words but we want to ensure every task are completed
            results = api_test_client.get("/most_frequent_words_count?limit=2&skip_if_process_incomplete=true")

            # Then it returns accepted
            assert results.status_code == 202

    def test_wait_for_all_task_to_finish__all_completed(self, api_test_client, clean_database):
        # Given a user with 2 task, all completed
        with get_session() as test_session:
            # TODO(mt): Use factory to create DB records
            task_completed = models.ProcessingTextTaskDBModel(
                uuid=str(uuid4()),
                text_absolute_location="test_location",
                retry_count=0,
                status="PROCESSED",
            )
            test_session.add(task_completed)

            task_in_progress = models.ProcessingTextTaskDBModel(
                uuid=str(uuid4()),
                text_absolute_location="test_location2",
                retry_count=0,
                status="PROCESSED",
            )
            test_session.add(task_in_progress)
            test_session.commit()

            # And the global word count with 3 words
            for word, count in [("the", 10), ("at", 3), ("constitution", 1)]:
                occurrence_per_word = models.WordOccurrenceDBModel(word=word, occurrence=count)
                test_session.add(occurrence_per_word)
                test_session.commit()

            # When we request the top2 words but we want to ensure every task are completed
            results = api_test_client.get("/most_frequent_words_count?limit=2&skip_if_process_incomplete=true")

            # Then it returns complete
            assert results.status_code == 200
            # With right result
            assert results.status_code == 200
            assert len(results.json()["display"]) == 2
            assert set([res[0] for res in results.json()["display"]]) == {"the", "at"}
