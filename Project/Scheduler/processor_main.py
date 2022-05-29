import sys
import signal

from src.signal_handler import get_signal_handler_method
from src.utils import read_config_file
from src.mq.MessageQueue import MessageQueue
from src.processor.result_processor import process_scraped_result


if __name__ == '__main__':
    # get the parameters for connecting to the message queue
    if (mq_params := read_config_file(config_file="config.conf", section="MQ")) is None:
        sys.exit(3)

    # create connect to the message queue
    message_queue = MessageQueue(param_dict=mq_params, function_to_execute=process_scraped_result)

    # register signal handling method
    signal.signal(signal.SIGINT, get_signal_handler_method(mq=message_queue))
    signal.signal(signal.SIGTERM, get_signal_handler_method(mq=message_queue))

    # start the processing and run forever
    message_queue.start_processing_worker_responses()
