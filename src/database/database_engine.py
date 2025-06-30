from .. import DatabaseConfig
from fifi import SQLAlchemyEngineBase


class DatabaseEngine(SQLAlchemyEngineBase):
    def __init__(self):
        super().__init__()
