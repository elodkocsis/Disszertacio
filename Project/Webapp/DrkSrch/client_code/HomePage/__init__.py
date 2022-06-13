from ._anvil_designer import HomePageTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ..ResultPage import ResultPage

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
      if self.get_heartbeat():
        # init result page
        result_page_form = ResultPage(query=query)
        
        # navigate to form
        open_form(result_page_form)
   
  
  # -------------------------------
  # Methods
  # -------------------------------
  
  def get_heartbeat(self) -> bool:
    """Method which checks if the server is online."""
    try:
      return anvil.server.call('heartbeat')
    except Exception as e:
      print(f"Exception while trying to call heartbeat: {e}")
      self.show_error_notification(message="Couldn't connect to server!")
    
    return False
  
  def show_error_notification(self, message: str):
    """Method which shows an error notification."""
    Notification(message,
             title="Server error",
             style="danger").show()


