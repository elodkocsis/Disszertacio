import re
from typing import Dict, Optional, List

import tld

from src.utils.logger import get_logger

# get logger
logger = get_logger()


def get_tor_proxy_dict() -> Dict:
    """
    Function that returns a dictionary containing the keys and values for the Tor proxy.

    :return: Proxy dictionary.

    """
    return {"http": "127.0.0.1:8118"}


def get_request_headers() -> Dict:
    """
    Function which returns the Header dictionary used for requests.

    :return: Header dictionary.

    """
    return {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "*",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0"  # Tor Browser UA
    }


def is_valid_url(url: str) -> bool:
    """
    Function which checks whether a URL is valid or not.

    :param url: URL to be checked.
    :return: True if the URL is valid, otherwise False.

    """

    # regex taken from Django url validation
    regex = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(regex, url) is not None


def is_onion_link(link: str) -> bool:
    """
    Function which checks if the received link is an onion link.

    :param link: Link to be checked.
    :return: True, if the link is and onion link, otherwise False.

    """

    if (_ := re.match(r'(?:https?://)?(?:www)?(\S*?\.onion)\b', link)) is None:
        return False

    return True


def get_url_protocol(url: str) -> Optional[str]:
    """
    Function which returns the protocol present in a URL.

    :param url: URL to get the protocol from.
    :return: Protocol section of a URL.

    """
    separator = "://"

    # if the separator is not in the url, we don't have a protocol
    if separator not in url:
        return None

    parts = url.split("://")

    return parts[0]


def get_tld_with_protocol(url: str) -> Optional[str]:
    """
    Function which returns the FLD of a URL with the protocol.

    Example: 'https://example.com/some/page' -> 'https://example.com'

    :param url: URL to extract the FLD and protocol from.
    :return: FLD string with protocol.

    """
    # extract the protocol from the current URL
    if (protocol := get_url_protocol(url=url)) is None:
        # this shouldn't happen, ever!
        logger.error(f"URL {url} doesn't have protocol part!")
        return None

    # extract fld
    if (fld := tld.get_fld(url, fail_silently=True)) is None:
        # this shouldn't happen either, ever!
        logger.error(f"URL {url} doesn't have FLD!")
        return None

    # assemble and return tld with protocol
    return protocol + "://" + fld + "/"


def url_has_fld(url: str) -> bool:
    """
    Function which checks whether a URL has FLD or not.

    :param url: URL to be checked.
    :return: True if URL has FLD, otherwise False.

    """

    return tld.get_fld(url, fail_silently=True) is not None


def remove_line_formatters(string: str) -> str:
    """
    Function which removes line formatting characters from string.

    :param string: String to be formatted.
    :return: String without line formatting characters.

    """

    return string.replace('\r', ' ').replace('\n', ' ')


def remove_multiple_spaces(string: str) -> str:
    """
    Function which replaces multiple consecutive occurrences of space characters with only one.

    :param string: String to be formatted.
    :return: Formatted string.

    """

    return re.sub(r' +', ' ', string)


def remove_unusable_links(list_of_links: List[str]) -> List[str]:
    """
    Function which removes links that are unusable from a list.

    :param list_of_links: List to be filtered of unusable links.
    :return: List of filtered links.

    """
    # we are using a set as lookup is O(1)
    invalid_link_values = {"", "#", None}

    return [link for link in list_of_links if link not in invalid_link_values]


def filter_resource_links(list_of_links: List[str]) -> List[str]:
    """
    Function which removes links from a list that are potentially pointing to non-HTML or -txt resources.

    :param list_of_links: List of links to be filtered.
    :return: List of filtered links.

    """
    # we are using a set because of O(1), not that it really matters for 2 elements
    allowed_extensions = {"html", "txt"}

    filtered_links = []

    for link in list_of_links:
        # split link along the TLD
        parts = link.split(".onion")

        # take the part after the TLD
        last_part = parts[-1]

        # remove slashes
        last_part = last_part.replace("/", "")

        # if there is a list of parameters, we will allow it
        if "?" in last_part:
            filtered_links.append(link)
            continue

        # split the last part based on the dots in a potential file extension
        parts = last_part.split(".")

        if len(parts) > 1:
            # get the potential extension
            potential_extension = parts[-1]

            # check if there is at least something
            if len(potential_extension) > 0:
                # we only add the url to the filtered list if the extension is present in the allowed set
                if potential_extension in allowed_extensions:
                    filtered_links.append(link)

            else:
                # if no extension was found, the link is probably good
                filtered_links.append(link)
        else:
            # if there are no dots, the link is good
            filtered_links.append(link)

    return filtered_links


def filter_regular_links(list_of_links: List[str]) -> List[str]:
    """
    Function which filters out all regular links from a list.

    :param list_of_links: List of links to be filtered.
    :return: List of filtered links.

    """

    return [link for link in list_of_links if is_onion_link(link=link)]


def remove_html_tags_from_string(string: str) -> str:
    """
    Function which removes HTML tags from a string.

    :param string: String from where HTML tags should be removed.
    :return: Cleaned string.

    """

    clean_text = re.sub(r"<(?:\"[^\"]*\"['\"]*|'[^']*'['\"]*|[^'\">])+>", '', string)
    return clean_text
