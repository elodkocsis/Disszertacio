import signal
import sys

from src.db.database import session_scope
from src.db.db_operations import get_page_urls_to_scrape
from src.mq.MessageQueue import MessageQueue
from src.utils.Sleeper import Sleeper
from src.utils.signal_handler import get_signal_handler_method
from src.utils.general import read_config_file, parse_commandline_args

if __name__ == '__main__':

    # get command line arguments
    args = parse_commandline_args()

    # sleep if necessary
    Sleeper()(hours=1)

    # get the parameters for connecting to the message queue
    if (mq_params := read_config_file(config_file=args.config_file, section="MQ")) is None:
        sys.exit(3)

    # create connect to the message queue
    message_queue = MessageQueue(param_dict=mq_params, function_to_execute=None)

    # register signal handling method
    signal.signal(signal.SIGINT, get_signal_handler_method(mq=message_queue))
    signal.signal(signal.SIGTERM, get_signal_handler_method(mq=message_queue))

    # create a session
    with session_scope() as session:

        # get all the urls that need to be scraped on this run
        list_of_urls_to_scrape = get_page_urls_to_scrape(session=session, access_day_difference=1)

        # send each url on their way through the MQ
        for url in list_of_urls_to_scrape:
            message_queue.send_message(data=url)
