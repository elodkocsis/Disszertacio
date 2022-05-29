from typing import Dict, Optional

from src.utils import read_config_file, eprint, dict_has_necessary_keys


def get_postgres_connection_string_with_params(host: str,
                                               port: int,
                                               username: str,
                                               password: str,
                                               database: str) -> str:
    """
    Function which creates a Postgres connection string for SQLAlchemy.

    :param host: Server hostname.
    :param port: Server port.
    :param username: Username.
    :param password: Password.
    :param database: Database to connect to.
    :return: Postgres connection string.

    """

    return f"postgresql://{username}:{password}@{host}:{port}/{database}"


def get_postgres_connection_string_with_dict(params: Dict) -> Optional[str]:
    """
    Function which creates a Postgres connection string based on the parameters provided in a Dict.

    Dictionary structure:

    {
        "postgresql_host" <str>,

        "postgresql_port": <int>,

        "postgresql_user": <str>,

        "postgresql_pass": <str>,

        "postgresql_db": <str>
    }

    :param params: Dictionary containing the parameters used
    :return: Postgres connection string if all the parameters are present.

    """

    # keys to look for which are needed to create the connection string for SQLAlchemy
    keys = ["postgresql_host", "postgresql_port", "postgresql_user", "postgresql_pass", "postgresql_db"]

    # checking for missing parameters in the received dictionary
    if not dict_has_necessary_keys(dict_to_check=params, needed_keys=keys):
        return None

    return get_postgres_connection_string_with_params(host=params[keys[0]],
                                                      port=params[keys[1]],
                                                      username=params[keys[2]],
                                                      password=params[keys[3]],
                                                      database=params[keys[4]])


def get_postgres_connection_string_with_config_file(config_file: str) -> Optional[str]:
    """
    Function which creates a Postgres connection sting based on the parameters provided in a configuration file.

    :param config_file: Path to the configuration file.
    :return: Postgres connection string if all the parameters are present.

    """

    if (params_dict := read_config_file(config_file=config_file, section="POSTGRES")) is not None:
        return get_postgres_connection_string_with_dict(params=params_dict)
    else:
        return None
