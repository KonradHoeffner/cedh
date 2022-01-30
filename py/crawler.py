# Slightly modified copy the crawler.py from https://anonymous.4open.science/r/cEDH-DDB-Crawler-D2E6

import logging
import requests
from bs4 import BeautifulSoup as bs


class Crawler:
    # keep track of visited URLs
    def __init__(self, url=""):
        self.url = url
        self.links = []

    # clean links
    def _filter_link(self, url):
        if url is None:
            return None
        if "jpg" in url:
            return None
        if "discord" in url:
            return None
        if "google" in url:
            return None
        # ignore internal hyperlinks
        if "http" not in url:
            return None
        if "moxfield" in url and "primer" in url:
            return url[: url.index("/primer")]
        else:
            # return None # Moxfield only
            return url.strip()

    def _browse_deck_categories(self):
        html = requests.get(self.url).text
        soup = bs(html, "html.parser")
        # keep track of which section each deck category falls under
        sections = []
        for div in soup.find_all("div", class_="ddb-section"):
            if "COMPETITIVE" in div.text or "BREW" in div.text:
                sections.append(1)
            # decks are meme or outdated
            else:
                sections.append(0)
        # find each deck category
        index = 0
        for li in soup.find_all("li"):
            if li.has_attr("data-title"):
                # filter out the non-competitive lists
                if sections[index] == 0:
                    index += 1
                    continue
                index += 1
                # get all of the deck lists from that category
                for link in li.find_all("a"):
                    link = self._filter_link(link.get("href"))
                    if link:
                        self.links.append(link)

    def run(self):
        try:
            self._browse_deck_categories()
        except Exception:
            logging.exception(f"Failed to crawl: {self.url}")
            raise
