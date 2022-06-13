from ._anvil_designer import SearchCardTemplate
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class SearchCard(SearchCardTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def search_text_box_pressed_enter(self, **event_args):
    """This method is called when the user presses Enter in this text box"""
    
    self.raise_event("search_event", query=self.search_text_box.text)

  def search_button_click(self, **event_args):
    """This method is called when the button is clicked"""
    
    self.raise_event("search_event", query=self.search_text_box.text)


