import json

from src.db.PageDBModel import Page
from src.db.database import session_scope
from src.db.db_operations import update_page, get_existing_page, add_page, get_all_page_urls_is_database
from src.utils.Blacklist import Blacklist
from src.utils.enums import ProcessingResult
from src.utils.general import dict_has_necessary_keys, strip_quotes
from src.utils.logger import get_logger

# get logger
logger = get_logger()

# load the blacklist
blacklist = Blacklist()


def process_scraped_result(received_data: str) -> ProcessingResult:
    """
    Function which processes a dictionary received from the scrapers through the MQ.
    This function is passed to the MessageQueue object at initialization.

    :param received_data: Stringified dict received from the scraper.
    :return: Page object that was successfully saved into the database.

    """

    try:
        result_dictionary = json.loads(received_data)
    except Exception as e:
        logger.warning(f"Couldn't convert received string to JSON: {e}")
        return ProcessingResult.PROCESSING_FAILED

    keys = Page.get_list_of_required_columns_for_update()

    # check if all the necessary keys are present
    if not dict_has_necessary_keys(dict_to_check=result_dictionary,
                                   needed_keys=keys):
        logger.error(f"Couldn't process result dict: '{result_dictionary}'! Missing fields!")
        return ProcessingResult.PROCESSING_FAILED

    # getting the url
    url = result_dictionary[keys[0]]

    # if the page url is blacklisted, don't save it
    if blacklist.is_url_blacklisted(url=url):
        logger.warning(f"URL: {url} is blacklisted! Skipping...")
        # we will consider it a successful processing, but we are not going to save it
        return ProcessingResult.SUCCESS

    # getting the links
    links = result_dictionary[keys[4]]

    with session_scope() as session:
        try:
            # redundant check, the url should already be present in the database
            if (existing_page := get_existing_page(session=session, url=url)) is not None:
                update_page(session=session, existing_page=existing_page, new_page_data=result_dictionary)

            else:
                # but if for some reason it isn't, we will add it, just to be sure
                add_page(session=session, new_page_data=result_dictionary, is_new_url=False)
        except Exception as e:
            logger.error(f"Couldn't save page to database: {e}")
            return ProcessingResult.SAVE_FAILED

        if (existing_page_urls := get_all_page_urls_is_database(session=session)) is None:
            # if we can't query all the existing page URLs, we will say that everything is fine for now
            # this should only happen if the database goes down right after the addition or update from before
            # TODO: maybe check this out in the future?
            return ProcessingResult.SUCCESS

        # go through all the links collected and create and save a new Page object into the database
        for link in links:
            # check if link is in the blacklist
            if blacklist.is_url_blacklisted(url=link):
                logger.warning(f"Link: {link} is blacklisted! Skipping...")
                continue

            data_for_link = {
                keys[0]: strip_quotes(string=link),     # url
                keys[1]: None,                          # page title
                keys[2]: None,                          # page content
                keys[3]: None,                          # meta tags
                "parent_url": url                       # parent url
            }

            # add the new link only if it's not already present in the database
            if link not in existing_page_urls:
                # adding new entry into the database for the new link
                if (_ := add_page(session=session, new_page_data=data_for_link, is_new_url=True)) is None:
                    # the only thing we do here is just printing about the issue
                    # if this operation fails, we can fix the code and on the next run we will get the missed links
                    logger.warning(f"Couldn't add Page object to database for new link: '{link}'!")

        return ProcessingResult.SUCCESS
