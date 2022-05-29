import sys

from src.mq.MessageQueue import MessageQueue
from src.utils import read_config_file

if __name__ == '__main__':

    # get the parameters for connecting to the message queue
    if(mq_params := read_config_file(config_file="config.conf", section="MQ")) is None:
        sys.exit(3)

    # create connect to the message queue
    message_queue = MessageQueue(param_dict=mq_params, function_to_execute=None)

    # TODO: continue with implementation
