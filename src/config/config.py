import os
from dotenv import load_dotenv
from fifi import singleton

load_dotenv()


@singleton
class DatabaseConfig:
    HOST: str = os.getenv("DATABASE_HOST", "localhost")
    PORT: int = int(os.getenv("DATABASE_PORT", 2222))
    USER: str = os.getenv("DATABASE_USER", "FiFi")
    PASS: str = os.getenv("DATABASE_PASS", "FiFi@HOWLS")
    DB: str = os.getenv("DATABASE_NAME", "ExchangeSimulator")
    DB_TECH: str = os.getenv("DATABASE_TECH", "postgresql")
    DB_LIB: str = os.getenv("DATABASE_LIB", "psycopg")
