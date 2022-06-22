from typing import Optional, List, Dict

from top2vec import Top2Vec

from src.db.database import session_scope
from src.db.db_operations import get_trainable_pages, search_pages_by_urls, sort_pages_list_based_on_url_list, \
    map_list_of_pages_to_dict
from src.utils.general import create_folder, file_exists
from src.utils.logger import get_logger

# getting the logger
logger = get_logger()


def train_model(number_of_workers: int) -> Optional[Top2Vec]:
    """
    Function which trains a Top2Vec model.

    :param number_of_workers: Number of threads to use for training the model.
    :return: Trained Top2Vec model.

    """

    with session_scope() as session:
        # retrieving trainable pages
        if(pages := get_trainable_pages(session=session)) is None:
            return None

    list_of_ids = []
    list_of_documents = []

    for page in pages:
        list_of_documents.append(page.page_content)
        list_of_ids.append(page.url)

    print(f"Number of documents: {len(list_of_documents)}")

    try:
        model = Top2Vec(documents=list_of_documents,
                        document_ids=list_of_ids,
                        keep_documents=False,  # we are not keeping the documents as we want to save on space
                        speed="learn",
                        workers=number_of_workers,
                        verbose=True)
    except Exception as e:
        logger.error(f"Exception when training Top2Vec model: {e}")
        return None

    return model


def index_top2vec_model(model: Top2Vec):
    """
    Method which runs document indexing on a Top2Vec model.

    :param model: Top2Vec model.

    """
    try:
        model.index_document_vectors()
    except Exception as e:
        logger.error(f"Exception when indexing documents in the Top2Vec model: {e}")


def run_query(top2vec_model: Top2Vec, query: str, number_of_pages: int) -> Optional[List[Dict]]:
    """
    Function which evaluates a query and returns an ordered list of dictionaries containing the relevant pages for
    a query.

    :param top2vec_model: Top2Vec model.
    :param query: Query text.
    :param number_of_pages: Number of pages to be returned.
    :return: Ordered list of dictionaries containing the relevant page data.

    """
    # getting the urls
    _, urls = top2vec_model.query_documents(query=query, num_docs=number_of_pages, use_index=True)

    # get the pages for the urls from the database
    with session_scope() as session:
        if (pages := search_pages_by_urls(session=session, list_of_urls=urls)) is None:
            # this means that we most likely lost connection to the database
            return None

    # sort the pages based on the order of their URLs returned by the model
    sorted_pages_list = sort_pages_list_based_on_url_list(ordered_url_list=list(urls), page_list=pages)

    # map the list of pages to a list of dicts that is expected by the front-end
    return map_list_of_pages_to_dict(list_of_pages=sorted_pages_list)


def save_model_to_disc(model: Top2Vec, path: str, file_name: str) -> bool:
    """
    Function which saves a Top2Vec model to disc.

    :param model: Top2Vec model to be saved.
    :param path: Path where the model should be saved.
    :param file_name: File name of the model.
    :return: True if the model could be saved to the disc, otherwise False.

    """

    # create the folder we want to save the model to if it doesn't exist
    if not create_folder(relative_path=path):
        return False

    # concat the full path to file
    if path[-1] != "/":
        full_path = path + "/" + file_name
    else:
        full_path = path + file_name

    # save the model to file
    try:
        model.save(file=full_path)
    except Exception as e:
        logger.warning(f"Exception when trying to save model to disc: {e}")
        return False

    return True


def load_model_from_disc(path: str, file_name: str) -> Optional[Top2Vec]:
    """
    Function which loads a saved Top2Vec model from disc.

    :param path: Path to the directory the model is located in.
    :param file_name: File name of the model.
    :return: Top2Vec model if it exists on the specified path.

    """

    # concat full path to model
    if path[-1] != "/":
        full_path = path + "/" + file_name
    else:
        full_path = path + file_name

    if not file_exists(path=full_path):
        return None

    # load the model from disc
    try:
        model = Top2Vec.load(full_path)
    except Exception as e:
        logger.error(f"Exception when loading existing model from path '{full_path}': {e}")
        return None

    # perform indexing
    index_top2vec_model(model=model)

    return model
