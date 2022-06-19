import os
import sys
from typing import Optional, Dict, List, Any
from argparse import ArgumentParser, Namespace
from configparser import ConfigParser

from environs import Env

from src.utils.logger import get_logger

# get logger
logger = get_logger()


def read_config_file(config_file: str, section: str) -> Optional[Dict]:
    """
    Function which reads a configuration file and returns the configuration parameters as a Dict.

    :param config_file: Path to the configuration file.
    :param section: The section to read the parameters within the config file.
    :return: Dict if the file and specified section exists, otherwise None.

    """
    config_parser = ConfigParser()

    config_parser.read(config_file)

    try:
        param_dict = dict(config_parser.items(section))
    except Exception as e:
        logger.error(f"Error while reading config file: {e}")
        param_dict = None

    return param_dict


def dict_has_necessary_keys(dict_to_check: Dict, needed_keys: List) -> bool:
    """
    Function which checks if a dictionary has the necessary keys or not.

    :param dict_to_check: Dictionary to be checked.
    :param needed_keys: List of keys that need to be present in the dictionary.
    :return: True if the keys are present in the dictionary, otherwise False.
    """

    # set operation to get missing values
    # this will check if all the necessary keys are present in a dictionary
    diff = set(needed_keys) - set(dict_to_check.keys())

    if len(diff) > 0:
        logger.warning("Parameters missing from dict: {}".format(",".join(diff)))
        return False

    return True


def running_in_docker() -> bool:
    """
    Function which determines if the application is running in a Docker container by checking the environment variable
    "AM_I_IN_A_DOCKER_CONTAINER".

    :return: True if script is running in a docker container, otherwise False.

    """

    try:
        return Env().bool("AM_I_IN_A_DOCKER_CONTAINER", False)
    except Exception:
        return False


def get_config_file_location() -> str:
    """
    Function which returns the config file location based on the environment the application is running in.

    :return: Path to the config file.

    """
    if running_in_docker():
        return "config.conf"

    return "config_local.conf"


def get_environment_variable(variable: str, default_value: Any) -> Any:
    """
    Function which returns an environment variable.

    :param variable: Name of the environment variable.
    :param default_value: The default value if the environment variable doesn't exist.
    :return: Value of the environment variable.

    """

    val = os.environ.get(variable, default_value)

    # check the situation where the variable is declared, but it has no value
    if len(val) == 0:
        return default_value

    return val


# TODO: implement function
def remove_file(file_location: str) -> bool:
    pass
