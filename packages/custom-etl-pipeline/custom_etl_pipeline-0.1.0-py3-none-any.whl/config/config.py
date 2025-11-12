import os
from dotenv import load_dotenv

load_dotenv()



class Config:
    # === Paths ===
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    SQL_DIR = os.path.join(BASE_DIR, "sql")
    LOG_DIR = os.path.join(BASE_DIR, "logs")

    DB_PATH = os.path.join(DATA_DIR, "staging.db")
    SCHEMA_FILE = os.path.join(SQL_DIR, "notar_schema.sql")

    # === Logging ===
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # === Mode (for incremental loads etc.) ===
    LOAD_MODE = os.getenv("LOAD_MODE", "initial")  # or "incremental"

    # === Database type (for future extensibility) ===
    DB_TYPE = os.getenv("DB_TYPE", "sqlite")
