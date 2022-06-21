import gc
import time
import threading
from typing import Dict, Optional, Union, List

from top2vec import Top2Vec

from src.topic_modelling.Singleton import Singleton
from src.topic_modelling.model_management_utils import train_model, save_model_to_disc, run_query, \
    index_top2vec_model, load_model_from_disc
from src.utils.enums import ModelStatus
from src.utils.logger import get_logger

# getting the logger
logger = get_logger()


class ModelManager(metaclass=Singleton):
    __instance = None
    __MODEL_TRAINING_TIMER_WAIT_TIME = 86400  # seconds -> this is 1 day, 24 hours
    __MODEL_LOCATION = "Top2VecModel"
    __MODEL_FILE_NAME = "model.t2v"

    def __init__(self):
        self.model_training_thread: Optional[threading.Thread] = None
        self.model_training_job_timer: Optional[threading.Timer] = None
        self.model: Optional[Top2Vec] = None
        self.client_lock = threading.Lock()
        self.counter_lock = threading.Lock()
        self.client_counter = 0
        self.model_status = ModelStatus.SETTING_UP

        # try loading an existing model
        self.load_model()

        # starting the trainer thread
        self.start_model_training_thread(manager_instance=self)

    def __del__(self):
        if self.model_training_thread is not None and self.model_training_thread.isAlive():
            # we want to wait for it to finish the training job and save the model to file before
            # killing the thread
            # this might not finish fast enough in docker, and it will probably get killed, losing all progress
            self.model_training_thread.join()

        # since the thread starts a new timer, we delete it after the thread has completed
        self.delete_model_training_timer()

    def get_pages(self, query: str, num_of_pages: int) -> Union[ModelStatus, List[Dict]]:
        """
        Function which returns a list of dict objects for containing the pages for the passed query.

        :param query: The query based on which the page data will be returned.
        :param num_of_pages: Number of results to be returned. If the value is less than 1, the value will be set to 1,
                            if the value is larger than 1000, the value will be set to 1000.
        :return: Ordered list of dictionaries containing the data for the pages.

        """

        logger.info(f"Request for query: {query} and num of pages: {num_of_pages}")

        # check the number of pages to not be less than 1
        if num_of_pages < 1:
            num_of_pages = 1

        # check the number of pages to not be more than 1000
        # this way we can compensate a bit for speed
        if num_of_pages > 1000:
            num_of_pages = 1000

        while True:
            # although it's not necessary to lock a simple read operation, because of the GIL, I really want to
            # make sure that no client request with "Flash" or "Quicksilver" level of speed will get through once the
            # model trainer thread starts messing with the model status and model...
            with self.client_lock:
                model_status = self.model_status

            if model_status == ModelStatus.UPDATING:
                # updating the model takes much less time than setting it up in the first place, so we can afford to
                # wait for it to update
                time.sleep(0.05)
            else:
                break

        if model_status != ModelStatus.READY:
            # this will be ModelStatus.SETTING_UP
            logger.warning("Model manages is still in SETTING_UP mode!")
            return model_status

        with self.counter_lock:
            self.client_counter += 1

        # we are not locking the actual model usages as that will create a bottleneck here, and we defeat the
        # purpose of having a somewhat parallel execution for different client requests
        # besides, addition and subtraction procedures are done much faster than the query procedure itself
        result = run_query(top2vec_model=self.model, query=query, number_of_pages=num_of_pages)

        with self.counter_lock:
            self.client_counter -= 1

        return result

    def set_model(self, new_model: Top2Vec):
        """
        Method which sets a new Top2Vec model and saves it to disc.

        :param new_model: New Top2Vec model to be set and saved to disc.

        """
        # overwrite model in memory
        self.model = new_model

        # try saving the model to disc
        save_model_to_disc(model=new_model, path=self.__MODEL_LOCATION, file_name=self.__MODEL_FILE_NAME)

        # index newly set model
        # IMPORTANT: indexing should ALWAYS be done after the model has been saved to disc. If the model is indexed
        # before saving, Top2Vec will fail to load it at the next restart
        index_top2vec_model(model=self.model)

    def load_model(self):
        """
        Method which loads an already present model from the disc.

        """
        logger.info("Loading existing model...")

        # if no model can be loaded, set the model status to set up
        if (model := load_model_from_disc(path=self.__MODEL_LOCATION, file_name=self.__MODEL_FILE_NAME)) is None:
            self.model_status = ModelStatus.SETTING_UP
            logger.info("No model could be found on the disc!")

        # if we have a model, set it and set the status to ready
        else:
            self.model = model
            self.model_status = ModelStatus.READY
            logger.info("Model loaded from disc.")

    '''
    ######## Static methods #########
    '''

    @staticmethod
    def start_model_training_thread(manager_instance):
        """
        Method which starts the thread responsible for training a new Top2Vec model.

        :param manager_instance: ModelManager instance.

        """
        # we are getting the model status
        with manager_instance.client_lock:
            model_status = manager_instance.model_status

        # if the status is ModelStatus.SETTING_UP, we start the setup thread
        if model_status == ModelStatus.SETTING_UP:
            logger.info("Starting model training thread.")
            manager_instance.model_training_thread = threading.Thread(target=manager_instance.model_trainer_job,
                                                                      args=(manager_instance,))
            # we are not joining the thread because the main thread has much important things to do, like serving
            # client requests
            manager_instance.model_training_thread.start()

        # otherwise, we are using the last model for the next cycle and only update it then
        else:
            logger.info("Starting model training timer.")
            manager_instance.model_training_job_timer = threading.Timer(
                manager_instance.__MODEL_TRAINING_TIMER_WAIT_TIME,
                manager_instance.model_trainer_job,
                args=(manager_instance,)
            )
            manager_instance.model_training_job_timer.start()

    @staticmethod
    def model_trainer_job(manager_instance):
        """
        Method which executes a Top2Vec model training job.

        :param manager_instance: ModelManager instance.

        """
        # we train the new model
        logger.info("Training new model...")

        # if the model has been trained successfully, we move on to switching it out with the existing one
        # otherwise we restart the timers
        # this is enough if there is already a model trained, but can cause issues if this is a "cold start"
        if (new_model := train_model()) is not None:
            logger.info("New model trained.")

            with manager_instance.client_lock:
                manager_instance.model_status = ModelStatus.UPDATING

            logger.info(f"Model status set to '{manager_instance.model_status}'")

            logger.info("Waiting for clients to finish using the model...")

            # we are checking the client counter and wait until all the clients have received a result from
            # the previous model;
            while True:
                # trying to acquire the counter lock
                is_locked = manager_instance.counter_lock.acquire(blocking=False)
                if not is_locked:
                    continue

                # getting the counter and releasing the lock
                counter = manager_instance.client_counter
                manager_instance.counter_lock.release()

                # if there are no more clients using the model, we move on
                if counter == 0:
                    break
                else:
                    # otherwise, we are waiting a bit and rechecking the count
                    time.sleep(0.05)

            logger.info("Setting the new model...")
            manager_instance.set_model(new_model=new_model)
            logger.info("New model set.")

            with manager_instance.client_lock:
                manager_instance.model_status = ModelStatus.READY

            logger.info(f"Model status set to '{manager_instance.model_status}'")

        # delete previous timer
        manager_instance.delete_model_training_timer()

        # we pretty much restart the whole threading cycle
        manager_instance.model_training_job_timer = threading.Timer(manager_instance.__MODEL_TRAINING_TIMER_WAIT_TIME,
                                                                    manager_instance.model_trainer_job,
                                                                    args=(manager_instance,))
        manager_instance.model_training_job_timer.start()

        logger.info(f"Timer set to run training job again after {manager_instance.__MODEL_TRAINING_TIMER_WAIT_TIME} "
                    f"seconds.")

    def delete_model_training_timer(self):
        """
        Method which deletes the model training timer.

        """
        if self.model_training_job_timer is not None:
            self.model_training_job_timer.cancel()
            del self.model_training_job_timer
            gc.collect()
