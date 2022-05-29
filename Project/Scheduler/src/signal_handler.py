import sys
from typing import Callable

from src.mq.MessageQueue import MessageQueue


def get_signal_handler_method(mq: MessageQueue) -> Callable:
    """
    Function which returns a method used for handling signals and interrupts.

    :param mq: Message queue we want to stop.
    :return: Method which will handle the termination signal.

    """

    def delete_mq(sig, frame):
        mq.close_connection()
        sys.exit(0)

    return delete_mq
