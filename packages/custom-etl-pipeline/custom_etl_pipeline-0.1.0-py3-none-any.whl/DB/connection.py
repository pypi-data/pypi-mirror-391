import sqlite3
import os


def get_connection(db_path: str):
    """
    Liefert eine SQLite-Connection.
    Später kann das erweitert werden.
    """
    db_dir = os.path.dirname(db_path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)

    return sqlite3.connect(db_path)
