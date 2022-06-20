from typing import List, Dict, Union, Optional

import anvil

from src.topic_modelling.ModelManager import ModelManager

# call the model manager to kickstart the whole load process
# we need to take the instance out because if we call the class in an anvil callable, it will create
# a new instance for each callable thread and that's not too good
from src.utils.enums import ModelStatus

model_manager = ModelManager()


@anvil.server.callable
def get_pages(query: str, num: int) -> Optional[Union[ModelStatus, List[Dict]]]:
    """
    Function which
    :param query:
    :param num:
    :return:
    """
    return model_manager.get_pages(query=query, num_of_pages=num)


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

    anvil.server.connect(url=uplink_url, key=key)

    anvil.server.wait_forever()
