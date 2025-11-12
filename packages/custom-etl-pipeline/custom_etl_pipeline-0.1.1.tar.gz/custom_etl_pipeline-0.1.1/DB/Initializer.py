from ETL.DB.connection import get_connection
from ETL.config.logging_conf import get_logger

logger = get_logger(__name__)




def init_schema(db_path: str, schema_file: str):
    """Initializes the database based on the schema file."""
    logger.info(f"Connecting to database at: {db_path}")
    
    try:
        conn = get_connection(db_path)
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON;")
        logger.info("Foreign keys enabled.")

        with open(schema_file, "r", encoding="utf-8") as f:
            schema_sql = f.read()
            logger.info(f"Loaded schema from {schema_file} ({len(schema_sql)} bytes).")

        cur.executescript(schema_sql)
        conn.commit()
        logger.info("Schema executed and committed successfully.")
    
    except Exception as e:
        logger.exception(f"Error initializing database schema: {e}")
        raise
    
    finally:
        conn.close()
        logger.info("Database connection closed.")
