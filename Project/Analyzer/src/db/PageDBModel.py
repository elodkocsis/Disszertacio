from sqlalchemy import Column, String, DateTime, Boolean, Text, JSON

from src.db.database import Base


class Page(Base):
    # although in the sql script it is defined the capital P, postgres creates it with lowercase P
    __tablename__ = "pages"

    url = Column(String, primary_key=True, index=True, unique=True)
    date_accessed = Column(DateTime, nullable=True, index=True)
    page_title = Column(Text, nullable=True)
    page_content = Column(Text, nullable=True)
    meta_tags = Column(JSON, nullable=True)
    parent_url = Column(String, nullable=True, index=True)
    new_url = Column(Boolean, nullable=False)
    date_added = Column(DateTime, nullable=True, index=True)

    def __repr__(self):
        return f"<Page: url: {self.url}; date_added: {self.date_added}; " \
               f"is_new: {self.new_url}; date_accessed: {self.date_added}>"

    def get_page_title(self) -> str:
        """
        Function which returns the page title. If the page has no title, the URL will be returned instead.

        :return: Page title or URL.

        """

        title = str(self.page_title)

        return title if self.page_title is not None and len(title) > 0 else self.url

    def get_page_description(self) -> str:
        """
        Function which returns the description of a page.

        :return: Page description.
        """

        # if the meta_tags property is not a list, we return an empty string
        if type(self.meta_tags) != list:
            return ""

        for tag in self.meta_tags:
            if (key := tag.get("key", None)) is not None and key == "description":
                return tag.get("value", "")

        # if we can't find a description tag, return an empty string
        return ""
