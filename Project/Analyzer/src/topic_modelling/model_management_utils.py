from typing import Optional, List, Dict

from top2vec import Top2Vec

from src.db.database import session_scope
from src.db.db_operations import get_trainable_pages
from src.utils.general import create_folder
from src.utils.logger import get_logger

# getting the logger
logger = get_logger()


def train_model() -> Optional[Top2Vec]:
    """
    Function which trains a Top2Vec model.

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
                        workers=12,  # my pc has 8 cores / 16 threads, so I can afford ramping this up a bit
                        verbose=True)
    except Exception as e:
        logger.error(f"Exception when training Top2Vec model: {e}")
        return None

    return model


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
    # TODO: implement this
    pass


def save_model_to_disc(model: Top2Vec, path: str, file_name: str) -> bool:
    """
    Function which saves a Top2Vec model to disc.

    :param model: Top2Vec model to be saved.
    :param path: Path where the model should be saved.
    :param file_name: File name of the model.
    :return: True if the model could be saved to the disc, otherwise False.

    """

    if not create_folder(relative_path=path):
        return False

    if path[-1] != "/":
        full_path = path + "/" + file_name
    else:
        full_path = path + file_name

    try:
        model.save(file=full_path)
    except Exception as e:
        logger.warning(f"Exception when trying to save model to disc: {e}")
        return False

    return True
