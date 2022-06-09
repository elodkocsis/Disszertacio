from typing import Optional, Dict, Union, List

import html2text
import requests
from bs4 import BeautifulSoup
from stem import Signal
from stem.control import Controller

from src.utils.enums import ScrapingResult
from src.utils.general import remove_duplicates
from src.utils.logger import get_logger
from src.data_collection.scraper_utils import get_tor_proxy_dict, get_request_headers, get_tld_with_protocol, \
    url_has_fld, is_onion_link, remove_line_formatters, remove_multiple_spaces, remove_unusable_links, \
    remove_html_tags_from_string

# get logger
logger = get_logger()


def scrape_url(url: str) -> Union[ScrapingResult, Dict]:
    """
    Function which scrapes the content of a page.

    :param url: URL to be scraped.
    :return: A Dictionary containing the relevant data from the page or a `ScrapingResult` object.

    """

    # check if url is an onion link
    if not is_onion_link(link=url):
        logger.error(f"URL '{url}' is not an onion link!")
        return ScrapingResult.INVALID_URL

    # get the response from the page
    if (response := send_request(url=url)) is None:
        return ScrapingResult.SCRAPING_FAILED

    # if the status code isn't within the 200 range, we consider it failed
    if response.status_code >= 300:
        return ScrapingResult.SCRAPING_FAILED

    # parse content
    try:
        parsed_content = BeautifulSoup(response.content, "html.parser")
    except Exception as e:
        logger.error(f"Couldn't parse response for url '{url}': {e}")
        return ScrapingResult.SCRAPING_FAILED

    # extract relevant data from page
    content_dict = extract_relevant_content(url=url, parsed_content=parsed_content)

    return content_dict


def extract_relevant_content(url: str, parsed_content: BeautifulSoup) -> Optional[Dict]:
    """
    Function which extracts the relevant content from a page.

    :param url: The current URL being scraped.
    :param parsed_content: The content from which we want to extract the relevant data.
    :return: Dictionary containing the relevant information we need.

    """

    # setup HTML2Text
    h2t = html2text.HTML2Text()
    h2t.ignore_links = True
    h2t.bypass_tables = True
    h2t.escape_snob = False
    h2t.ignore_images = True

    # extract the links present on the page
    # we extract only the references present in anchor(a) tags
    extracted_urls = [tag.get('href') for tag in parsed_content.findAll('a')]

    # filter unusable links
    extracted_urls = remove_unusable_links(list_of_links=extracted_urls)

    # format same domain links
    extracted_urls = format_urls(url_being_scraped=url, list_of_urls=extracted_urls)

    # remove duplicate urls
    extracted_urls = remove_duplicates(list_of_strings=extracted_urls)

    # extract title
    extracted_title = h2t.handle(str(parsed_content.title).strip())

    # format title
    formatted_title = format_text(string=extracted_title)

    # extract body text
    extracted_body = h2t.handle(str(parsed_content.body).strip())

    # format text data
    extracted_text = format_content_text(title=extracted_title, body=extracted_body)

    # extract the meta tags
    # we are going for name here
    extracted_meta_tags = [{"key": tag.get('name'), "value": tag.get("content")}
                           for tag in parsed_content.findAll('meta')]

    return {
        "url": url,
        "page_title": formatted_title,
        "page_content": extracted_text,
        "links": extracted_urls,
        "meta_tags": extracted_meta_tags
    }


def format_urls(url_being_scraped: str, list_of_urls: List[str]) -> Optional[List[str]]:
    """
    Function which formats the URLs in a list.

    Example:    '/some/pages' -> 'http://domain.top_level/some/pages';
                'http://domain.top_leve/page#section' -> 'http://domain.top_leve/page'

    :param url_being_scraped: The current URL that is being scraped.
    :param list_of_urls: List of URLs to format.
    :return: List of formatted URLs.

    """

    if (current_url := get_tld_with_protocol(url=url_being_scraped)) is None:
        # again, this shouldn't happen, ever!
        return None

    # initialize the new list
    formatted_urls = []
    for url in list_of_urls:
        # remove section part
        parts = url.split("#")
        url = parts[0]

        # NOTE: will keep this commented for now
        # remove parameters
        # parts = url_without_section.split("?")
        # url_without_params = parts[0]

        # if url doesn't contain FLD
        if not url_has_fld(url=url):
            # add FLD to it
            url = current_url + url

        formatted_urls.append(url)

    return formatted_urls


def format_content_text(title: str, body: str) -> str:
    """
    Function which formats the title and body text of a webpage.

    :param title: Title string.
    :param body: Body string.
    :return: Formatted page content in string format.

    """

    # remove line formatters from title
    title = remove_line_formatters(string=title)

    # remove multiple spaces from title
    title = remove_multiple_spaces(string=title)

    # remove line formatters from body text
    body = remove_line_formatters(string=body)

    # remove multiple spaces from body text
    body = remove_multiple_spaces(string=body)

    # remove HTML tags from body text
    body = remove_html_tags_from_string(string=body)

    # combine the title with the body text and return result
    return title + ". " + body


def format_text(string: str) -> str:
    """
    Function which formats a given text.

    :param string: Text to be formatted.
    :return: Formatted text.

    """

    # remove line formatters
    string = remove_line_formatters(string=string)

    # remove multiple spaces
    string = remove_multiple_spaces(string=string)

    return string


def send_request(url: str) -> Optional[requests.Response]:
    """
    Function which sends an HTTP GET request to the specified URL.

    :param url: URL to send an HTTP GET request to.
    :return: Response object.
    """

    try:
        # send a GET request to the URL
        # we are using the TOR proxy in order to access .onion sites
        # the headers we use are the same that the TOR browser sends when sending requests
        result = requests.get(url, proxies=get_tor_proxy_dict(), headers=get_request_headers())
    except Exception as e:
        logger.error(f"GET request failed for url '{url}': {e}")
        return None

    return result


def change_tor_identity() -> bool:
    """
    Function which changes the TOR identity.

    :return: True if the identity was changed, otherwise False.
    """

    try:
        with Controller.from_port(port=9051) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)
    except Exception as e:
        logger.warning(f"Exception when trying to request new TOR identity: {e}")
        return False

    return True
