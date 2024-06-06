import os
from urllib.parse import urljoin
from bs4 import BeautifulSoup, SoupStrainer
import requests_cache

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

with open('publication_links.csv', 'r') as f:
    publication_links = f.readlines()
    for link in publication_links:
        response = session.get(urljoin(url, link))
        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.select("a[href$='.pdf']"):
            #Name the pdf files using the last portion of each link which are unique in this case
            filename = os.path.join(folder_location, link['href'].split('/')[-1])
            logger.info(f"Downloading {filename}")
            with open(filename, 'wb') as f:
                f.write(requests.get(urljoin(url, link['href'])).content)
