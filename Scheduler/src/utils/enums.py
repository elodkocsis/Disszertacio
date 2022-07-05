from enum import Enum


class ProcessingResult(int, Enum):
    """
    Class describing the possible states of the received data processing result.

    """
    SUCCESS = 0
    PROCESSING_FAILED = 1
    SAVE_FAILED = 2
