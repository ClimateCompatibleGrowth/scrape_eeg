# Webscraper to archive EEG papers

Two scripts to:

1. obtain the URLs of all PDFs on the EEG website
2. download all the PDFs to a local folder

Install dependencies

    conda create -n python=3.12 requests requests_cache beautifulsoup4

Now run the scripts::

    python scrape.py

Then::

    python get_pdf.py


You should see a folder `webscraping` containing all the PDF files.
Then there's a log file `app.log` which should contain a bunch of debugging messages.
Then `metadata.csv` which contains all of the details about the files scraped from the site including title, publication date, summary and authors.


## Dependencies

- beautifulsoup4
- requests_cache
