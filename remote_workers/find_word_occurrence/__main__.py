import collections
import json
import os
import time
from enum import Enum
from pathlib import Path
from uuid import UUID

import pydantic
import requests
from pydantic import validator


CENTRAL_NODE_URL = f"{'localhost' if os.environ.get('RUN_IN_DOCKER') else '0.0.0.0'}:5001"

# DUPLICATE FROM resources.py
# TODO(mt): Create shared library that all nodes can use
class ProcessingTextTaskStatusEnum(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    PROCESSED = "PROCESSED"
    # This will trigger a retry
    FAILED = "FAILED"


class SingleProcessingTextTask(pydantic.BaseModel):
    uuid: UUID
    text_absolute_location: str
    status: ProcessingTextTaskStatusEnum = ProcessingTextTaskStatusEnum.NOT_STARTED
    retry_count: int = 0
    word_occurrences_result: dict[str, int] | None = None

    @validator("word_occurrences_result", pre=True)
    def validate_word_occurrences_result(cls, value):
        if isinstance(value, str):
            return json.loads(value)
        else:
            return value


def _process_file(file_path: Path) -> dict[str, int]:
    with open(file_path) as f:
        all_words = f.read().split(" ")
    return collections.Counter(all_words)


# TODO(mt): auto-restart the node if it crashes
if __name__ == "__main__":
    print("Remote Node Started")
    # Periodically Poll for new messages
    while True:
        try:
            response = requests.get(f"{CENTRAL_NODE_URL}/tasks_queue")
            response.raise_for_status()
        except requests.HTTPError as http_error:
            if http_error.response.status_code == 404:
                print(f"No Jobs in Queue, retry in 5seconds")
                time.sleep(5)
                continue
            else:
                print(f"Server responded with unexpected error {http_error.response.status_code}")
                time.sleep(10)
                continue
        except requests.RequestException:
            print(f"Server is not reachable, retry in 10 seconds")
            time.sleep(10)
            continue

        # If a message is available in the queue, process it
        try:
            task_to_process = SingleProcessingTextTask.parse_obj(response.json())
        except pydantic.ValidationError:
            response = requests.put(
                f"{CENTRAL_NODE_URL}/processing_text_tasks/{str(response.json()['uuid'])}/results",
                json={"status": ProcessingTextTaskStatusEnum.FAILED.name},
            )
            continue

        try:
            print(f"Processing task {task_to_process}")
            result = _process_file(Path(task_to_process.text_absolute_location))
        except Exception as e:
            # TODO(mt): Don't return wide exception
            print(f"Exception occurs: {e}")
            response = requests.put(
                f"{CENTRAL_NODE_URL}/processing_text_tasks/{str(task_to_process.uuid)}/results",
                json={"status": ProcessingTextTaskStatusEnum.FAILED.name},
            )
            continue
        print(f"Nb of words: {len(result.keys())}")

        response = requests.put(
            f"{CENTRAL_NODE_URL}/processing_text_tasks/{str(task_to_process.uuid)}/results",
            json={"status": ProcessingTextTaskStatusEnum.PROCESSED.name, "word_occurrences_result": json.dumps(result)},
        )
