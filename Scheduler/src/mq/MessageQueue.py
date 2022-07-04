import sys
import time
from typing import Dict, Optional, List, Callable

from pika import BlockingConnection, ConnectionParameters, BasicProperties
from pika.spec import PERSISTENT_DELIVERY_MODE

from src.utils.enums import ProcessingResult
from src.utils.general import dict_has_necessary_keys
from src.utils.logger import get_logger

# get logger
logger = get_logger()


class MessageQueue:
    # keys to look for on the connection parameter dictionary
    __connection_keys = ["mq_host", "mq_port", "mq_worker_queue", "mq_processor_queue"]

    def __init__(self, param_dict: Dict, function_to_execute: Optional[Callable[[str], ProcessingResult]]):
        """
        Initializer method.

        :param param_dict: Dictionary containing the connection parameters for the MQ.
        :param function_to_execute: Function to execute in response for the data received from the MQ.

        """

        # saving param dict
        self.param_dict = param_dict

        # save the function for later
        self.function_to_execute = function_to_execute

        # trying to establish connection to the MQ
        if not self._connect(param_dict=self.param_dict):
            logger.error(f"Couldn't connect to the MQ!")
            sys.exit(1)

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

        logger.info("Start working...")

        was_consuming_before = False

        while True:
            if not self.channel.is_open:
                self._connect(param_dict=self.param_dict)

            try:
                # declare the scheduler queue
                # making it durable for persistence purposes
                self.channel.queue_declare(queue=MessageQueue.__connection_keys[3], durable=True)
            except Exception as e:
                logger.warning(f"Exception when trying to declare queue {MessageQueue.__connection_keys[3]}: {e}")
                # if this is the first time reaching this point, and the queue declaration failed, exit
                if not was_consuming_before:
                    return
                logger.warning("Retrying in 10 seconds...")
                time.sleep(10)
                continue

            # setting basic_qos for fair dispatching
            try:
                self.channel.basic_qos(prefetch_count=1)
            except Exception as e:
                logger.warning(f"Exception when defining basic_qos: {e}")
                # if this is the first time reaching this point, exit
                if not was_consuming_before:
                    return
                logger.warning("Retrying in 10 seconds...")
                time.sleep(10)
                continue

            try:
                # define where and how to consume
                # at this point, the connection keys have been checked
                # Change index for connection keys list if the ordering changes!
                self.channel.basic_consume(queue=MessageQueue.__connection_keys[3],
                                           on_message_callback=self._on_message())
            except Exception as e:
                logger.warning(f"Exception when defining consume method: {e}")
                # if this is the first time reaching this point, exit
                if not was_consuming_before:
                    return
                logger.warning("Retrying in 10 seconds...")
                time.sleep(10)
                continue

            try:
                # start consuming when data is available on the queue
                self.channel.start_consuming()
            except Exception as e:
                # if the MQ goes down, we will try to reconnect to the MQ
                logger.warning(f"Exception when trying to start consuming messages: {e}")
                logger.warning("Retrying in 10 seconds...")
                time.sleep(10)
                was_consuming_before = True

    def _connect(self, param_dict: Dict) -> bool:
        """
        Function which establishes a connection to the MQ.

        :param param_dict: :param param_dict: Dictionary containing the connection parameters for the MQ.
        :return: True if a connection could be established to the MQ, otherwise False.

        """

        # connect to the message queue
        if (connection := MessageQueue._get_connection_from_params(param_dict=param_dict,
                                                                   needed_keys=MessageQueue.__connection_keys)) is None:
            # at this point the errors have been printed to the screen
            return False
        else:
            self.connection = connection

        try:
            self.channel = self.connection.channel()
        except Exception:
            return False

        try:
            # declare the worker queue
            # Change index for connection keys list if the ordering changes!
            # making it durable for persistence purposes
            self.channel.queue_declare(queue=MessageQueue.__connection_keys[2], durable=True)
        except Exception:
            return False

        return True

    def _on_message(self):
        """
        Wrapper for callback because we want to have access to the class members: to the function we want to execute.

        """

        def callback(ch, method, properties, body):  # Taken from documentation, not defining param types.

            # only execute anything if there is anything to execute
            # in the case of the scheduler, this should NOT be executed -> the scheduler should not call
            # the "start_processing_worker_responses" method!!!
            if self.function_to_execute is not None:
                # get the returned data
                data = body.decode()

                logger.info(f'Data received. Processing data...')

                # run the job with the received data
                processing_result = self.function_to_execute(data)

                # check the result of the processing operation
                if processing_result == ProcessingResult.SUCCESS:
                    logger.info("Data processed.")
                    ch.basic_ack(delivery_tag=method.delivery_tag)

                if processing_result == ProcessingResult.PROCESSING_FAILED:
                    logger.warning(f"Couldn't process data:\n{data}\n")
                    # if processing fails it is because the data is faulty
                    # we ack the message as we don't want it to occupy space in the queue
                    ch.basic_ack(delivery_tag=method.delivery_tag)

                if processing_result == ProcessingResult.SAVE_FAILED:
                    # if we cannot save it to the database, is most likely because the database is unreachable
                    # or the url is already present in the db; keep in mind we don't really have any synchronization
                    # between processor apps
                    logger.warning("Couldn't save processed data into the database!")
                    ch.basic_ack(delivery_tag=method.delivery_tag)

        return callback

    def send_message(self, data: str) -> bool:
        """
        Function which sends a message to the MQ.

        :param data: Data string to be sent.
        :return: True if the message was sent, False if and error occurred.

        """

        # convert dict to bytes
        try:
            message = bytes(data.encode('UTF-8'))
        except Exception as e:
            logger.warning(f"Couldn't convert data dict to bytes: {e}")
            return False

        # send the message
        try:
            self.channel.basic_publish(
                exchange='',
                routing_key=MessageQueue.__connection_keys[2],  # send the message to the workers
                body=message,
                properties=BasicProperties(
                    delivery_mode=PERSISTENT_DELIVERY_MODE  # persisting message
                ))
        except Exception as e:
            logger.warning(f"Couldn't send message: {e}")
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
            logger.warning(f"Error creating connection object to MQ: {e}")
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
