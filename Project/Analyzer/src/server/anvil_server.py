import threading
import time
from typing import List, Dict, Union, Optional

import anvil

from src.topic_modelling.ModelManager import ModelManager
from src.utils.enums import ModelStatus
from src.utils.logger import get_logger

logger = get_logger()

# create an event
should_stop_event = threading.Event()


@anvil.server.callable
def get_pages(query: str, num: int) -> Optional[Union[ModelStatus, List[Dict]]]:
    """
    Function which returns the results for a given query.

    :param query: Query string for which we want to get the results.
    :param num: Number of results to be returned.
    :return: List of dictionaries containing the data for the pages or a model status if the model is not set up yet.

    """

    return ModelManager().get_pages(query=query, num_of_pages=num)


@anvil.server.callable
def heartbeat() -> bool:
    """
    Function which returns a simple True for serving as a heartbeat.

    :return: True.
    """
    return True


def start_server(uplink_url: str, key: str):
    """
    Method which starts the anvil server.

    :param uplink_url: The URL of the Webapp uplink.
    :param key: Webapp uplink key.

    """

    # call the model manager to kickstart the whole load process and create a single instance across the application
    # we are calling it here as we don't want it to run and create the instance at the import step called from main
    ModelManager()

    anvil.server.connect(url=uplink_url, key=key)

    while True:
        if should_stop_event.isSet():
            break

        time.sleep(0.5)
