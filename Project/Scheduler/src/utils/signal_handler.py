import sys
import threading
import time
from typing import Callable

from src.mq.MessageQueue import MessageQueue

# create an event
should_stop_event = threading.Event()


def get_signal_handler_method(mq: MessageQueue) -> Callable:
    """
    Function which returns a method used for handling signals and interrupts.

    :param mq: Message queue we want to stop.
    :return: Method which will handle the termination signal.

    """

    def delete_mq(sig, frame):
        if mq.channel.is_open:
            mq.close_connection()

        # set the event
        should_stop_event.set()

        # wait 1 second to give time for the sleeper to exit
        time.sleep(1)

        sys.exit(0)

    return delete_mq
