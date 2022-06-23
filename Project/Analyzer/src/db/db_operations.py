from typing import List, Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from src.db.PageDBModel import Page
from src.utils.logger import get_logger

# get logger
logger = get_logger()


def get_trainable_pages(session: Session) -> Optional[List[Page]]:
    """
    Function which returns the Pages that can be used for training the Topic Modelling model.

    :param session: Session object for database.
    :return: List of Page objects which can be used for training the Topic Modelling model.

    """

    try:
        pages = session.query(Page) \
            .filter(
            and_(
                Page.new_url == "false",
                Page.page_content is not None,
                func.length(Page.page_content) > 0,
                Page.page_title is not None,
                func.length(Page.page_title) > 0
            )
        ).all()
    except Exception as e:
        logger.warning(f"Exception when querying new page urls: {e}")
        return None

    return pages


def search_pages_by_urls(session: Session, list_of_urls: List[str]) -> Optional[List[Page]]:
    """
    Function which returns the Page objects from the database for the URLs that have been provided.

    :param session: Session object for database.
    :param list_of_urls: List of URLs for which we want the
    :return: List of Page objects.

    """
    try:
        pages = session.query(Page).where(Page.url.in_(list_of_urls)).all()
    except Exception as e:
        logger.warning(f"Exception when querying new page urls: {e}")
        return None

    return pages


'''
############ Helper functions ############
'''


def sort_pages_list_based_on_url_list(ordered_url_list: List[str], page_list: List[Page]) -> List[Page]:
    """
    Function which sorts a list of Page objects based on the order of the URLs in a reference list.

    :param ordered_url_list: Ordered list of URLs based on which the page list should be sorted.
    :param page_list: List of Page objects to be sorted.
    :return: Sorted Page list based on an ordered URL list.

    """
    # create a dictionary and associate the URLs with their index in the list for O(1) lookup
    # ordered_url_dict = {url: index for index, url in enumerate(ordered_url_list)}

    return sorted(page_list, key=lambda x: ordered_url_list.index(x.url))


def map_list_of_pages_to_dict(list_of_pages: List[Page]) -> List[dict]:
    """
    Function which maps a list of Page objects to a list of dictionaries that is going to be used by the front-end.

    :param list_of_pages: List of Page objects.
    :return: List of dictionaries containing the data of the Page objects for the front-end.

    """

    return [{
        "url": page.url,
        "title": page.get_page_title(),
        "description": page.get_page_description()
    } for page in list_of_pages]
