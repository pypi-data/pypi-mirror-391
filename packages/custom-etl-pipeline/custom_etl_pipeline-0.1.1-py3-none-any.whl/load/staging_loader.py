import pandas as pd
from ETL.DB.connection import get_connection
from ETL.config.logging_conf import get_logger
from ETL.base import BaseLoader
import sqlite3

logger = get_logger(__name__)

class StagingLoader(BaseLoader):
    """Loads cleaned DataFrames into the staging database."""

    def __init__(self, db_path: str, mode: str = "replace"):
        super().__init__()
        self.db_path = db_path
        self.mode = mode

    def load(self, data: dict[str, pd.DataFrame]):
        conn = get_connection(self.db_path)

        try:
            for name, df in data.items():
                if df.empty:
                    logger.warning(f"'{name}': empty DataFrame, skipping.")
                    continue

                staging_table = f"{name}_staging"

                logger.info(f"Loading {len(df)} rows into '{staging_table}' (mode={self.mode})...")

                try:
                    df.to_sql(
                        name=staging_table,
                        con=conn,
                        if_exists=self.mode,
                        index=False,
                        method="multi",
                        chunksize=200,
                    )

                    logger.info(f"Successfully loaded {len(df)} rows into '{staging_table}'.")

                except sqlite3.OperationalError as e:
                    if "too many SQL variables" in str(e).lower():
                        logger.error(
                            f"SQLite variable limit exceeded for '{staging_table}'. "
                            "Try reducing chunksize or column count."
                        )
                    else:
                        logger.exception(f"SQLite error while loading '{staging_table}': {e}")

                except Exception as e:
                    logger.exception(f"Unexpected error while loading '{staging_table}': {e}")

        finally:
            conn.close()
            logger.info("Database connection closed.")
