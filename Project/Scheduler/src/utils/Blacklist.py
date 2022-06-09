import sys
import hashlib

from src.utils.general import strip_url
from src.utils.logger import get_logger

# get logger
logger = get_logger()


class Blacklist:
    """
    Class which is responsible for holding the blacklisted URLs and for checking if URLs are present within the
    blacklist.

    """

    def __init__(self):
        """
        Init method.

        IMPORTANT: if this step fails, the application should and is being shut down! The application should not operate
        without a populated blacklist for ethical reason!!!
        """
        try:
            with open("./src/utils/blacklist_2022-06-03.txt", "r") as file:
                file_contents = file.read()
        except Exception as e:
            logger.error(f"Couldn't read blacklist file: {e}")
            # we are exiting with code 0 because of the docker restart policy which should be set for "on-failure"
            # if we are exiting with code 0, that won't register as failure and docker will not restart the container
            # this is needed because without a blacklist the application should not operate!
            sys.exit(0)

        elements = file_contents.split(" ")
        if len(elements) == 0:
            logger.error("The blacklist file contents is empty!")
            sys.exit(0)

        self.blacklist = {element for element in elements}

        logger.info(f"Blacklist loaded. {len(self.blacklist)} elements are within the blacklist.")

    def is_url_blacklisted(self, url: str) -> bool:
        """
        Function which checks whether a URL is present within the blacklist or not.

        :param url: URL to be checked.
        :return: True if the URL is present in the blacklist, otherwise False.

        """

        # hashing the url
        full_md5_hash = hashlib.md5(url.encode("UTF-8")).hexdigest()

        # hash the stripped url
        stripped_md5_has = hashlib.md5(strip_url(url=url).encode("UTF-8")).hexdigest()

        return full_md5_hash in self.blacklist or stripped_md5_has in self.blacklist
