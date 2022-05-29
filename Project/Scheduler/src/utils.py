from sys import stderr
from typing import Optional, Dict
from configparser import ConfigParser


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
        eprint(f"Error while reading config file: {e}")
        param_dict = None

    return param_dict


def eprint(*args, **kwargs):
    """
    Method which prints to STDERR.

    """
    print(*args, file=stderr, **kwargs)
