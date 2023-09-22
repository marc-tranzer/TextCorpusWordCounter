import threading

from api import API
from databases.sqlite_connect import engine
from workers.ResultProcessor.result_processor import ResultProcessor

if __name__ == "__main__":
    print("Program is starting")

    print(f"DB {engine} started")
    # Running the api should not block, run in on a different thread
    api = API()
    A = threading.Thread(target=api.run)
    A.start()

    result_processor = ResultProcessor().run()
