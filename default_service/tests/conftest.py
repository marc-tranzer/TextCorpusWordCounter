import os

pytest_plugins = ["tests.fixtures"]


def pytest_sessionfinish(session, exitstatus):
    os.remove("my_database.db")
