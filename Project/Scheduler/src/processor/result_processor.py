from typing import Dict, Optional

from src.db.PageDBModel import Page
from src.db.database import session_scope
from src.db.db_operations import update_page, get_existing_page, add_page
from src.utils.general import dict_has_necessary_keys, eprint


def process_scraped_result(result_dictionary: Dict) -> Optional[Page]:
    """
    Function which processes a dictionary received from the scrapers through the MQ.
    This function is passed to the MessageQueue object at initialization.

    :param result_dictionary: A dictionary object with data received from the scraper.
    :return: Page object that was successfully saved into the database.

    """

    keys = Page.get_list_of_required_columns_for_update()

    # check if all the necessary keys are present
    if not dict_has_necessary_keys(dict_to_check=result_dictionary,
                                   needed_keys=keys):
        eprint(f"Couldn't process result dict: '{result_dictionary}'! Missing fields!")
        return None

    # getting the url
    url = result_dictionary[keys[0]]

    # getting the links
    links = result_dictionary[keys[3]]

    with session_scope() as session:
        # redundant check, the url should already be present in the database
        if (existing_page := get_existing_page(session=session, url=url)) is not None:
            page = update_page(session=session, existing_page=existing_page, new_page_data=result_dictionary)

        else:
            # but if for some reason it isn't, we will add it, just to be sure
            page = add_page(session=session, new_page_data=result_dictionary, is_new_url=False)

        # go through all the links collected and create and save a new Page object into the database
        for link in links:
            data_for_link = {
                keys[0]: link,  # url
                keys[1]: None,  # page content
                keys[2]: None,  # meta tags
            }

            # adding new entry into the database for the new link
            if (_ := add_page(session=session, new_page_data=data_for_link, is_new_url=True)) is None:
                # the only thing we do here is just printing about the issue
                # if this operation fails, we can fix the code and on the next run we will get the missed links
                eprint(f"Couldn't add Page object to database for new link: '{link}'!")

        return page
