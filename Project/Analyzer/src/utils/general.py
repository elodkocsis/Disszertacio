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
    if val == default_value or len(val) == 0:
        return default_value

    return val


def remove_file(filename: str) -> bool:
    """
    Function which removes a file if it exists.

    :param filename: Path to the file.
    :return: True if the file was removed, otherwise False
    """
    if os.path.exists(filename):
        try:
            os.remove(filename)
        except OSError:
            return False
        return True
    return False


def create_folder(relative_path: str):
    """
    Function which creates a folder.

    :param relative_path: The relative path to the folder.
    :return: Returns the status of the operation.
    """
    try:
        os.makedirs(relative_path, exist_ok=True)
    except OSError as e:
        logger.error(f"Exception when trying to create folder '{relative_path}': {e}")
        # return false if folder cannot be created/exists
        return False

    # return true if folder was created
    return True


def file_exists(path: str) -> bool:
    """
    Function which checks if a file exists.

    :param path: Path to the file.
    :return: True if the file exists, otherwise False.

    """

    try:
        return os.path.exists(path)
    except Exception as e:
        logger.warning(f"Exception when checking if file at path '{path}' exists: {e}")
        return False


def get_uplink_env_var() -> Optional[str]:
    """
    Function which tries to read the server uplink location from an environment variable.

    :return: Uplink location if it is set as an environment variable.

    """

    return get_environment_variable(variable="UPLINK", default_value=None)


def get_uplink_key() -> Optional[str]:
    """
    Function which tries to read the server uplink key from an environment variable.

    :return: Uplink server key if it is set as an environment variable.

    """

    return get_environment_variable(variable="UPLINK_KEY", default_value=None)


def get_trainer_thread_number(default_value=12) -> int:
    """
    Function which tries to read the number of trainer threads from an environment variable. The number should be
    specified based on the capabilities of the processor running this application.

    :param default_value: The number of threads to use for model training if the environment variable is not set.
    :return: Number of threads to use for training the model.
    """

    return get_environment_variable(variable="TRAINER_THREADS", default_value=default_value)
