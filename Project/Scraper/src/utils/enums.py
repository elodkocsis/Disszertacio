from enum import Enum


class ScrapingResult(int, Enum):
    """
    Class describing the possible states of the scraping result result.

    """

    INVALID_URL = 1
    SCRAPING_FAILED = 2
