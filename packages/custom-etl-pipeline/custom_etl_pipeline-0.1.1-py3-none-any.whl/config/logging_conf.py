import logging
import os

def setup_logging(level=logging.INFO):
    """Called ONCE at the start of the app to configure global logging."""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "etl.log")

    log_format = "%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, mode="a", encoding="utf-8")
        ]
    )

    logging.info("Logging initialized.")


def get_logger(name=__name__):
    """Returns a named logger using the global configuration."""
    return logging.getLogger(name)
