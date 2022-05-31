import json
import sys
from typing import Dict, Optional, List, Callable

from pika import BlockingConnection, ConnectionParameters, BasicProperties
from pika.spec import PERSISTENT_DELIVERY_MODE

from src.utils.general import eprint, dict_has_necessary_keys


class MessageQueue:
    # keys to look for on the connection parameter dictionary
    __connection_keys = ["mq_host", "mq_port", "mq_worker_queue", "mq_processor_queue"]

    def __init__(self, param_dict: Dict, function_to_execute: Optional[Callable[[Dict], Optional[Dict]]]):
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

        # declare the worker queue
        # Change index for connection keys list if the ordering changes!
        # making it durable for persistence purposes
        self.channel.queue_declare(queue=MessageQueue.__connection_keys[2], durable=True)

        # save the function for later
        self.function_to_execute = function_to_execute

    def close_connection(self):
        """
        Method which closes the connection to the MQ.
        DO NOT USE ANY METHOD AFTER CALLING THIS METHOD!!!

        """

        self.connection.close()

    def start_processing_worker_responses(self):
        """
        Method which reads data from the MQ and executes the task received.

        """

        # declare the scheduler queue
        # making it durable for persistence purposes
        self.channel.queue_declare(queue=MessageQueue.__connection_keys[3], durable=True)

        # setting basic_qos for fair dispatching
        self.channel.basic_qos(prefetch_count=1)

        # define where and how to consume
        # at this point, the connection keys have been checked
        # Change index for connection keys list if the ordering changes!
        self.channel.basic_consume(queue=MessageQueue.__connection_keys[3], on_message_callback=self._on_message())

        # start consuming when data is available on the queue
        self.channel.start_consuming()

    def _on_message(self):
        """
        Wrapper for callback because we want to have access to the class members: to the function we want to execute.

        """

        def callback(ch, method, properties, body):  # Taken from documentation, not defining param types.

            # only execute anything if there is anything to execute
            # in the case of the scheduler, this should NOT be executed -> the scheduler should not call
            # the "start_processing_worker_responses" method!!!
            if self.function_to_execute is not None:
                # TODO: check if this needs an UTF-8 decoding
                # get the returned data
                data = body.decode()

                # TODO: maybe switch out the prints for logging?
                print(f' [x] Data received. Processing data...')

                # run the job with the received data
                if (page := self.function_to_execute(data)) is not None:
                    print(f' [x] Data processed. Page "{page}" added to database.')

                    # acknowledge that the task is done if the function doesn't return None.
                    ch.basic_ack(delivery_tag=method.delivery_tag)

        return callback

    def send_message(self, data: Dict) -> bool:
        """
        Function which sends a message to the .

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
                routing_key=MessageQueue.__connection_keys[2],  # send the message to the workers
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

        if not dict_has_necessary_keys(dict_to_check=param_dict, needed_keys=needed_keys):
            return None

        return MessageQueue._get_connection(host=param_dict[needed_keys[0]],
                                            port=param_dict[needed_keys[1]])
