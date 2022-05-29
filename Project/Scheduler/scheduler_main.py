import sys

from src.db.database import session_scope
from src.db.db_operations import get_page_urls_to_scrape
from src.mq.MessageQueue import MessageQueue
from src.utils import read_config_file

if __name__ == '__main__':

    # get the parameters for connecting to the message queue
    if (mq_params := read_config_file(config_file="config.conf", section="MQ")) is None:
        sys.exit(3)

    # create connect to the message queue
    message_queue = MessageQueue(param_dict=mq_params, function_to_execute=None)

    # create a session
    with session_scope() as session:

        # get all the urls that need to be scraped on this run
        list_of_urls_to_scrape = get_page_urls_to_scrape(session=session, access_day_difference=1)

        # send each url on their way through the MQ
        for url in list_of_urls_to_scrape:
            message_queue.send_message(data=url)
