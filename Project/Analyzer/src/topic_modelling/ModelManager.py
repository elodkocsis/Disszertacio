import gc
import time
import threading
from typing import Dict, Optional, Union

from src.utils.enums import ModelStatus
from src.utils.logger import get_logger

# getting the logger
logger = get_logger()


# TODO: remove this
class Model:

    def __init__(self, label, version):
        self.label = label
        self.version = version

    def get_label(self) -> Dict:
        time.sleep(5)
        return {"data": self.label + str(self.version)}

    def __str__(self):
        return f"<Model: label={self.label}; version={self.version}>"


# TODO: add method to load model from disc
class ModelManager(object):
    __instance = None
    # TODO: switch this back to 1 day
    __MODEL_TRAINING_TIMER_WAIT_TIME = 60  # 86400  # seconds -> this is 1 day, 24 hours
    __MODEL_LOCATION_AND_NAME = "./model.t2v"

    def __new__(cls, *args, **kwargs):
        if ModelManager.__instance is None:
            # creating the object
            ModelManager.__instance = object.__new__(cls)

            # initializing the instance
            ModelManager.__instance.__init__()

            # starting the trainer thread
            ModelManager.start_model_training_thread(manager_instance=ModelManager.__instance)

        return ModelManager.__instance

    def __init__(self):
        self.model_training_job_timer: Optional[threading.Timer] = None
        self.model: Optional[Model] = None
        self.client_lock = threading.Lock()
        self.counter_lock = threading.Lock()
        self.client_counter = 0
        # TODO: replace this with the appropriate state, if there is any model present on the disc or not
        self.model_status = ModelStatus.SETTING_UP

    def __del__(self):
        if self.model_training_thread is not None and self.model_training_thread.isAlive():
            # we want to wait for it to finish the training job and save the model to file before
            # killing the thread
            # this might not finish fast enough in docker, and it will probably get killed, losing all progress
            self.model_training_thread.join()

        # since the thread starts a new timer, we delete it after the thread has completed
        self.delete_model_training_timer()

    def get_value(self) -> Union[ModelStatus, Dict]:
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
            return model_status

        with self.counter_lock:
            self.client_counter += 1

        # we are not locking the actual model usages as that will create a bottleneck here, and we defeat the
        # purpose of having a somewhat parallel execution for different client requests
        # besides, addition and subtraction procedures are done much faster than the model usage itself
        result = self.model.get_label()

        with self.counter_lock:
            self.client_counter -= 1

        return result

    def set_model(self, new_model: Model):
        print(f"New model: {new_model}")
        self.model = new_model

    '''
    ######## Static methods #########
    '''

    @staticmethod
    def train_new_model(model_manager_instance) -> Model:
        time.sleep(20)
        if model_manager_instance.model is not None:
            current_version = model_manager_instance.model.version
        else:
            current_version = 0

        return Model(label="MyCustomModel", version=current_version + 1)

    @staticmethod
    def start_model_training_thread(manager_instance):
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
        # we train the new model
        logger.info("Training new model...")
        new_model = ModelManager.train_new_model(model_manager_instance=manager_instance)
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
