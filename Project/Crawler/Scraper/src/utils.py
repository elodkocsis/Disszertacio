import re
from sys import stderr
from typing import Optional, Dict
from configparser import ConfigParser


def read_config_file(config_file: str) -> Optional[Dict]:
    """
    Function which reads a configuration file and returns the configuration parameters as a Dict.

    :param config_file: Path to the configuration file.
    :return: Dict if the file and specified section exists, otherwise None.

    """
    config_parser = ConfigParser()

    config_parser.read(config_file)

    # config_parser.remove_section('root')

    try:
        param_dict = dict(config_parser.items("DEFAULT"))
    except Exception as e:
        eprint(e)
        param_dict = None

    return param_dict


def eprint(*args, **kwargs):
    """
    Method which prints to STDERR.

    """
    print(*args, file=stderr, **kwargs)


def is_onion_link(link: str) -> bool:
    """
    Function which checks if the received link is an onion link.

    :param link: Link to be checked.
    :return: True, if the link is and onion link, otherwise False.

    """

    if (_ := re.match(r'(?:https?://)?(?:www)?(\S*?\.onion)\b', link)) is None:
        return False

    return True
