from urllib.parse import urljoin
from bs4 import BeautifulSoup, SoupStrainer
import requests_cache

from logging import basicConfig, getLogger, INFO

basicConfig(level=INFO, filename="app.log", filemode="w")
logger = getLogger(__name__)

url = "https://www.energyeconomicgrowth.org/www.energyeconomicgrowth.org/content/publications.html"

publication_links = []
unexplored_links = []
explored_links = []


session = requests_cache.CachedSession("cache", expire_after=30)
strainer = SoupStrainer("a", href=True)


def get_publication_links(url):
    logger.info(f"Unexplored links: {unexplored_links}.")
    logger.info(f"Explored links: {explored_links}.")
    response = session.get(url)
    soup = BeautifulSoup(response.text, "html.parser", parse_only=strainer)
    for link in soup.select("a[href$='.html']"):
        link_to_check = str(link['href'])
        if "publication" in link_to_check and "publications.html" not in link_to_check:
            if "/publication/" in link_to_check and link_to_check not in publication_links:
                publication_links.append(link_to_check)
                logger.info(f"Found publication link: {link_to_check}")
            elif link_to_check not in explored_links and link_to_check not in unexplored_links and link_to_check not in url :
                logger.info(f"Found new publication page: {link_to_check}")
                unexplored_links.append(link_to_check)

    return publication_links


with open('publication_links.csv', 'w') as f:
    publications = get_publication_links(url)
    logger.info(f"Found {len(publications)} publications.")
    f.writelines("\n".join(publications))

    if sorted(set(publications)) != sorted(publications):
        raise ValueError("Duplicate publications found.")

    while len(unexplored_links) > 0:
        next_link = unexplored_links.pop(0)
        explored_links.append(next_link)
        publications = get_publication_links(urljoin(url, next_link))
        logger.info(f"Found {len(publications)} publications.")
    f.writelines("\n".join(publications))

if sorted(set(publications)) != sorted(publications):
    print(f"{len(publications) - len(set(publications))} duplicate publications found.")
    raise ValueError("Duplicate publications found.")
