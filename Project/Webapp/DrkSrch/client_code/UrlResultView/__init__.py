from ._anvil_designer import UrlResultViewTemplate
from anvil import *


class UrlResultView(UrlResultViewTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)
