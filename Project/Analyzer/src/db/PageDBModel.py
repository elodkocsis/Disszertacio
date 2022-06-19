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
