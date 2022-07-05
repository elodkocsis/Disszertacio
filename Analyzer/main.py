import signal
import sys

from src.server.anvil_server import start_server
from src.utils.general import get_uplink_env_var, get_uplink_key
from src.utils.logger import get_logger
from src.utils.signal_handler import signal_handler

# getting the logger
logger = get_logger()

if __name__ == '__main__':

    # read the environment variables for server connection
    uplink_url = get_uplink_env_var()
    uplink_key = get_uplink_key()

    # check variables
    if uplink_url is None:
        logger.error("Uplink locations is missing!")
        sys.exit(1)

    if uplink_key is None:
        logger.error("Uplink server key is missing!")
        sys.exit(1)

    # register signal handling method
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # start the server
    start_server(uplink_url=uplink_url, key=uplink_key)
