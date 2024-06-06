import os
from urllib.parse import urljoin
from bs4 import BeautifulSoup, SoupStrainer
import requests_cache
from csv import DictWriter

from logging import basicConfig, getLogger, INFO

basicConfig(level=INFO, filename="app.log", filemode="w")
logger = getLogger(__name__)

url = "https://www.energyeconomicgrowth.org/www.energyeconomicgrowth.org/content/publications.html"

session = requests_cache.CachedSession("cache", expire_after=30)
strainer = SoupStrainer("a", href=True)

# If there is no such folder, the script will create one automatically
folder_location = r'webscraping'
if not os.path.exists(folder_location):
    os.mkdir(folder_location)

metadata = []

with open('publication_links.csv', 'r') as f:
    publication_links = f.readlines()
    for publication in sorted(set(publication_links)):
        response = session.get(urljoin(url, publication, allow_fragments=True))
        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.select("a[href$='.pdf']"):

            href = str(link['href'])

            # Name the pdf files using the last portion of each link which are unique in this case
            filename = os.path.join(folder_location, href.split('/')[-1])
            filename = filename.replace("%20", "_")

            authors = soup.find("div", {"class": "views-field-field-author"})
            publication_date = soup.find("div", {"class": "views-field-field-publication-date"})
            title = soup.find('div', {'class': 'field--name-node-title'})
            abstract = soup.find('div', {'class': 'field--type-text-with-summary'})

            metadata.append({
                "filename": filename,
                "url": urljoin(url, href),
                "authors": authors.find("div", {"class": "field-content"}).text if authors else None,
                "publication_date": publication_date.find("time").text if publication_date else None,
                "parent_url": urljoin(url, publication),
                'title': title.find('h2').text.strip() if title else None,
                'abstract': abstract.find('p').text.strip() if abstract else None
                })

            with open(filename, 'wb') as f:
                response = session.get(urljoin(url, href))
                if response.status_code == 200:
                    logger.info(f"Downloading {filename} from {href} in {publication}.")
                    f.write(response.content)
                else:
                    logger.error(f"Failed to download {filename} from {href} in {publication}.")
                    # Hacky manual munge to get the correct URL
                    response = session.get("https://www.energyeconomicgrowth.org/www.energyeconomicgrowth.org/" + href[5:])
                    if response.status_code == 200:
                        logger.info(f"Downloading {filename} from {href} in {publication}.")
                        f.write(response.content)

with open('metadata.csv', 'w') as f:
    writer = DictWriter(f, fieldnames=["title", "abstract", "filename", "url", "authors", "publication_date", "parent_url"])
    writer.writeheader()
    writer.writerows(metadata)