import sys
import time

from src.server.anvil_server import should_stop_event
from src.topic_modelling.ModelManager import ModelManager


def signal_handler(sig, frame):
    # delete the timer and/or thread
    ModelManager().__del__()

    # set the event to stop the server
    should_stop_event.set()

    # wait a bit for the server to have time to check the event status
    time.sleep(1)

    # exit
    sys.exit(0)

