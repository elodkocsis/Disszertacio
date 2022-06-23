from ._anvil_designer import ResultPageTemplate
from anvil import *
import anvil.server

from ..Utils import get_heartbeat, show_notification


class ResultPage(ResultPageTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # get the query passed on from the HomePage
        query = properties['query']

        # check if it has anything in it
        if len(query) > 0:
            # load the data
            self.get_search_results(query=query)

    # -------------------------------
    # Callbacks
    # -------------------------------

    def app_logo_mouse_up(self, x, y, button, **event_args):
        """This method is called when a mouse button is released on this component"""

        open_form('HomePage')

    def search_card_search_event(self, query, **event_args):
        """This method is called Event fired when the user clicks the search button or hits enter in the search box."""

        # check if the length of the query is at least 1 char
        if len(query) > 0:
            self.get_search_results(query=query)

    # -------------------------------
    # Methods
    # -------------------------------

    def get_search_results(self, query: str, num: int = 100):
        """
        Method which attempts to retrieve the search results for a query.
    
        :param query: Query string based on which we want to retrieve the search results.
        :param num: Number of results we want to retrieve.
    
        """

        # Load existing articles from the Data Table, and display them in the articles_panel
        if get_heartbeat():
            try:
                result = anvil.server.call('get_pages', query=query, num=num)
            except Exception as e:
                print(f"Exception while trying to retrieve results for query '{query}': {e}")
                show_notification(message="Couldn't retrieve results from the server!")
                return

            if type(result) == str and result == "setting_up":
                show_notification(message="Pages are currently being indexed. Try again later!",
                                  style="warning")
                return

            self.result_panel.items = result
