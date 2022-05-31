from datetime import datetime, timedelta
from typing import List, Optional, Dict

from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from src.db.PageDBModel import Page
from src.utils.general import eprint


def get_page_urls_to_scrape(session: Session, access_day_difference: int) -> Optional[List[str]]:
    """
    Function which returns the list of urls for which scraping has to be done.

    :param session: Session object for database
    :param access_day_difference: How long ago should have been updated to be reconsidered.
    :return: List of URL strings for the pages that need to be scraped.

    """
    current_time = datetime.now()
    date_to_check_against = current_time - timedelta(days=access_day_difference)

    try:
        pages = session.query(Page.url) \
            .filter(
            or_(
                Page.new_url == "true",  # because it is a string in the database...
                and_(
                    Page.date_accessed is not None,
                    Page.date_accessed < date_to_check_against
                )
            )
        ) \
            .order_by(
            Page.date_added.asc()
        ) \
            .all()
    except Exception as e:
        eprint(f"Exception when querying new page urls: {e}")
        return None

    # the elements in the "pages" list are of type Row(tuple), thus we need to extract the first element, the url
    return [row[0] for row in pages] if len(pages) > 0 else []


def update_page(session: Session, existing_page: Page, new_page_data: Dict) -> Optional[Page]:
    """
    Function which updates a record in the database based on the new data it receives.

    :param session: Session object for the database.
    :param existing_page: The existing Page data we want to update.
    :param new_page_data: Dictionary containing the new data for a database record.
    :return: The updated Page object if the update was successful, otherwise None.

    """

    keys = Page.get_list_of_required_columns_for_update()

    # update the relevant fields
    existing_page.page_content = new_page_data[keys[1]]      # key for content
    existing_page.meta_tags = new_page_data[keys[2]]    # key for meta tags
    existing_page.date_accessed = datetime.now()        # update with the current time
    existing_page.new_url = False                       # specify that this is no more a new url

    # try to save and commit
    try:
        session.add(existing_page)
        session.commit()
    except Exception as e:
        eprint(f"Exception while trying to update record in the database {e}")
        return None

    return existing_page


def get_existing_page(session: Session, url: str) -> Optional[Page]:
    """
    Function which returns a Page object from the database if it exists.

    :param session: Session object for the database.
    :param url: The URL of the page.
    :return: Page object if it is present in the database.

    """

    return session.query(Page).filter(Page.url == url).first()


def add_page(session: Session, new_page_data: Dict, is_new_url: bool) -> Optional[Page]:
    """
    Function which inserts a record in the database based on the new data it receives.

    :param session: Session object for the database.
    :param new_page_data: Dictionary containing the new data for a database record.
    :param is_new_url: Flag signifying whether the url is a new one or it has already been scraped, but the row got
                        deleted while the URL was being scraped.
    :return: The updated Page object if the update was successful, otherwise None.

    """

    keys = Page.get_list_of_required_columns_for_update()

    # create new page object
    new_page = Page(url=new_page_data[keys[0]],
                    date_accessed=None if is_new_url else datetime.now(),  # new URLs were not accessed
                    page_content=new_page_data[keys[1]],
                    meta_tags=new_page_data[keys[2]],
                    new_url=is_new_url,
                    date_added=datetime.now())

    # try to save and commit
    try:
        session.add(new_page)
        session.commit()
    except Exception as e:
        eprint(f"Exception while trying to insert record into the database {e}")
        return None

    return new_page
