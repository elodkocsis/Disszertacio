from datetime import datetime, timedelta
from typing import List, Optional, Dict

from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from src.db.PageDBModel import Page
from src.utils import eprint, dict_has_necessary_keys


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


def update_page(session: Session, new_page_data: Dict) -> bool:
    """
    Function which updates a record in the database based on the new data it receives.

    :param session: Session object for the database.
    :param new_page_data: Dictionary containing the new data for a database record.
    :return: True if the update operation was successful, otherwise False.

    """

    keys = Page.get_list_of_required_columns_for_update()

    # double check, since we are interested in the same data here too as we were when receiving the response from the MQ
    if not dict_has_necessary_keys(dict_to_check=new_page_data,
                                   needed_keys=keys):
        return False

    url = new_page_data[keys[0]]

    # get the existing record
    if (existing_data := session.query(Page)
            .filter(Page.url == url)
            .first()) is not None:

        # update the relevant fields
        existing_data.page_content = new_page_data[keys[1]]      # key for content
        existing_data.meta_tags = new_page_data[keys[2]]    # key for meta tags
        existing_data.date_accessed = datetime.now()        # update with the current time
        existing_data.new_url = False                       # specify that this is no more a new url

        # try to save and commit
        try:
            session.add(existing_data)
            session.commit()
        except Exception as e:
            eprint(f"Exception while trying to update record in the database {e}")
            return False

        return True

    # I know, I know, but it's much more readable with the else present
    else:
        # if this function is used as it is intended, this should never happen
        eprint(f'URL "{url}" present in the database!')
        return False
