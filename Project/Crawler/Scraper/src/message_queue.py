import json
import sys
from typing import Dict, Optional, List, Callable

from pika import BlockingConnection, ConnectionParameters, BasicProperties
from pika.spec import PERSISTENT_DELIVERY_MODE

from src.utils import eprint, is_onion_link


# TODO: I written this class without testing it. Check out if the message sending/acknowledging logic is correct.
class MessageQueue:
    # keys to look for on the connection parameter dictionary
    __connection_keys = ["mq_host", "mq_port", "mq_worker_queue", "mq_processor_queue"]

    def __init__(self, param_dict: Dict, function_to_execute: Callable[[str], Dict]):
        """
        Initializer method.

        :param param_dict: Dictionary containing the connection parameters for the MQ.
        :param function_to_execute: Function to execute in response for the data received from the MQ.

        """

        # connect to the message queue
        # this thing could be done with propagating exceptions, but I don't want to write a try-except in main...
        # TODO: add some retry feature or something if the MQ goes down
        if (connection := MessageQueue._get_connection_from_params(param_dict=param_dict,
                                                                   needed_keys=MessageQueue.__connection_keys)) is None:
            # at this point the errors have been printed to the screen
            sys.exit(1)
        else:
            self.connection = connection

        try:
            self.channel = self.connection.channel()
        except Exception as e:
            eprint(f"Couldn't create channel object: {e}")
            sys.exit(2)

        # declare the scheduler/processor queue
        # Change index for connection keys list if the ordering changes!
        # making it durable for persistence purposes
        self.channel.queue_declare(queue=MessageQueue.__connection_keys[3], durable=True)

        # save the function for later
        self.function_to_execute = function_to_execute

    def __del__(self):
        """
        Destructor method.

        """

        # I'm not really sure if this will ever be called but defined nonetheless.
        self.connection.close()

    def start_working(self):
        """
        Method which reads data from the MQ, executes the task received and sends back the results.

        """

        # declare the worker queue
        # making it durable for persistence purposes
        self.channel.queue_declare(queue=MessageQueue.__connection_keys[2], durable=True)

        # setting basic_qos for fair dispatching
        self.channel.basic_qos(prefetch_count=1)

        # start consuming when data is available on the queue
        # at this point, the connection keys have been checked
        # Change index for connection keys list if the ordering changes!
        self.channel.basic_consume(queue=MessageQueue.__connection_keys[2], on_message_callback=self._on_message())

    def _on_message(self):
        """
        Wrapper for callback because we want to have access to the class members: to the function we want to execute.

        """

        def callback(ch, method, properties, body):  # Taken from documentation, not defining param types.

            # TODO: check if this needs an UTF-8 decoding
            # get the url
            url = body.decode()

            # check if url is a valid onion link
            if not is_onion_link(link=url):
                print(f' [x] URL "{url}" is not a valid onion link!')

                # acknowledge that it has been processed even if it's not a valid link we want to deal with
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            # TODO: maybe switch out the prints for logging?
            print(f' [x] URL to work with: "{url}"...')

            # run the job with the url
            result = self.function_to_execute(url)

            print(" [x] URL {url} processed.")

            # send back the result
            if self._send_message(data=result):

                # acknowledge that the task is done only when the response has been sent back successfully
                ch.basic_ack(delivery_tag=method.delivery_tag)

        return callback

    def _send_message(self, data: Dict) -> bool:
        """
        Function which sends a message to the scheduler/processor.

        :param data: Data dictionary to be sent.
        :return: True if the message was sent, False if and error occurred.

        """

        # convert dict to bytes
        try:
            message = bytes(json.dumps(data, ensure_ascii=False).encode('utf8'))
        except Exception as e:
            eprint(f"Couldn't convert data dict to bytes: {e}")
            return False

        # send the message
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=MessageQueue.__connection_keys[3],  # send the message to the scheduler/processor
                body=message,
                properties=BasicProperties(
                    delivery_mode=PERSISTENT_DELIVERY_MODE
                ))
        except Exception as e:
            eprint(f"Couldn't send message: {e}")
            return False

        return True

    '''
    ######## Static methods #########
    '''

    @staticmethod
    def _get_connection(host: str, port: int) -> Optional[BlockingConnection]:
        """
        Function which creates a BlockingConnection object for the MQ.

        :param host: Host of the MQ.
        :param port: Port of the MQ.
        :return: BlockingConnection for the MQ.

        """
        try:
            return BlockingConnection(ConnectionParameters(host=host, port=port))
        except Exception as e:
            eprint(f"Error creating connection object to MQ: {e}")
            return None

    @staticmethod
    def _get_connection_from_params(param_dict: Dict, needed_keys: List[str]) -> Optional[BlockingConnection]:
        """
        Function which creates a BlockingConnection object for MQ based on the parameters received.

        :param param_dict: Dict of parameters needed to connect to the message queue.
        :return: BlockingConnection object used to communicate with the MQ.

        """

        # set operation to get missing values
        # this will check if all the necessary keys are present, thus we won't have to check again when we define
        # the worker and scheduler/processor queues
        diff = set(needed_keys) - set(param_dict.keys())

        if len(diff) > 0:
            eprint("The following parameters are missing: {}".format(",".join(diff)))
            return None

        return MessageQueue._get_connection(host=param_dict[needed_keys[0]],
                                            port=param_dict[needed_keys[1]])
