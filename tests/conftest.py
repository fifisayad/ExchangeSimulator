import os
import asyncio
import sqlite3
import pytest

from fifi import DatabaseProvider


@pytest.fixture
def database_provider_test():
    sqlite3.connect("memory")
    os.environ["DATABASE_HOST"] = ""
    os.environ["DATABASE_PORT"] = "0"
    os.environ["DATABASE_USER"] = ""
    os.environ["DATABASE_PASS"] = ""
    db = DatabaseProvider(
        user="",
        password="",
        host="",
        port=0,
        db_name="memory",
        db_tech="sqlite",
        db_lib="aiosqlite",
    )
    event_loop = asyncio.new_event_loop()
    event_loop.run_until_complete(db.init_models())
    yield db
    # remove singleton instance
    DatabaseProvider.instance = None
    # remove sqlite instance file
    os.remove("./memory")
