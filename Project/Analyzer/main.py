from pprint import pprint

from src.db.database import session_scope
from src.db.db_operations import get_trainable_pages, search_pages_by_urls, sort_pages_list_based_on_url_list

if __name__ == '__main__':
    with session_scope() as session:
        pages = get_trainable_pages(session=session)
        pprint(pages)
        print("\n===========================================================\n")

        url_set = {page.url for page in pages}
        url_list = [page.url for page in pages]
        ret_pages = search_pages_by_urls(session=session, list_of_urls=url_set)

        ret_pages = sort_pages_list_based_on_url_list(ordered_url_list=url_list, page_list=ret_pages)

        for item1, item2 in zip(pages, ret_pages):
            if item1.url != item2.url:
                print("Lists are not in the same order!")

        pprint(ret_pages)

