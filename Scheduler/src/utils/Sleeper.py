import time
from datetime import datetime
from typing import Optional

from src.utils.logger import get_logger
from src.utils.signal_handler import should_stop_event

# get logger
logger = get_logger()


class Sleeper:
    """
    Class which makes sure that the wait times between URL scheduling runs are kept consistent, even in the event of
    a container crash and restart before the next scheduling should take place.
    
    """
    # the location we want to save the last
    __datetime_file_location = "sleeper.txt"

    def __call__(self, hours: int):
        """
        Call method; starts sleeping.

        :param hours: Number of hours to sleep.

        """
        # we can't wait negative amount of hours
        if hours < 0:
            hours = 0

        # get the last time we slept
        if (last_datetime := self._read_last_datetime()) is not None:

            # if we have to sleep
            if hours != 0:
                self._sleep(hours=hours, last_datetime=last_datetime)

        # save the current datetime to file
        self._save_current_datetime()

    def _save_current_datetime(self):
        """
        Method which saves the current datetime to a file when the sleep has been completed.

        """

        try:
            with open(self.__datetime_file_location, 'w') as file:
                file.write(datetime.now().strftime("%Y-%b-%d %H:%M:%S"))
        except Exception as e:
            # we are not doing anything if write does not succeed
            logger.warning(f"Exception when writing the current datetime to file: {e}")

    def _read_last_datetime(self) -> Optional[datetime]:
        """
        Function which reads the last datetime saved to a file.

        :return: Datetime object.

        """

        try:
            with open(self.__datetime_file_location, 'r') as file:
                return datetime.strptime(file.read(), "%Y-%b-%d %H:%M:%S")
        except Exception:
            return None

    @staticmethod
    def _sleep(hours: int, last_datetime: datetime):
        """
        Method which will stall the program execution until the set amount of hours have passed from the last
        time the application was sleeping.

        :param hours: Number of hours to wait before resuming program execution.
        :param last_datetime: The last time the program has been stalling.

        """
        # convert hours to seconds
        seconds = hours * 60 * 60

        while True:
            # check for stop event
            if should_stop_event.isSet():
                break

            # calculate if the last time we slept was longer than we have to wait
            diff = datetime.now() - last_datetime

            # get the second difference
            time_to_still_wait_out = seconds - diff.seconds

            if time_to_still_wait_out <= 0:
                break

            time.sleep(0.5)
