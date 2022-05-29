from typing import List

from sqlalchemy.orm import Session

from src.db.PageDBModel import Page


# TODO: write implementation
def get_new_pages_urls(session: Session) -> List[str]:
    pass


# TODO: write implementation
def get_older_pages_urls(session: Session, access_day_difference: int) -> List[str]:
    pass


# TODO: write implementation
def update_page(session: Session, new_page_data: Page):
    pass
