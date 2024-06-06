import os
from urllib.parse import urljoin
from bs4 import BeautifulSoup, SoupStrainer
import requests
from csv import DictWriter

from logging import basicConfig, getLogger, INFO

basicConfig(level=INFO, filename="app.log", filemode="w")
logger = getLogger(__name__)

url = "https://www.energyeconomicgrowth.org/www.energyeconomicgrowth.org/content/publications.html"

strainer = SoupStrainer("a", href=True)

# If there is no such folder, the script will create one automatically
folder_location = r'webscraping'
if not os.path.exists(folder_location):
    os.mkdir(folder_location)

metadata = []

with open('publication_links.csv', 'r') as f:
    publication_links = f.readlines()
    for link in sorted(set(publication_links)):
        response = requests.get(urljoin(url, link))
        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.select("a[href$='.pdf']"):

            href = str(link['href'])

            # Name the pdf files using the last portion of each link which are unique in this case
            filename = os.path.join(folder_location, href.split('/')[-1])
            filename = filename.replace("%20", "_")

            authors = soup.find("div", {"class": "views-field-field-author"})
            publication_date = soup.find("div", {"class": "views-field-field-publication-date"})

            metadata.append({
                "filename": filename,
                "url": urljoin(url, href),
                "authors": authors.find("div", {"class": "field-content"}).text if authors else None,
                "publication_date": publication_date.find("time").text if publication_date else None,
                })

            logger.info(f"Downloading {filename}")
            with open(filename, 'wb') as f:
                f.write(requests.get(urljoin(url, href)).content)

with open('metadata.csv', 'w') as f:
    writer = DictWriter(f, fieldnames=["filename", "url", "authors", "publication_date"])
    writer.writeheader()
    writer.writerows(metadata)