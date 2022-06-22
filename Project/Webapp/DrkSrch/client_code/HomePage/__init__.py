from ._anvil_designer import HomePageTemplate
from anvil import *
import anvil.server

from ..ResultPage import ResultPage
from ..Utils import get_heartbeat


class HomePage(HomePageTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

    # -------------------------------
    # Callbacks
    # -------------------------------

    def search_card_search_event(self, query, **event_args):
        """This method is called Event fired when the user clicks the search button or hits enter in the search box."""

        # check if the length of the query is at least 1 char
        if len(query) > 0:

            # check if server is online
            if get_heartbeat():
                # init result page
                result_page_form = ResultPage(query=query)

                # navigate to form
                open_form(result_page_form)
