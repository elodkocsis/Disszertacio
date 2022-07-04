import re
from sys import stderr
from typing import Optional, Dict, List
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


def strip_quotes(string: str) -> str:
    """
    Function which strips the quotation marks from strings.

    :param string: The string we want to strip of the quotation marks.
    :return: String stripped of quotation marks.
    """

    quotation_marks = ['"', "'", "`"]

    for mark in quotation_marks:
        string = string.replace(mark, "")

    return string


def remove_duplicates(list_of_strings: List[str]) -> List[str]:
    """
    Function which removes the duplicate elements from a list.

    :param list_of_strings: List of strings to filter.
    :return: Filtered list.

    """

    return list(set(list_of_strings))
