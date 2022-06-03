import sys
import logging


def get_logger() -> logging.Logger:
    # creating a new logger
    logger = logging.getLogger("Scraper")

    # if it has already been initialized, just return it
    if logger.hasHandlers():
        return logger

    # initialize the logger as needed
    formatter = logging.Formatter('%(asctime)s | %(levelname)s: %(message)s')
    console = logging.StreamHandler(stream=sys.stdout)
    console.setFormatter(formatter)
    console.setLevel(level=logging.INFO)
    logger.addHandler(console)
    logger.setLevel(logging.INFO)

    return logger
