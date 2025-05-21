from src.config.config import DatabaseConfig
from fifi import SQLAlchemyEngineBase


class DatabaseEngine(SQLAlchemyEngineBase):
    def __init__(self):
        super().__init__(
            host=DatabaseConfig.HOST,
            port=DatabaseConfig.PORT,
            user=DatabaseConfig.USER,
            password=DatabaseConfig.PASS,
            db_name=DatabaseConfig.DB,
            db_tech=DatabaseConfig.DB_TECH,
            db_lib=DatabaseConfig.DB_LIB,
        )
